from typing import List
from pathlib import Path
import json
import hashlib
import configparser

def calculate_file_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def list_documents(folder: str, ext: str) -> List[str]:
    return [f.name for f in Path(folder).glob(f"*{ext}")]

def load_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def load_template_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def list_history_files(folder: str) -> List[str]:
    """Возвращает список файлов истории (*.json)"""
    return sorted([f.name for f in Path(folder).glob("*.json")], reverse=True)

def load_history_file(path: Path) -> dict:
    """Загружает JSON-файл истории анализа"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_metadata_map(folder: str) -> dict:
    """
    Возвращает словарь {отображаемое имя: hash} из .meta-файлов.
    """
    folder_path = Path(folder)
    mapping = {}

    for meta_file in folder_path.glob("*.meta"):
        try:
            meta_content = meta_file.read_text(encoding="utf-8")
            lines = meta_content.splitlines()
            meta_dict = {}
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    meta_dict[key.strip()] = value.strip()

            if "filename" in meta_dict:
                display_name = f"{meta_dict['filename']} ({meta_file.stem[:8]})"
                mapping[display_name] = meta_file.stem

        except Exception as e:
            print(f"Ошибка при чтении метаданных {meta_file.name}: {e}")
            continue

    return mapping
