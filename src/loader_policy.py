import datetime
from pathlib import Path

from docling.document_converter import DocumentConverter

from src.logger import logger
from src.utils import calculate_file_hash

POLICY_DIR = Path("data/policies")
POLICY_DIR.mkdir(parents=True, exist_ok=True)

class PolicyLoader:
    """
    Загрузчик и конвертер договора страхования.
    """

    def __init__(self):
        logger.info("Инициализация PolicyLoader")
        self.converter = DocumentConverter()

    def load_file(self, uploaded_file) -> dict:
        """
        Загружает файл, конвертирует в Markdown, сохраняет и возвращает метаданные.
        """
        try:
            # Чтение файла
            file_content = uploaded_file.read()
            file_name = uploaded_file.name
            file_ext = Path(file_name).suffix.lower()

            logger.info(f"Загрузка файла договора: {file_name}")

            # Сохраняем временно
            temp_path = POLICY_DIR / f"_temp_{file_name}"
            with open(temp_path, "wb") as f:
                f.write(file_content)

            # Конвертация в markdown
            result = self.converter.convert(str(temp_path))
            output_md = result.document.export_to_markdown()
            temp_path.unlink()  # удалим временный файл

            # Хэш и метаданные
            file_hash = calculate_file_hash(output_md)
            date_uploaded = datetime.datetime.now().isoformat()
            char_count = len(output_md)

            metadata = {
                "filename": file_name,
                "hash": file_hash,
                "uploaded": date_uploaded,
                "chars": char_count
            }

            # Сохраняем markdown
            md_path = POLICY_DIR / f"{file_hash}.md"
            meta_path = POLICY_DIR / f"{file_hash}.meta"

            with open(md_path, "w", encoding="utf-8") as f:
                f.write(output_md)

            with open(meta_path, "w", encoding="utf-8") as f:
                for k, v in metadata.items():
                    f.write(f"{k}: {v}\n")

            logger.info(f"Файл сохранен: {md_path.name}")

            return {
                "markdown": output_md,
                "metadata": metadata
            }

        except Exception as e:
            logger.error(f"Ошибка загрузки договора: {e}", exc_info=True)
            raise RuntimeError("Ошибка загрузки и конвертации договора") from e
