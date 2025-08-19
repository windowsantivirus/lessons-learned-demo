
# Lessons Learned – Streamlit Demo

This is a **working demo** of the Lessons Learned application you described. It supports:
- Submitting lessons with **phase** (Bid, Solutioning, Planning, Execution, Closure) and **category** (Technical/Non-Technical)
- Browsing with filters and keyword search
- Basic status moderation (Draft/Submitted/Approved/Rejected)
- SQLite database persistence (`lessons.db`)

## How to run

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL shown in the terminal (usually http://localhost:8501).

## Notes

- This is an **MVP**. In your enterprise setup, you can:
  - Keep SharePoint as the system of record (Power Apps UI), or
  - Use Dataverse for richer security/relationships.
- You can import/export CSV from the Browse tab to seed content.
