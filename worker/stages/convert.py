import logging
from pathlib import Path
import requests
from markitdown import MarkItDown
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ConvertStage:
    """Convert files to Markdown using markitdown"""

    async def execute(self, context):
        logger.info(f"Converting {len(context.extracted_files)} files to Markdown")

        md = MarkItDown()

        for file_path in context.extracted_files:
            path = Path(file_path)
            ext = path.suffix.lower()

            try:
                if ext == ".url":
                    content = self._convert_url(path)
                elif ext in (".png", ".jpg", ".jpeg"):
                    content = self._convert_image(path)
                else:
                    result = md.convert(str(path))
                    content = result.text_content or ""

                context.markdown_contents[path.name] = content
                logger.debug(f"Converted: {path.name}")

            except Exception as e:
                logger.warning(f"Failed to convert {path.name}: {e}")
                context.failed_files.append(path.name)

        logger.info(f"Converted {len(context.markdown_contents)} files")

        # Calculate content length (approximate token count)
        all_md_text = "\n\n".join(context.markdown_contents.values())
        context.content_length = len(all_md_text) // 4
        logger.info(f"Calculated content_length: {context.content_length} tokens")

    def _convert_url(self, path: Path) -> str:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            for line in content.split("\n"):
                if line.strip().startswith("URL="):
                    url = line.strip()[4:].strip()

                    response = requests.get(url, timeout=30, allow_redirects=True)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.text, "html.parser")
                    title = soup.title.string if soup.title else ""
                    body = soup.get_text(separator="\n", strip=True)

                    return f"# {title}\n\n## URL\n\n{response.url}\n\n## Content\n\n{body[:10000]}"
        except Exception as e:
            logger.warning(f"URL conversion failed: {e}")

        return ""

    def _convert_image(self, path: Path) -> str:
        return "[Image conversion requires OpenAI]"
