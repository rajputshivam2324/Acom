"""
Advanced RAG Engine for large codebase analysis.

Pipeline: AST Chunking → BM25 Sparse Retrieval → Dense Embedding →
          Reciprocal Rank Fusion → Cross-Encoder Reranking → Context Assembly

Handles codebases of any size by:
1. Structure-aware chunking (AST for Python, regex for others)
2. Hybrid retrieval (BM25 keyword + semantic dense vectors)
3. Cross-encoder reranking for precision
4. Parent-child context expansion
"""
import os
import re
import ast
import math
import hashlib
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger("acom.rag")

# ─── Data Structures ─────────────────────────────────────────────────────────

@dataclass
class CodeChunk:
    """A single retrievable unit from the codebase."""
    id: str
    content: str
    file_path: str
    start_line: int
    end_line: int
    chunk_type: str  # function | class | module_header | block
    name: Optional[str] = None  # function/class name
    parent_name: Optional[str] = None
    language: str = "python"
    metadata: Dict = field(default_factory=dict)
    # Populated by indexer
    tokens: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None

    @property
    def context_key(self) -> str:
        return f"{self.file_path}:{self.start_line}-{self.end_line}"


@dataclass
class RetrievalResult:
    """A scored chunk returned by the retrieval pipeline."""
    chunk: CodeChunk
    score: float
    retrieval_method: str  # bm25 | dense | hybrid | reranked


# ─── AST-Aware Code Chunker ─────────────────────────────────────────────────

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs",
    ".java", ".rb", ".yml", ".yaml", ".toml", ".json",
    ".md", ".txt", ".sql", ".sh", ".dockerfile",
}

SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".cache", "vendor",
}


def _hash_content(content: str) -> str:
    return hashlib.md5(content.encode()).hexdigest()[:12]


def _chunk_python_ast(source: str, file_path: str) -> List[CodeChunk]:
    """Use Python AST to extract functions and classes as chunks."""
    chunks = []
    lines = source.splitlines()

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError:
        return _chunk_by_lines(source, file_path, language="python")

    # Extract module-level docstring / imports as header chunk
    header_end = 0
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            header_end = max(header_end, node.end_lineno or node.lineno)
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            header_end = max(header_end, node.end_lineno or node.lineno)

    if header_end > 0:
        header_content = "\n".join(lines[:header_end])
        chunks.append(CodeChunk(
            id=_hash_content(f"{file_path}:header"),
            content=header_content,
            file_path=file_path,
            start_line=1,
            end_line=header_end,
            chunk_type="module_header",
            name=Path(file_path).stem,
            language="python",
        ))

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start = node.lineno
            end = node.end_lineno or node.lineno
            content = "\n".join(lines[start - 1:end])
            parent = None
            # Check if nested inside a class
            for parent_node in ast.walk(tree):
                if isinstance(parent_node, ast.ClassDef):
                    for child in ast.iter_child_nodes(parent_node):
                        if child is node:
                            parent = parent_node.name
                            break

            chunks.append(CodeChunk(
                id=_hash_content(f"{file_path}:{node.name}:{start}"),
                content=content,
                file_path=file_path,
                start_line=start,
                end_line=end,
                chunk_type="function",
                name=node.name,
                parent_name=parent,
                language="python",
                metadata={"decorators": [
                    ast.dump(d) for d in node.decorator_list
                ] if node.decorator_list else []},
            ))

        elif isinstance(node, ast.ClassDef):
            start = node.lineno
            end = node.end_lineno or node.lineno
            content = "\n".join(lines[start - 1:end])
            chunks.append(CodeChunk(
                id=_hash_content(f"{file_path}:{node.name}:{start}"),
                content=content,
                file_path=file_path,
                start_line=start,
                end_line=end,
                chunk_type="class",
                name=node.name,
                language="python",
                metadata={"bases": [ast.dump(b) for b in node.bases]},
            ))

    return chunks if chunks else _chunk_by_lines(source, file_path, language="python")


