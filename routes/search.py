from flask import Blueprint, render_template, request, session
from config import DB_PATH
from models.database import get_connection, init_db
from routes.utils import login_required, current_user

search_bp = Blueprint("search", __name__)

@search_bp.route("/search")
@login_required
def search():
    query = request.args.get("q", "").strip()
    user_id = session["user_id"]
    init_db(DB_PATH)
    
    results = []
    if query:
        with get_connection(DB_PATH) as conn:
            # Search meetings (title), transcripts, summaries, and tasks
            rows = conn.execute("""
                SELECT DISTINCT m.id, m.title, m.meeting_date, m.sentiment, m.created_at,
                       s.content as summary
                FROM meetings m
                LEFT JOIN transcripts t ON t.meeting_id = m.id
                LEFT JOIN summaries s ON s.meeting_id = m.id
                LEFT JOIN tasks tk ON tk.meeting_id = m.id
                WHERE m.user_id = ? AND (
                    m.title LIKE ? OR 
                    t.content LIKE ? OR 
                    s.content LIKE ? OR 
                    tk.description LIKE ?
                )
                ORDER BY m.created_at DESC
                LIMIT 50
            """, (user_id, f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%')).fetchall()
            
            for r in rows:
                results.append(dict(r))
                
    return render_template(
        "dashboard/search.html",
        user=current_user(),
        query=query,
        results=results
    )
