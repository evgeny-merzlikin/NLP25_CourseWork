import datetime
from pathlib import Path

from docling.document_converter import DocumentConverter

from src.logger import logger
from src.utils import calculate_file_hash

RULES_DIR = Path("data/rules")
RULES_DIR.mkdir(parents=True, exist_ok=True)

class RulesLoader:
    """
    Загрузчик и конвертер правил страхования.
    """

    def __init__(self):
        logger.info("Инициализация RulesLoader")
        self.converter = DocumentConverter()

    def load_file(self, uploaded_file) -> dict:
        """
        Загружает файл правил, конвертирует в Markdown, сохраняет и возвращает метаданные.
        """
        try:
            file_content = uploaded_file.read()
            file_name = uploaded_file.name
            file_ext = Path(file_name).suffix.lower()

            logger.info(f"Загрузка файла правил: {file_name}")

            temp_path = RULES_DIR / f"_temp_{file_name}"
            with open(temp_path, "wb") as f:
                f.write(file_content)

            result = self.converter.convert(str(temp_path))
            output_md = result.document.export_to_markdown()
            temp_path.unlink()

            file_hash = calculate_file_hash(output_md)
            date_uploaded = datetime.datetime.now().isoformat()
            char_count = len(output_md)

            metadata = {
                "filename": file_name,
                "hash": file_hash,
                "uploaded": date_uploaded,
                "chars": char_count
            }

            md_path = RULES_DIR / f"{file_hash}.md"
            meta_path = RULES_DIR / f"{file_hash}.meta"

            with open(md_path, "w", encoding="utf-8") as f:
                f.write(output_md)

            with open(meta_path, "w", encoding="utf-8") as f:
                for k, v in metadata.items():
                    f.write(f"{k}: {v}\n")

            logger.info(f"Файл правил сохранен: {md_path.name}")

            return {
                "markdown": output_md,
                "metadata": metadata
            }

        except Exception as e:
            logger.error(f"Ошибка загрузки правил: {e}", exc_info=True)
            raise RuntimeError("Ошибка загрузки и конвертации правил страхования") from e
