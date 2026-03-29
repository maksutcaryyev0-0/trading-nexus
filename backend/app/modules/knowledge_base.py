"""
NEXUS RAG Knowledge Base
Upload books/strategies → AI uses them in every analysis
"""
import asyncio
from pathlib import Path
from typing import Optional
from loguru import logger

from app.core.config import settings


class KnowledgeBase:

    def __init__(self):
        self.qdrant_url  = settings.QDRANT_URL
        self.collection  = settings.QDRANT_COLLECTION
        self._client     = None
        self._embedder   = None

    def _get_client(self):
        if not self._client:
            from qdrant_client import QdrantClient
            self._client = QdrantClient(url=self.qdrant_url)
        return self._client

    def _get_embedder(self):
        if not self._embedder:
            from sentence_transformers import SentenceTransformer
            self._embedder = SentenceTransformer("all-MiniLM-L6-v2")
        return self._embedder

    async def init_collection(self):
        """Create Qdrant collection if not exists"""
        try:
            client = self._get_client()
            from qdrant_client.models import Distance, VectorParams
            collections = await asyncio.to_thread(client.get_collections)
            names = [c.name for c in collections.collections]
            if self.collection not in names:
                await asyncio.to_thread(
                    client.create_collection,
                    collection_name=self.collection,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
                )
                logger.info(f"Created Qdrant collection: {self.collection}")
        except Exception as e:
            logger.error(f"Qdrant init error: {e}")

    async def index_document(
        self,
        doc_id: str,
        content: str,
        metadata: dict,
        user_id: str,
    ) -> int:
        """Chunk document and index into vector DB"""
        chunks = self._chunk_text(content, chunk_size=500, overlap=50)
        embedder = self._get_embedder()
        client   = self._get_client()

        from qdrant_client.models import PointStruct

        points = []
        for i, chunk in enumerate(chunks):
            vector = await asyncio.to_thread(embedder.encode, chunk)
            points.append(PointStruct(
                id=f"{doc_id}_{i}",
                vector=vector.tolist(),
                payload={
                    "user_id": user_id,
                    "doc_id":  doc_id,
                    "chunk_id": i,
                    "text": chunk,
                    **metadata,
                },
            ))

        # Upload in batches of 100
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i+batch_size]
            await asyncio.to_thread(
                client.upsert,
                collection_name=self.collection,
                points=batch,
            )

        logger.info(f"Indexed {len(chunks)} chunks for doc {doc_id}")
        return len(chunks)

    async def search(
        self,
        query: str,
        user_id: str,
        limit: int = 5,
        category: Optional[str] = None,
    ) -> list:
        """Semantic search in knowledge base"""
        try:
            embedder = self._get_embedder()
            client   = self._get_client()

            vector = await asyncio.to_thread(embedder.encode, query)

            filter_condition = {"must": [{"key": "user_id", "match": {"value": user_id}}]}
            if category:
                filter_condition["must"].append(
                    {"key": "category", "match": {"value": category}}
                )

            from qdrant_client.models import Filter, FieldCondition, MatchValue
            results = await asyncio.to_thread(
                client.search,
                collection_name=self.collection,
                query_vector=vector.tolist(),
                limit=limit,
                with_payload=True,
            )

            return [
                {
                    "text":     r.payload.get("text", ""),
                    "score":    r.score,
                    "doc_id":   r.payload.get("doc_id"),
                    "filename": r.payload.get("filename"),
                    "category": r.payload.get("category"),
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Knowledge search error: {e}")
            return []

    async def get_context_for_analysis(
        self, symbol: str, regime: str, user_id: str
    ) -> str:
        """Get relevant knowledge for current analysis"""
        queries = [
            f"{symbol} trading strategy",
            f"{regime} market conditions strategy",
            f"institutional analysis {symbol}",
            "entry criteria stop loss position sizing",
        ]

        all_results = []
        for q in queries:
            results = await self.search(q, user_id, limit=3)
            all_results.extend(results)

        # Deduplicate and sort by score
        seen = set()
        unique = []
        for r in sorted(all_results, key=lambda x: x["score"], reverse=True):
            key = r["text"][:100]
            if key not in seen:
                seen.add(key)
                unique.append(r)

        if not unique:
            return ""

        context = "\n\n---\n\n".join([
            f"[From: {r.get('filename', 'Knowledge Base')}]\n{r['text']}"
            for r in unique[:5]
        ])

        return f"\n\n## Relevant Knowledge Base Context:\n{context}"

    async def extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        try:
            import PyPDF2
            text = []
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text.append(page.extract_text() or "")
            return "\n".join(text)
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return ""

    async def extract_docx(self, file_path: str) -> str:
        """Extract text from Word document"""
        try:
            from docx import Document
            doc = Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs if p.text])
        except Exception as e:
            logger.error(f"DOCX extraction error: {e}")
            return ""

    async def process_file(
        self,
        file_path: str,
        doc_id: str,
        user_id: str,
        metadata: dict,
    ) -> int:
        """Auto-detect file type and process"""
        path = Path(file_path)
        ext  = path.suffix.lower()

        if ext == ".pdf":
            content = await self.extract_pdf(file_path)
        elif ext in (".docx", ".doc"):
            content = await self.extract_docx(file_path)
        elif ext in (".txt", ".md"):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        elif ext in (".csv", ".xlsx"):
            content = f"Tabular data file: {path.name}"
        else:
            content = ""

        if not content.strip():
            logger.warning(f"No content extracted from {file_path}")
            return 0

        return await self.index_document(doc_id, content, metadata, user_id)

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> list:
        """Split text into overlapping chunks"""
        words  = text.split()
        chunks = []
        start  = 0
        while start < len(words):
            end   = min(start + chunk_size, len(words))
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            start = end - overlap
        return chunks

    async def delete_document(self, doc_id: str, user_id: str):
        """Remove document from knowledge base"""
        try:
            client = self._get_client()
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            await asyncio.to_thread(
                client.delete,
                collection_name=self.collection,
                points_selector=Filter(
                    must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]
                ),
            )
            logger.info(f"Deleted document {doc_id}")
        except Exception as e:
            logger.error(f"Delete error: {e}")


knowledge_base = KnowledgeBase()
