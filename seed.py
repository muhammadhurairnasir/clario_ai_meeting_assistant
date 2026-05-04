import os
import shutil
from werkzeug.security import generate_password_hash
from models.database import (
    init_db, get_connection, insert_user, insert_meeting,
    insert_transcript, insert_summary, insert_tasks, set_meeting_graphs
)
from utils.visualization import (
    build_knowledge_graph, generate_assignee_bar_chart, generate_priority_donut_chart, generate_status_pie_chart
)
from config import DB_PATH, UPLOAD_DIR
import pathlib

# Ensure we use static/graphs so the UI can serve them properly
APP_ROOT = pathlib.Path(__file__).resolve().parent
STATIC_GRAPH_DIR = APP_ROOT / "static" / "graphs"

def seed():
    print("🧹 Cleaning up old data...")
    # Empty tables instead of deleting the DB file to avoid WinError 32 locks
    if os.path.exists(DB_PATH):
        try:
            conn = get_connection(DB_PATH)
            conn.execute("DELETE FROM tasks")
            conn.execute("DELETE FROM summaries")
            conn.execute("DELETE FROM transcripts")
            conn.execute("DELETE FROM meetings")
            conn.execute("DELETE FROM users")
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Warning: Could not clear database tables: {e}")
    
    # Delete generated graphs and uploads
    if STATIC_GRAPH_DIR.exists():
        shutil.rmtree(STATIC_GRAPH_DIR)
    STATIC_GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    print("🛠️  Initializing database schema...")
    init_db(DB_PATH)

    print("🌱 Seeding Demo User...")
    pwd_hash = generate_password_hash("Demo1234!")
    user_id = insert_user("DemoUser", "demo@clario.ai", pwd_hash)

    print("🌱 Seeding Sample Meeting 1: Q3 Planning...")
    m1_id = insert_meeting(user_id, meeting_date="2026-05-02")
    
    transcript_1 = (
        "Alright everyone, let's kick off the Q3 planning session. "
        "We have a lot of critical items to cover. "
        "John, you must finalize the Q3 marketing budget immediately, this is urgent. "
        "Sarah, please review the new landing page designs by this week. "
        "Mike will schedule a follow-up sync with the engineering team soon. "
        "Also, we need to make sure the client presentation is ready. Sarah needs to prepare the slides."
    )
    insert_transcript(m1_id, transcript_1)
    
    summary_1 = (
        "The team discussed Q3 planning and assigned critical marketing and design tasks. "
        "John is responsible for the budget, while Sarah will handle landing pages and presentation slides."
    )
    insert_summary(m1_id, summary_1)
    
    tasks_1 = [
        {
            "id": 1,
            "description": "John, you must finalize the Q3 marketing budget immediately, this is urgent.",
            "assigned_to": "John",
            "due_date": "Not specified",
            "keyword": "must",
            "priority": "High",
            "status": "pending"
        },
        {
            "id": 2,
            "description": "Sarah, please review the new landing page designs by this week.",
            "assigned_to": "Sarah",
            "due_date": "this week",
            "keyword": "please",
            "priority": "Medium",
            "status": "pending"
        },
        {
            "id": 3,
            "description": "Mike will schedule a follow-up sync with the engineering team soon.",
            "assigned_to": "Mike",
            "due_date": "soon",
            "keyword": "will",
            "priority": "Medium",
            "status": "completed"
        },
        {
            "id": 4,
            "description": "Sarah needs to prepare the slides.",
            "assigned_to": "Sarah",
            "due_date": "Not specified",
            "keyword": "needs to",
            "priority": "Low",
            "status": "pending"
        }
    ]
    insert_tasks(m1_id, tasks_1)
    
    print("📊 Generating graphs for Meeting 1...")
    t1_graph = [dict(t, id=i+1) for i, t in enumerate(tasks_1)]
    build_knowledge_graph(t1_graph, str(STATIC_GRAPH_DIR / f"graph_m{m1_id}.png"))
    generate_assignee_bar_chart(t1_graph, str(STATIC_GRAPH_DIR / f"bar_m{m1_id}.png"))
    generate_priority_donut_chart(t1_graph, str(STATIC_GRAPH_DIR / f"donut_m{m1_id}.png"))
    generate_status_pie_chart(t1_graph, str(STATIC_GRAPH_DIR / f"status_m{m1_id}.png"))
    
    set_meeting_graphs(
        m1_id, 
        f"graphs/graph_m{m1_id}.png", 
        f"graphs/bar_m{m1_id}.png", 
        f"graphs/donut_m{m1_id}.png",
        f"graphs/status_m{m1_id}.png"
    )

    print("✅ Database truncated and seeded successfully!")

if __name__ == "__main__":
    seed()
