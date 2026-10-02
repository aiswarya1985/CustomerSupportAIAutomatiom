from customer_support_agent.core.settings import get_settings
from customer_support_agent.integrations.rag.chroma_kb import KnowledgeBaseService
import traceback

settings = get_settings()

print("=" * 50)
print("Settings check:")
print("  GOOGLE_API_KEY present:", bool(settings.GOOGLE_API_KEY))
print("  GOOGLE_API_KEY prefix:", (settings.GOOGLE_API_KEY or "")[:8])
print("  effective embedding model:", settings.effective_google_embedding_model)
print("  knowledge_base_path:", settings.knowledge_base_path)
print("=" * 50)

try:
    service = KnowledgeBaseService(settings=settings)
    print("KnowledgeBaseService created OK")
    result = service.ingest_directory(
        directory=settings.knowledge_base_path,
        clear_existing=False,
    )
    print("INGEST RESULT:", result)
except Exception:
    print("FULL TRACEBACK:")
    traceback.print_exc()