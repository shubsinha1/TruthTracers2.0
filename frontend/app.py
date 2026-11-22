"""TruthTrace Streamlit UI. Run: streamlit run frontend/app.py"""
import json
import streamlit as st
from api_client import health, verify_claim

st.set_page_config(page_title="TruthTrace | Fact Check", page_icon="🔎", layout="wide")

st.markdown("""
<style>
.stApp {background: #f6f8fb;}
.block-container {max-width: 1000px; padding-top: 2rem;}
.header {background: linear-gradient(110deg, #102e50, #11527f);color: white;padding: 1.8rem 2rem;border-radius: 17px;margin-bottom: 1rem;}
.header h1 {color:white; margin:0; font-size: 2.1rem;}
.header p {color:#d5e9f7;margin:.35rem 0 0 0;}
div[data-testid="stMetric"] {background:white; padding:1rem; border-radius:12px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header"><h1>🔎 TruthTrace</h1><p>Source-grounded fact-checking assistant · TruthTracers · PE-B25-30</p></div>', unsafe_allow_html=True)
st.caption("Enter a claim and paste source passages. The app does not automatically browse or authenticate sources.")

with st.sidebar:
    st.header("System status")
    try:
        status = health()
        if status.get("status") == "ok":
            st.success("Backend connected")
        if status.get("api_key_configured"):
            st.success("Gemini API key configured in backend")
        else:
            st.warning("Gemini API key not configured yet")
    except Exception:
        st.error("Backend offline. Start FastAPI in Terminal 1.")
    st.divider()
    st.write("**Model**: Configured in backend `.env`")
    st.caption("The API key never appears in the frontend or the API request payload.")
    st.caption("Gemini free-tier requests may be used by Google to improve its products. Use public data only.")

st.subheader("Step 1 · Claim")
claim = st.text_area("Claim to verify", placeholder="Example: Hot water cures COVID-19.", height=105)

st.subheader("Step 2 · Sources")
st.caption("Enter at least one passage and, if available, its source title and URL. Up to 3 excerpts.")
sources = []
for n in range(1, 4):
    with st.expander(f"Source S{n}", expanded=n == 1):
        name = st.text_input("Source name", key=f"name{n}", placeholder="WHO / PIB / reputable fact-checking outlet")
        url = st.text_input("URL (optional)", key=f"url{n}", placeholder="https://...")
        passage = st.text_area("Exact source excerpt", key=f"passage{n}", height=135)
        if passage.strip():
            sources.append({"source_id": f"S{n}", "name": name.strip() or f"Source S{n}", "url": url.strip(), "text": passage.strip()})

clicked = st.button("Verify Claim", type="primary", use_container_width=True)
if clicked:
    if len(claim.strip()) < 5:
        st.error("Please enter a claim of at least 5 characters.")
    elif not sources:
        st.error("Please paste at least one source passage.")
    else:
        try:
            with st.spinner("Evaluating the evidence..."):
                st.session_state["result"] = verify_claim({"claim": claim.strip(), "sources": sources})
        except Exception as exc:
            st.session_state.pop("result", None)
            st.error(str(exc))

if "result" in st.session_state:
    result = st.session_state["result"]
    st.divider()
    st.subheader("Step 3 · Assessment")
    verdict = result.get("verdict", "Unverifiable")
    icon = {"True": "✅", "False": "❌", "Misleading": "⚠️", "Unverifiable": "❓"}.get(verdict, "❓")
    left, right = st.columns(2)
    left.metric("Verdict", f"{icon} {verdict}")
    right.metric("Confidence (qualitative)", result.get("confidence", "Unknown"))
    st.markdown("#### Explanation")
    st.write(result.get("explanation", "Not available"))
    st.markdown("#### Evidence (exact quote verified by backend)")
    if not result.get("evidence"):
        st.info("No verified evidence quotations returned.")
    else:
        for evidence in result["evidence"]:
            st.markdown(f"**{evidence['source_id']}**")
            st.info(evidence["quote"])
            st.write(evidence["how_it_relates"])
    st.markdown("#### Confidence rationale")
    st.write(result.get("confidence_reason", ""))
    if result.get("limitations"):
        st.markdown("#### Limitations")
        for limitation in result["limitations"]:
            st.write(f"• {limitation}")
    st.caption(f"Model: {result.get('model_used', 'unknown')} · Exact quote check: {result.get('evidence_checked', False)}")
    st.download_button("Download JSON result", json.dumps(result, indent=2, ensure_ascii=False), file_name="truthtrace_result.json", mime="application/json")

st.divider()
st.caption("Academic prototype. Source quotation matching does not prove authenticity, relevance or truth. Confidence is not a calibrated probability.")
