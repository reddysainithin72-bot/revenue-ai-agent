# AI Revenue Root-Cause Investigation Agent

Full portfolio project: SQLite + Pandas + NEAT + LangGraph + Groq + Streamlit + Plotly.

## Setup
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python database/seed.py
python neat_engine/trainer.py
python test_phase2.py
pytest -q
python -m streamlit run app.py
```

Copy `.env.example` to `.env` and add `GROQ_API_KEY` for LLM-generated reports. Without it, the app uses a deterministic report fallback.

## Flow
User goal -> metrics profiler -> NEAT strategy -> safe SQL evidence -> evidence evaluator -> iterative LangGraph loop -> Groq report -> Streamlit dashboard.

NEAT prioritizes investigation hypotheses; it does not generate arbitrary SQL. The evidence engine reports supported associations and does not automatically establish causality.
