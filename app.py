import streamlit as st
import os
import traceback
from pathlib import Path

from src.logger import logger
from src.loader_policy import PolicyLoader
from src.loader_rules import RulesLoader
from src.analyzer import InsuranceAnalyzer
from src.utils import (
    calculate_file_hash,
    list_documents,
    load_text_file,
    load_template_file,
    list_history_files,
    load_history_file,
    load_metadata_map
)

st.set_page_config(page_title="Анализ условий страхования", layout="wide")
st.markdown("# 🛡️ Автоматизированный анализ условий страхования")

mode = st.sidebar.radio(
    "Выберите режим работы:",
    (
        "📘 Загрузка правил страхования",
        "📄 Загрузка договора страхования",
        "🔍 Анализ договора",
        "🕓 История запросов",
    ),
)


if mode == "📘 Загрузка правил страхования":
    st.subheader("Загрузка правил страхования")
    uploaded_file = st.file_uploader("Выберите файл (.doc, .docx, .pdf)", type=["doc", "docx", "pdf"])
    if uploaded_file:
        loader = RulesLoader()
        try:
            result = loader.load_file(uploaded_file)
            st.success("✅ Правила успешно загружены")
            st.markdown("### Метаданные")
            st.json(result["metadata"])
            st.markdown("### Markdown:")
            st.markdown(result["markdown"])
        except Exception as e:
            st.error(f"❌ Ошибка: {str(e)}")


elif mode == "📄 Загрузка договора страхования":
    st.subheader("Загрузка договора страхования")
    uploaded_file = st.file_uploader("Выберите файл (.doc, .docx, .pdf)", type=["doc", "docx", "pdf"])
    if uploaded_file:
        loader = PolicyLoader()
        try:
            result = loader.load_file(uploaded_file)
            st.success("✅ Договор успешно загружен")
            st.markdown("### Метаданные")
            st.json(result["metadata"])
            st.markdown("### Markdown:")
            st.markdown(result["markdown"])
        except Exception as e:
            st.error(f"❌ Ошибка: {str(e)}")


elif mode == "🔍 Анализ договора":
    st.subheader("🔍 Анализ условий страхования")

    # Загружаем словари отображения: отображаемое имя -> GUID
    contract_map = load_metadata_map("data/policies")
    rules_map = load_metadata_map("data/rules")

    selected_contract_display = st.selectbox("Выберите договор страхования", list(contract_map.keys()))
    selected_rules_display = st.selectbox("Выберите правила страхования", list(rules_map.keys()))

    if selected_contract_display and selected_rules_display:
        contract_guid = contract_map[selected_contract_display]
        rules_guid = rules_map[selected_rules_display]

        contract_text = load_text_file(Path("data/policies") / f"{contract_guid}.md")
        rules_text = load_text_file(Path("data/rules") / f"{rules_guid}.md")

        template_paths = list(Path("data/templates").glob("*.txt"))
        selected_template = st.selectbox("Выберите шаблон", [p.name for p in template_paths])

        template_text = load_template_file(Path("data/templates") / selected_template)
        edited_template = st.text_area("Шаблон запроса (редактируемый)", value=template_text, height=300)

        if st.button("Выполнить анализ"):
            try:
                with st.spinner("Анализируем..."):
                    analyzer = InsuranceAnalyzer()
                    result = analyzer.analyze(
                        contract_text=contract_text,
                        rules_text=rules_text,
                        template_text=edited_template
                    )

                st.success("✅ Анализ выполнен")

                st.markdown("### 📋 Ответ модели:")
                st.markdown(result["response"], unsafe_allow_html=True)

                st.markdown("### 📊 Метаданные:")
                st.json({
                    "GUID": result["id"],
                    "Дата": result["timestamp"],
                    "Символов в договоре": result["contract_chars"],
                    "Символов в правилах": result["rules_chars"],
                    "Символов в шаблоне": result["prompt_chars"],
                    "Токены": result.get("tokens"),
                })

                with st.expander("📄 Использованный шаблон"):
                    st.code(result["template"], language="jinja")

                with st.expander("📤 Текст запроса, отправленного в LLM"):
                    st.text_area("Промпт", result["prompt_text"], height=300)

            except Exception as e:
                logger.error(f"Ошибка при анализе: {e}", exc_info=True)
                st.error(f"❌ Ошибка при анализе: {str(e)}")




elif mode == "🕓 История запросов":
    st.subheader("🕓 История запросов")

    history_files = list_history_files("data/history")
    if not history_files:
        st.info("История запросов пока пуста.")
    else:
        selected_file = st.selectbox("Выберите запись из истории", history_files)

        if selected_file:
            try:
                history = load_history_file(Path("data/history") / selected_file)

                st.markdown("### 📋 Ответ модели (отформатированный Markdown):")
                st.markdown(history.get("response", ""), unsafe_allow_html=True)

                st.markdown("### 📊 Метаданные:")
                st.json({
                    "GUID": history.get("id"),
                    "Дата": history.get("timestamp"),
                    "Токены": history.get("tokens"),
                    "Символов в договоре": history.get("contract_chars"),
                    "Символов в правилах": history.get("rules_chars"),
                    "Символов в запросе": history.get("prompt_chars"),
                })

                with st.expander("📄 Использованный шаблон"):
                    st.code(history.get("template", ""), language="jinja")

                if "prompt_text" in history:
                    with st.expander("📤 Текст запроса, отправленного в LLM"):
                        st.text_area("Prompt", history["prompt_text"], height=300)

            except Exception as e:
                st.error(f"❌ Ошибка загрузки истории: {str(e)}")

