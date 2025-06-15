import os
import uuid
import json
import datetime
from pathlib import Path
from typing import Optional

from pydantic import SecretStr
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from src.logger import logger

HISTORY_DIR = Path("data/history")
HISTORY_DIR.mkdir(parents=True, exist_ok=True)


class InsuranceAnalyzer:
    """
    Выполняет анализ условий страхования через OpenAI-совместимый API.
    """

    def __init__(
        self,
        model_name: str = "google/gemini-2.5-flash-pre-05-20",
        temperature: float = 0.1,
        base_url: str = "https://api.vsegpt.ru/v1"
    ):
        api_key_raw = os.getenv("OPENAI_API_KEY")
        if not api_key_raw:
            raise EnvironmentError("Переменная окружения OPENAI_API_KEY не установлена")

        self.api_key: SecretStr = SecretStr(api_key_raw)

        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=self.api_key,
            base_url=base_url,
        )

        logger.info(f"InsuranceAnalyzer инициализирован с моделью: {model_name}")

    def analyze(
        self,
        contract_text: str,
        rules_text: str,
        template_text: str
    ) -> dict:
        """
        Выполняет анализ договора и правил страхования.
        Возвращает словарь с результатами и метаинформацией.
        """
        try:
            prompt = PromptTemplate(
                input_variables=["contract_text", "rules_text"],
                template=template_text
            )
            prompt_text = prompt.format(
                contract_text=contract_text,
                rules_text=rules_text
            )

            logger.info("📤 Отправка запроса в LLM...")
            messages = [HumanMessage(content=prompt_text)]
            response = self.llm.invoke(messages)
            response_text = response.content

            logger.info("✅ Ответ LLM получен")

            result = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.datetime.now().isoformat(),
                "template": template_text,
                "prompt_text": prompt_text,
                "contract_chars": len(contract_text),
                "rules_chars": len(rules_text),
                "prompt_chars": len(prompt_text),
                "response": response_text,
                "tokens": getattr(response, "usage", None)
            }

            output_path = HISTORY_DIR / f"{result['id']}.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            logger.info(f"📁 Результат анализа сохранён: {output_path.name}")

            return result

        except Exception as e:
            logger.error(f"❌ Ошибка в анализе: {e}", exc_info=True)
            raise RuntimeError("Ошибка при анализе договора и правил") from e
