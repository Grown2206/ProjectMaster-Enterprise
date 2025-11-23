import streamlit as st

def render_kanban_board(manager, pid, project):
    st.subheader("📋 Kanban Board")
    
    tasks = project.get("tasks", [])
    col_todo, col_prog, col_done = st.columns(3)
    
    with col_todo:
        st.markdown("### 📝 To Do")
        st.markdown("---")
        for t in tasks:
            if t["status"] == "To Do": render_kanban_card(manager, pid, t, ["In Progress"], "To Do")

    with col_prog:
        st.markdown("### 🔨 In Progress")
        st.markdown("---")
        for t in tasks:
            if t["status"] == "In Progress": render_kanban_card(manager, pid, t, ["To Do", "Done"], "In Progress")

    with col_done:
        st.markdown("### ✅ Done")
        st.markdown("---")
        for t in tasks:
            if t["status"] == "Done": render_kanban_card(manager, pid, t, ["In Progress"], "Done")

def render_kanban_card(manager, pid, task, possible_moves, current_status):
    bg_color = "#262730"
    if current_status == "Done": bg_color = "#1e3a2f" 
    if current_status == "In Progress": bg_color = "#3a2f1e"
    
    # Abhängigkeit Visualisierung
    block_icon = ""
    block_msg = ""
    if task.get("blocked_by"):
        block_icon = "🔒 "
        block_msg = f"<div style='color:#ff4b4b; font-size:0.8em; margin-bottom:5px'>Wartet auf: {task['blocked_by']}</div>"

    # Kommentar Indikator
    comm_count = len(task.get("comments", []))
    comm_icon = f"💬 {comm_count}" if comm_count > 0 else "💬 +"

    with st.container():
        st.markdown(f"""
        <div style="background-color: {bg_color}; padding: 10px; border-radius: 5px; margin-bottom: 5px; border: 1px solid #444;">
            <strong>{block_icon}{task['text']}</strong>
            {block_msg}
        </div>
        """, unsafe_allow_html=True)
        
        # Action Buttons
        c1, c2, c3 = st.columns([2, 1, 1])
        
        # Moves
        for move_to in possible_moves:
            label = "➡" if move_to == "Done" or (current_status=="To Do" and move_to=="In Progress") else "⬅"
            if c1.button(f"{label}", key=f"mv_{task['id']}_{move_to}", help=f"Move to {move_to}"):
                manager.update_task_status(pid, task['id'], move_to)
                st.rerun()

        # Delete
        if c3.button("🗑", key=f"del_kan_{task['id']}"):
            manager.delete_task_by_id(pid, task['id'])
            st.rerun()
            
    # Detail Expander für Kommentare
    with st.expander(comm_icon):
        for c in task.get("comments", []):
            # Support both 'date' and 'timestamp' fields for backward compatibility
            comment_date = c.get('date') or c.get('timestamp', 'N/A')
            st.markdown(f"<small>**{comment_date}**: {c['text']}</small>", unsafe_allow_html=True)

        new_comment = st.text_input("Kommentar...", key=f"nc_{task['id']}")
        if st.button("Senden", key=f"send_c_{task['id']}"):
            if new_comment:
                manager.add_task_comment(pid, task['id'], new_comment)
                st.rerun()