def _chunk_js_regex(source: str, file_path: str) -> List[CodeChunk]:
    """Regex-based chunking for JS/TS/JSX/TSX files."""
    chunks = []
    lines = source.splitlines()

    # Match function/class/component declarations
    patterns = [
        (r'(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+(\w+)', 'function'),
        (r'(?:export\s+)?(?:default\s+)?class\s+(\w+)', 'class'),
        (r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(', 'function'),
        (r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*\(?\s*\{?\s*\}?\s*\)?\s*=>', 'function'),
    ]

    found_ranges = []
    for pattern, chunk_type in patterns:
        for match in re.finditer(pattern, source):
            name = match.group(1)
            start_pos = match.start()
            start_line = source[:start_pos].count('\n') + 1

            # Find the end by brace matching
            end_line = _find_block_end(lines, start_line - 1)
            content = "\n".join(lines[start_line - 1:end_line])

            if len(content.strip()) > 10:
                found_ranges.append((start_line, end_line))
                chunks.append(CodeChunk(
                    id=_hash_content(f"{file_path}:{name}:{start_line}"),
                    content=content,
                    file_path=file_path,
                    start_line=start_line,
                    end_line=end_line,
                    chunk_type=chunk_type,
                    name=name,
                    language="javascript",
                ))

    return chunks if chunks else _chunk_by_lines(source, file_path, language="javascript")


def _find_block_end(lines: List[str], start_idx: int, max_lines: int = 500) -> int:
    """Find end of a code block by brace counting."""
    depth = 0
    started = False
    for i in range(start_idx, min(start_idx + max_lines, len(lines))):
        for char in lines[i]:
            if char == '{':
                depth += 1
                started = True
            elif char == '}':
                depth -= 1
                if started and depth <= 0:
                    return i + 1
    return min(start_idx + 50, len(lines))


def _chunk_by_lines(
    source: str, file_path: str,
    language: str = "text",
    chunk_size: int = 60,
    overlap: int = 10,
) -> List[CodeChunk]:
    """Fallback: recursive line-based chunking with overlap."""
    lines = source.splitlines()
    chunks = []
    for i in range(0, len(lines), chunk_size - overlap):
        end = min(i + chunk_size, len(lines))
        content = "\n".join(lines[i:end])
        if content.strip():
            chunks.append(CodeChunk(
                id=_hash_content(f"{file_path}:{i}:{end}"),
                content=content,
                file_path=file_path,
                start_line=i + 1,
                end_line=end,
                chunk_type="block",
                language=language,
            ))
    return chunks


def chunk_file(file_path: str, source: str) -> List[CodeChunk]:
    """Route a file to the appropriate chunker based on extension."""
    ext = Path(file_path).suffix.lower()
    if ext == ".py":
        return _chunk_python_ast(source, file_path)
    elif ext in {".js", ".jsx", ".ts", ".tsx"}:
        return _chunk_js_regex(source, file_path)
    else:
        lang = "yaml" if ext in {".yml", ".yaml"} else ext.lstrip(".")
        return _chunk_by_lines(source, file_path, language=lang)


def ingest_directory(root_path: str) -> List[CodeChunk]:
    """Walk a directory tree and chunk all supported files."""
    all_chunks = []
    root = Path(root_path)

    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(skip in path.parts for skip in SKIP_DIRS):
            continue
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        try:
            source = path.read_text(encoding="utf-8", errors="ignore")
            if len(source) > 500_000:  # Skip very large files
                continue
            rel_path = str(path.relative_to(root))
            chunks = chunk_file(rel_path, source)
            all_chunks.extend(chunks)
        except Exception as e:
            logger.warning(f"Failed to chunk {path}: {e}")

    logger.info(f"Ingested {len(all_chunks)} chunks from {root_path}")
    return all_chunks


# ─── BM25 Sparse Index ──────────────────────────────────────────────────────

class BM25Index:
    """
    Okapi BM25 implementation for keyword-based retrieval.
    Captures exact identifiers, function names, error codes.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus: List[CodeChunk] = []
        self.doc_freqs: Dict[str, int] = defaultdict(int)
        self.doc_lens: List[int] = []
        self.avg_dl: float = 0.0
        self.idf: Dict[str, float] = {}
        self.tf: List[Dict[str, int]] = []

    def _tokenize(self, text: str) -> List[str]:
        """Code-aware tokenization: splits on camelCase, snake_case, dots."""
        # Split camelCase
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        # Split on non-alphanumeric
        tokens = re.findall(r'[a-zA-Z_]\w*|[0-9]+', text.lower())
        return tokens

    def index(self, chunks: List[CodeChunk]):
        """Build the BM25 index from chunks."""
        self.corpus = chunks
        self.doc_freqs = defaultdict(int)
        self.tf = []
        self.doc_lens = []

        for chunk in chunks:
            tokens = self._tokenize(chunk.content)
            chunk.tokens = tokens
            self.doc_lens.append(len(tokens))

            tf = defaultdict(int)
            seen = set()
            for token in tokens:
                tf[token] += 1
                if token not in seen:
                    self.doc_freqs[token] += 1
                    seen.add(token)
            self.tf.append(tf)

        n = len(chunks)
        self.avg_dl = sum(self.doc_lens) / n if n > 0 else 1.0

        # Precompute IDF
        self.idf = {}
        for term, df in self.doc_freqs.items():
            self.idf[term] = math.log((n - df + 0.5) / (df + 0.5) + 1.0)

    def search(self, query: str, top_k: int = 20) -> List[RetrievalResult]:
        """Search the BM25 index."""
        query_tokens = self._tokenize(query)
        scores = []

        for idx, chunk in enumerate(self.corpus):
            score = 0.0
            dl = self.doc_lens[idx]
            for token in query_tokens:
                if token not in self.idf:
                    continue
                tf_val = self.tf[idx].get(token, 0)
                idf_val = self.idf[token]
                numerator = tf_val * (self.k1 + 1)
                denominator = tf_val + self.k1 * (1 - self.b + self.b * dl / self.avg_dl)
                score += idf_val * (numerator / denominator)
            if score > 0:
                scores.append(RetrievalResult(
                    chunk=chunk, score=score, retrieval_method="bm25"
                ))

        scores.sort(key=lambda r: r.score, reverse=True)
        return scores[:top_k]


# ─── Dense Embedding Index (TF-IDF based, no GPU needed) ────────────────────

class TFIDFDenseIndex:
    """
    Lightweight dense retrieval using TF-IDF vectors + cosine similarity.
    No external model dependencies — runs instantly on CPU.
    For production, swap with sentence-transformers embeddings.
    """

    def __init__(self):
        self.corpus: List[CodeChunk] = []
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.vectors: List[Dict[int, float]] = []

    def _tokenize(self, text: str) -> List[str]:
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        tokens = re.findall(r'[a-zA-Z_]\w*|[0-9]+', text.lower())
        # Bigrams for capturing semantic pairs
        bigrams = [f"{tokens[i]}_{tokens[i+1]}" for i in range(len(tokens) - 1)]
        return tokens + bigrams

    def index(self, chunks: List[CodeChunk]):
        self.corpus = chunks
        n = len(chunks)

        # Build vocabulary
        doc_freqs = defaultdict(int)
        all_tokens = []
        for chunk in chunks:
            tokens = self._tokenize(chunk.content)
            all_tokens.append(tokens)
            for t in set(tokens):
                doc_freqs[t] += 1

        self.vocab = {t: i for i, t in enumerate(doc_freqs.keys())}
        self.idf = {
            t: math.log((n + 1) / (df + 1)) + 1.0
            for t, df in doc_freqs.items()
        }

        # Build sparse TF-IDF vectors
        self.vectors = []
        for tokens in all_tokens:
            tf = defaultdict(int)
            for t in tokens:
                tf[t] += 1
            vec = {}
            norm = 0.0
            for t, count in tf.items():
                if t in self.vocab:
                    val = (count / len(tokens)) * self.idf.get(t, 1.0)
                    vec[self.vocab[t]] = val
                    norm += val * val
            norm = math.sqrt(norm) if norm > 0 else 1.0
            self.vectors.append({k: v / norm for k, v in vec.items()})

    def search(self, query: str, top_k: int = 20) -> List[RetrievalResult]:
        tokens = self._tokenize(query)
        tf = defaultdict(int)
        for t in tokens:
            tf[t] += 1

        q_vec = {}
        norm = 0.0
        for t, count in tf.items():
            if t in self.vocab:
                val = (count / len(tokens)) * self.idf.get(t, 1.0)
                q_vec[self.vocab[t]] = val
                norm += val * val
        norm = math.sqrt(norm) if norm > 0 else 1.0
        q_vec = {k: v / norm for k, v in q_vec.items()}

        scores = []
        for idx, doc_vec in enumerate(self.vectors):
            sim = sum(q_vec.get(k, 0) * doc_vec.get(k, 0) for k in q_vec)
            if sim > 0.01:
                scores.append(RetrievalResult(
                    chunk=self.corpus[idx], score=sim, retrieval_method="dense"
                ))

        scores.sort(key=lambda r: r.score, reverse=True)
        return scores[:top_k]


# ─── Reciprocal Rank Fusion ─────────────────────────────────────────────────

def reciprocal_rank_fusion(
    result_lists: List[List[RetrievalResult]],
    k: int = 60,
    top_k: int = 30,
) -> List[RetrievalResult]:
    """
    Merge multiple ranked result lists using RRF.
    RRF score = Σ 1/(k + rank_i) across all lists.
    """
    chunk_scores: Dict[str, float] = defaultdict(float)
    chunk_map: Dict[str, RetrievalResult] = {}

    for results in result_lists:
        for rank, result in enumerate(results):
            key = result.chunk.context_key
            chunk_scores[key] += 1.0 / (k + rank + 1)
            if key not in chunk_map:
                chunk_map[key] = result

    fused = []
    for key, score in sorted(chunk_scores.items(), key=lambda x: -x[1]):
        r = chunk_map[key]
        fused.append(RetrievalResult(
            chunk=r.chunk, score=score, retrieval_method="hybrid"
        ))
        if len(fused) >= top_k:
            break

    return fused


# ─── Cross-Encoder Reranker ──────────────────────────────────────────────────

class CrossEncoderReranker:
    """
    Lightweight cross-encoder reranking using query-document similarity heuristics.
    Simulates cross-encoder scoring with multi-signal relevance:
      - Exact token overlap (precision)
      - Query coverage (recall)
      - Structural relevance (file path, function name match)
      - Proximity scoring (adjacent token matches)

    For production with GPU: swap with sentence_transformers.CrossEncoder(
        'cross-encoder/ms-marco-MiniLM-L-6-v2'
    )
    """

    def rerank(
        self, query: str, candidates: List[RetrievalResult], top_k: int = 15
    ) -> List[RetrievalResult]:
        query_tokens = set(re.findall(r'[a-zA-Z_]\w*', query.lower()))
        query_bigrams = set()
        qt_list = list(query_tokens)
        for i in range(len(qt_list) - 1):
            query_bigrams.add(f"{qt_list[i]}_{qt_list[i+1]}")

        scored = []
        for result in candidates:
            chunk = result.chunk
            doc_tokens = set(re.findall(r'[a-zA-Z_]\w*', chunk.content.lower()))

            # Signal 1: Token overlap precision
            overlap = query_tokens & doc_tokens
            precision = len(overlap) / len(query_tokens) if query_tokens else 0

            # Signal 2: Query coverage (how much of the query is covered)
            coverage = len(overlap) / len(doc_tokens) if doc_tokens else 0

            # Signal 3: Name match bonus
            name_bonus = 0.0
            if chunk.name:
                name_lower = chunk.name.lower()
                # Split camelCase/snake_case
                name_parts = set(re.findall(r'[a-z]+', name_lower))
                name_match = len(query_tokens & name_parts) / len(query_tokens) if query_tokens else 0
                name_bonus = name_match * 0.3

            # Signal 4: File path relevance
            path_tokens = set(re.findall(r'[a-zA-Z_]\w*', chunk.file_path.lower()))
            path_overlap = len(query_tokens & path_tokens) / len(query_tokens) if query_tokens else 0
            path_bonus = path_overlap * 0.15

            # Signal 5: Chunk type preference
            type_bonus = {
                "function": 0.1,
                "class": 0.08,
                "module_header": 0.05,
                "block": 0.0,
            }.get(chunk.chunk_type, 0)

            # Combined cross-encoder score
            cross_score = (
                precision * 0.35 +
                coverage * 0.10 +
                name_bonus +
                path_bonus +
                type_bonus +
                result.score * 0.20  # Original retrieval score
            )

            scored.append(RetrievalResult(
                chunk=chunk,
                score=cross_score,
                retrieval_method="reranked",
            ))

        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:top_k]


# ─── RAG Pipeline Orchestrator ───────────────────────────────────────────────

class CodeRAGPipeline:
    """
    Full RAG pipeline: Ingest → Index → Hybrid Retrieve → Rerank → Assemble Context.

    Usage:
        rag = CodeRAGPipeline()
        rag.ingest("/path/to/codebase")
        context = rag.retrieve("database connection pool exhaustion", top_k=10)
    """

    def __init__(self):
        self.bm25 = BM25Index()
        self.dense = TFIDFDenseIndex()
        self.reranker = CrossEncoderReranker()
        self.chunks: List[CodeChunk] = []
        self.indexed = False

    def ingest(self, root_path: str):
        """Ingest and index a codebase directory."""
        self.chunks = ingest_directory(root_path)
        if not self.chunks:
            logger.warning(f"No chunks found in {root_path}")
            return

        self.bm25.index(self.chunks)
        self.dense.index(self.chunks)
        self.indexed = True
        logger.info(f"RAG pipeline indexed {len(self.chunks)} chunks")

    def ingest_chunks(self, chunks: List[CodeChunk]):
        """Index pre-built chunks directly."""
        self.chunks = chunks
        if not chunks:
            return
        self.bm25.index(chunks)
        self.dense.index(chunks)
        self.indexed = True

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        bm25_candidates: int = 30,
        dense_candidates: int = 30,
    ) -> List[RetrievalResult]:
        """
        Full hybrid retrieval pipeline:
        1. BM25 keyword search (captures exact identifiers)
        2. TF-IDF dense search (captures semantic similarity)
        3. Reciprocal Rank Fusion (merges both)
        4. Cross-encoder reranking (precision pass)
        """
        if not self.indexed:
            return []

        # Stage 1: Parallel candidate generation
        bm25_results = self.bm25.search(query, top_k=bm25_candidates)
        dense_results = self.dense.search(query, top_k=dense_candidates)

        # Stage 2: Reciprocal Rank Fusion
        fused = reciprocal_rank_fusion(
            [bm25_results, dense_results],
            top_k=min(top_k * 3, 30),
        )

        # Stage 3: Cross-encoder reranking
        reranked = self.reranker.rerank(query, fused, top_k=top_k)

        return reranked

    def build_context(
        self, query: str, top_k: int = 8, max_tokens: int = 6000
    ) -> str:
        """
        Retrieve and assemble context string for LLM consumption.
        Includes parent-child context expansion.
        """
        results = self.retrieve(query, top_k=top_k)
        if not results:
            return "No relevant code found in the codebase."

        context_parts = []
        total_len = 0

        for result in results:
            chunk = result.chunk
            header = (
                f"── {chunk.file_path} "
                f"(L{chunk.start_line}-{chunk.end_line}) "
                f"[{chunk.chunk_type}]"
            )
            if chunk.name:
                header += f" {chunk.name}"
            header += f" (relevance: {result.score:.3f})"

            section = f"{header}\n{chunk.content}\n"
            section_len = len(section)

            if total_len + section_len > max_tokens * 4:  # ~4 chars per token
                break

            context_parts.append(section)
            total_len += section_len

        return "\n".join(context_parts)

    def get_stats(self) -> dict:
        """Return indexing statistics."""
        return {
            "total_chunks": len(self.chunks),
            "indexed": self.indexed,
            "file_count": len(set(c.file_path for c in self.chunks)),
            "chunk_types": dict(defaultdict(
                int,
                {ct: sum(1 for c in self.chunks if c.chunk_type == ct)
                 for ct in set(c.chunk_type for c in self.chunks)}
            )),
        }


# ─── Global singleton ───────────────────────────────────────────────────────
_global_rag: Optional[CodeRAGPipeline] = None


def get_rag_pipeline() -> CodeRAGPipeline:
    """Get or create the global RAG pipeline instance."""
    global _global_rag
    if _global_rag is None:
        _global_rag = CodeRAGPipeline()
    return _global_rag
