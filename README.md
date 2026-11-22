# TruthTrace
TruthTrace compares a social-media claim against one to three passages you supply. Source URLs record provenance. The app evaluates the pasted text and does not retrieve those URLs.

## Quick start on Windows
1. Install Python 3.10 or newer with the Windows Python launcher.
2. Extract the full ZIP, open the TruthTrace_FullStack folder, and double-click **run.bat**. The first run installs dependencies and requires internet.
3. When the terminal says Uvicorn is running, open **http://127.0.0.1:8000**. Keep the terminal open.
4. Select **Example cases**, choose a case, then **View assessment**. All four examples use a fictional notice and prepared answers. They run locally without a Gemini key.
5. To assess your own claim, edit the generated **.env**, set GEMINI_API_KEY to your Google AI Studio key, and restart the launcher. Select **Check a claim**, enter a claim and source passages, then **Verify claim**. Download the report to retain the inputs, quotations and assessment.

## Quick start on macOS or Linux
From the extracted project directory:
```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
cp -n .env.example .env
python -m uvicorn backend.main:app
```
Open http://127.0.0.1:8000. The browser interface and API share one server. The separate Streamlit client is also available.

## Optional Streamlit client
With FastAPI running, activate the same virtual environment in a second terminal, install `frontend/requirements.txt` with pip, then run `python -m streamlit run frontend/app.py`. This client calls the live verification endpoint on port 8000.

## How to interpret results
Each verdict describes how the supplied excerpts relate to the claim. The backend checks that each quoted passage occurs in the cited source. It drops unmatched quotes and converts decisive verdicts with no surviving quote to Unverifiable. Quote matching cannot establish that a source is accurate or that the model interpreted it correctly.

## Testing and configuration
Open http://127.0.0.1:8000/docs for interactive API documentation. To run the included validation tests, install pytest in the virtual environment and run `python -m pytest -q` from the project root.

The default model is configured in .env.example. Live access depends on your Gemini key, model access, internet connection and quota. Use a free-tier eligible model for a zero-budget demo. Keep the local .env private and use public excerpts for live requests. The app stores no claim history. Download individual reports from the browser before closing the page.
