import logging
import json

logger = logging.getLogger(__name__)


class ExtractLLMStage:
    """Extract structured data using LLM with Pydantic schema"""

    async def execute(self, context, model: str = "openai"):
        from api.config import settings
        from worker.schemas.tender_schema import TenderSchema, TenderSchemaSimple

        logger.info(f"Starting LLM extraction with model: {model}")

        if model == "gigachat":
            from langchain_gigachat import GigaChat

            llm = GigaChat(
                model=settings.gigachat_model,
                credentials=settings.gigachat_api_key,
                temperature=0,
                max_tokens=32000,
                scope="GIGACHAT_API_CORP",
                verify_ssl_certs=False,
                timeout=600,
            )
            structured_llm = llm.with_structured_output(TenderSchemaSimple)
        elif model == "openai":
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                model=settings.openai_model,
                api_key=settings.openai_api_key,
                base_url=f"https://{settings.openai_base_url}/v1",
                temperature=0,
                max_tokens=32000,
            )
            structured_llm = llm.with_structured_output(TenderSchema)

        combined_content = self._prepare_content(context.markdown_contents)

        system_prompt = """You are an expert at extracting structured data from tender documentation.
Extract all available information into the following JSON schema. Use null for missing fields.
Be thorough and extract as much information as possible."""

        try:
            result = structured_llm.invoke(f"{system_prompt}\n\n{combined_content}")

            result_dict = result.model_dump()

            context.extraction_result = result_dict
            logger.info("LLM extraction completed")

        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            raise ValueError(f"LLM extraction failed: {e}")

    def _prepare_content(self, md_contents: dict) -> str:
        parts = ["# Извлеченные данные\n"]
        for filename, content in md_contents.items():
            parts.append(f"### {filename}\n\n{content[:50000]}\n")
        return "\n".join(parts)
