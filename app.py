
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = "lessons.db"

PHASES = ["Bid", "Solutioning", "Planning", "Execution", "Closure"]
CATEGORIES = ["Technical", "Non-Technical"]
IMPACTS = ["Cost", "Schedule", "Quality", "Scope", "Risk", "Other"]
STATUSES = ["Draft", "Submitted", "Approved", "Rejected"]

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS lessons ("
        "lesson_id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "project_id TEXT, "
        "project_name TEXT, "
        "customer_name TEXT, "
        "project_phase TEXT, "
        "category TEXT, "
        "lesson_title TEXT, "
        "description TEXT, "
        "recommendations TEXT, "
        "impact TEXT, "
        "tags TEXT, "
        "contributor TEXT, "
        "contribution_date TEXT, "
        "status TEXT"
        ")"
    )
    con.commit()
    con.close()

def insert_lesson(data):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "INSERT INTO lessons ("
        "project_id, project_name, customer_name, project_phase, category, "
        "lesson_title, description, recommendations, impact, tags, "
        "contributor, contribution_date, status"
        ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            data["project_id"],
            data["project_name"],
            data["customer_name"],
            data["project_phase"],
            data["category"],
            data["lesson_title"],
            data["description"],
            data["recommendations"],
            data["impact"],
            data["tags"],
            data["contributor"],
            data["contribution_date"],
            data["status"],
        ),
    )
    con.commit()
    con.close()

def update_status(lesson_id, new_status):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("UPDATE lessons SET status = ? WHERE lesson_id = ?", (new_status, lesson_id))
    con.commit()
    con.close()

def load_lessons(filters=None, search=""):
    con = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM lessons WHERE 1=1"
    params = []

    if filters:
        if filters.get("categories"):
            query += " AND category IN ({})".format(",".join(["?"] * len(filters["categories"])))
            params.extend(filters["categories"])
        if filters.get("phases"):
            query += " AND project_phase IN ({})".format(",".join(["?"] * len(filters["phases"])))
            params.extend(filters["phases"])
        if filters.get("status"):
            query += " AND status IN ({})".format(",".join(["?"] * len(filters["status"])))
            params.extend(filters["status"])
    if search:
        like = f"%{search}%"
        query += " AND (lesson_title LIKE ? OR description LIKE ? OR recommendations LIKE ? OR project_name LIKE ? OR customer_name LIKE ?)"
        params.extend([like, like, like, like, like])

    query += " ORDER BY datetime(contribution_date) DESC, lesson_id DESC"
    df = pd.read_sql_query(query, con, params=params)
    con.close()
    return df

st.set_page_config(page_title="Lessons Learned", page_icon="🧠", layout="wide")
st.title("🧠 Lessons Learned (Demo)")

init_db()

tab_submit, tab_browse, tab_admin = st.tabs(["Submit a Lesson", "Browse & Filter", "Admin"])

with tab_submit:
    st.subheader("Add a new lesson")
    with st.form("submit_lesson_form", clear_on_submit=True):
        cols1 = st.columns(3)
        project_id = cols1[0].text_input("Project ID")
        project_name = cols1[1].text_input("Project Name")
        customer_name = cols1[2].text_input("Customer Name")

        cols2 = st.columns(3)
        project_phase = cols2[0].selectbox("Project Phase", PHASES, index=2)
        category = cols2[1].selectbox("Category", CATEGORIES, index=0)
        impact = cols2[2].selectbox("Impact (optional)", [""] + IMPACTS, index=0)

        lesson_title = st.text_input("Lesson Title")
        description = st.text_area("Description", height=150, placeholder="Context → What happened → Root cause → What we'll do next time")
        recommendations = st.text_area("Recommendations", height=120, placeholder="Concrete actions to prevent recurrence")
        tags = st.text_input("Tags (comma-separated)")
        cols3 = st.columns(3)
        contributor = cols3[0].text_input("Contributor", value="")
        status = cols3[1].selectbox("Status", STATUSES, index=0)
        contribution_date = cols3[2].text_input("Contribution Date", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        submitted = st.form_submit_button("Submit Lesson")
        if submitted:
            if not lesson_title or not description:
                st.error("Please provide at least a Lesson Title and Description.")
            else:
                data = {
                    "project_id": project_id.strip(),
                    "project_name": project_name.strip(),
                    "customer_name": customer_name.strip(),
                    "project_phase": project_phase,
                    "category": category,
                    "lesson_title": lesson_title.strip(),
                    "description": description.strip(),
                    "recommendations": recommendations.strip(),
                    "impact": impact if impact else "",
                    "tags": tags.strip(),
                    "contributor": contributor.strip() if contributor else "",
                    "contribution_date": contribution_date,
                    "status": status,
                }
                insert_lesson(data)
                st.success("Lesson saved! 🎉")

with tab_browse:
    st.subheader("Search & Filter")
    c1, c2, c3, c4 = st.columns([2,2,2,3])
    sel_categories = c1.multiselect("Category", CATEGORIES, default=[])
    sel_phases = c2.multiselect("Phase", PHASES, default=[])
    sel_status = c3.multiselect("Status", STATUSES, default=[])
    search = c4.text_input("Keyword search", placeholder="Title, description, recommendations, project, customer")

    df = load_lessons(filters={"categories": sel_categories, "phases": sel_phases, "status": sel_status}, search=search)
    st.caption(f"{len(df)} result(s)")
    st.dataframe(df, use_container_width=True, hide_index=True)

    if not df.empty:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "lessons_export.csv", "text/csv")

with tab_admin:
    st.subheader("Moderate Status")
    df_all = load_lessons()
    if df_all.empty:
        st.info("No lessons yet.")
    else:
        # Build options as (id, label) tuples
        options = [(int(row.lesson_id), f"#{int(row.lesson_id)} — {str(row.lesson_title)[:60]}") for _, row in df_all.iterrows()]
        selected = st.selectbox("Pick a lesson to update", options=options, format_func=lambda x: x[1])
        selected_id = selected[0] if isinstance(selected, tuple) else None

        new_status = st.selectbox("New Status", STATUSES)
        if st.button("Update Status"):
            if selected_id:
                update_status(selected_id, new_status)
                st.success(f"Updated lesson #{selected_id} to {new_status}. Go to Browse to see changes.")

st.markdown("---")
st.caption("Demo app • SQLite backend • Streamlit UI. For production, wire this UI to SharePoint/Dataverse via Power Apps.")
