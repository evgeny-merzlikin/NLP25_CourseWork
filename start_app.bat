@echo off
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
set "OPENAI_API_KEY=sk-or-vv-3ee8d6de0312c2dcb3e579f90c58e34fda291a5211b19d2fca6f8f7816448298"
streamlit run app.py