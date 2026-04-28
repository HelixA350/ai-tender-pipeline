import logging

logger = logging.getLogger(__name__)


class RAGExtractionStage:
    async def execute(self, context, model: str = "openai"):
        from worker.schemas.tender_schema import TenderSchemaSimple
        from api.config import settings

        logger.info(
            f"Starting RAG extraction for content_length: {context.content_length}"
        )

        # 1. Combine content with document boundaries
        combined_parts = []
        for filename, content in context.markdown_contents.items():
            combined_parts.append(
                f"=== DOCUMENT START: {filename} ===\n{content}\n=== DOCUMENT END: {filename} ==="
            )
        full_text = "\n\n".join(combined_parts)

        # 2. Split into chunks
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=128)
        chunks = splitter.split_text(full_text)
        logger.info(f"Split into {len(chunks)} chunks")

        # 3. Embeddings based on model
        if model == "gigachat":
            from langchain_gigachat import GigaChatEmbeddings

            embeddings = GigaChatEmbeddings(
                credentials=settings.gigachat_api_key,
                scope="GIGACHAT_API_CORP",
                verify_ssl_certs=False,
            )
        else:
            from langchain_openai import OpenAIEmbeddings

            embeddings = OpenAIEmbeddings(
                api_key=settings.openai_api_key,
                base_url=f"https://{settings.openai_base_url}/v1",
                model="openai/text-embedding-3-large",
            )

        # 4. Vector store with batch embeddings to avoid 300k token limit

        batch_size = 100  # ~25k tokens per batch (100 chunks * ~256 tokens)
        all_embeddings = []

        logger.info(
            f"Creating embeddings for {len(chunks)} chunks in batches of {batch_size}"
        )

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            batch_embeddings = embeddings.embed_documents(batch)
            all_embeddings.extend(batch_embeddings)
            logger.debug(
                f"Processed batch {i // batch_size + 1}, total embeddings: {len(all_embeddings)}"
            )

        from langchain_community.vectorstores import FAISS
        from langchain_core.documents import Document

        # Build FAISS index manually
        vector_store = FAISS.from_embeddings(
            text_embeddings=list(zip(chunks, all_embeddings)),
            embedding=embeddings
        )
        logger.info(f"FAISS index created with {len(chunks)} vectors")

        # 5. Queries for SemanticSummary fields
        field_queries = {
            "customer": "заказчик отрасль тип организации регион",
            "procurement_method": "способ закупки площадка",
            "supply_scope": "суть поставки что поставляется количество позиций характер номенклатуры производители артикулы единственный производитель",
            "service_scope": "описание работ ШМР ПНР ТО ремонт что делается объект оборудование место выполнения режим работы численность допуски",
            "engineering_scope": "инжиниринговая конструкторская часть разработка реинжиниринг стадии КД опытный образец передача прав",
            "delivery_terms": "условия поставки Incoterms место доставки сроки поставки допустимость досрочной поставки логистическая сложность",
            "financial_profile": "финансовые параметры НМЦ валюта НДС условия оплаты тип аванс срок",
            "penalty_profile": "штрафные условия процент пени просрочка база начисления максимальный порог расторжение",
            "product_requirements": "требования к продукту состояние гарантийный срок точка отсчёта аналоги импортозамещение страна происхождения",
            "participant_requirements": "требования к участнику лицензии СРО опыт ограничения происхождение МСП РФ",
            "timeline_summary": "ключевые даты сроки подача заявок поставка выполнение работ продолжительность",
            "complexity_flags": "усложняющие факторы удалённый регион привязка к бренду короткий срок подачи специальные допуски сжатые сроки поставки опытный образец командировочные схема оплаты",
        }
        queries = list(field_queries.values())

        # 6. Search top-5 relevant chunks per query
        all_relevant = []
        for query in queries:
            docs = vector_store.similarity_search(query, k=5)
            all_relevant.extend([d.page_content for d in docs])

        # 7. Deduplicate
        unique_chunks = list(set(all_relevant))
        rag_content = "\n\n".join(unique_chunks)
        logger.info(f"Prepared {len(unique_chunks)} unique relevant chunks for LLM")

        # 8. LLM with TenderSchemaSimple
        if model == "gigachat":
            from langchain_gigachat import GigaChat

            llm = GigaChat(
                model=settings.gigachat_model,
                credentials=settings.gigachat_api_key,
                temperature=0,
                max_tokens=32000,
                scope="GIGACHAT_API_CORP",
                verify_ssl_certs=False,
            )
        else:
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                model=settings.openai_model,
                api_key=settings.openai_api_key,
                base_url=f"https://{settings.openai_base_url}/v1",
                temperature=0,
                max_tokens=32000,
            )
        structured_llm = llm.with_structured_output(TenderSchemaSimple)

        # 9. Invoke
        system_prompt = """You are an expert at extracting structured data from tender documentation.
Extract all available information into the following JSON schema. Use null for missing fields.
Be thorough and extract as much information as possible."""
        result = structured_llm.invoke(f"{system_prompt}\n\n{rag_content}")
        context.extraction_result = result.model_dump()
        logger.info("RAG extraction completed")
