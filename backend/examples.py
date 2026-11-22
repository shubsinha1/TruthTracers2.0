"""Authored teaching cases. These responses never stand in for live model output."""

NOTICE = ("The Alder Quay library will open at 10 am on Saturday. "
          "Only the reading room will open. The lending desk will remain closed.")

def example(title, claim, verdict, quote, reason):
    return {
        "title": title,
        "input": {"claim": claim, "sources": [
            {"source_id": "S1", "name": "Alder Quay library · fictional notice",
             "url": "", "text": NOTICE}]},
        "assessment": {
            "verdict": verdict, "explanation": reason,
            "evidence": [{"source_id": "S1", "quote": quote, "how_it_relates": reason}] if quote else [],
            "confidence": "High" if quote else "Low",
            "confidence_reason": "The notice addresses the claim directly." if quote else "The notice gives no information about fees.",
            "limitations": ["This prepared case uses a fictional library notice."]}}


EXAMPLES = {
    "hours": example("Opening hours", "The library will open at 10 am on Saturday.", "True",
                     "will open at 10 am on Saturday", "The opening time and day match the notice."),
    "lending": example("Lending desk", "The lending desk will open on Saturday.", "False",
                       "The lending desk will remain closed.", "The notice explicitly says the desk will be closed."),
    "services": example("Available services", "The library is reopening on Saturday with all its usual services.", "Misleading",
                        "Only the reading room will open.", "The opening day is correct, but the notice limits which services will operate."),
    "fees": example("Admission fee", "Library admission will cost five credits.", "Unverifiable",
                    "", "The notice covers opening hours and services. It gives no admission price.")
}
