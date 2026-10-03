from __future__ import annotations

from streamlit import logger

from customer_support_agent.core.settings import Settings
from customer_support_agent.integrations.rag.chroma_kb import KnowledgeBaseService
from loguru import logger

class KnowledgeService:
    def __init__(self, settings: Settings):
        self._settings = settings

    def ingest(self, clear_existing: bool = False) -> dict[str, int]:
        rag_service = KnowledgeBaseService(settings=self._settings)
        logger.info(f"Starting knowledge ingestion with clear_existing={clear_existing}...")
        return rag_service.ingest_directory(
            directory=self._settings.knowledge_base_path,
            clear_existing=clear_existing,
        )