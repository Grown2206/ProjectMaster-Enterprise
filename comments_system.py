"""
Comments & Mentions System
Collaboration through comments, replies, and @mentions
"""

import streamlit as st
from datetime import datetime
import uuid
import re
from typing import Dict, List, Tuple


class CommentsSystem:
    """Manage comments and mentions"""

    @staticmethod
    def initialize_session_state():
        """Initialize comments in session state"""
        if 'comments' not in st.session_state:
            st.session_state.comments = []

        if 'comment_notifications' not in st.session_state:
            st.session_state.comment_notifications = []

    @staticmethod
    def add_comment(target_type: str, target_id: str, author: str,
                   text: str, parent_id: str = None) -> str:
        """Add new comment"""
        comment = {
            'id': str(uuid.uuid4()),
            'target_type': target_type,  # 'project', 'task', 'experiment'
            'target_id': target_id,
            'author': author,
            'text': text,
            'parent_id': parent_id,  # For replies
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'edited_at': None,
            'likes': [],
            'mentions': CommentsSystem.extract_mentions(text)
        }

        st.session_state.comments.append(comment)

        # Create notifications for mentioned users
        CommentsSystem.create_mention_notifications(comment)

        return comment['id']

    @staticmethod
    def extract_mentions(text: str) -> List[str]:
        """Extract @mentions from text"""
        # Find all @username patterns
        mentions = re.findall(r'@(\w+)', text)
        return list(set(mentions))  # Remove duplicates

    @staticmethod
    def create_mention_notifications(comment: Dict):
        """Create notifications for mentioned users"""
        for username in comment['mentions']:
            notification = {
                'id': str(uuid.uuid4()),
                'user': username,
                'type': 'mention',
                'comment_id': comment['id'],
                'message': f"{comment['author']} hat dich erwähnt",
                'read': False,
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.comment_notifications.append(notification)

    @staticmethod
    def get_comments_for_target(target_type: str, target_id: str) -> List[Dict]:
        """Get all comments for a specific target"""
        return [
            c for c in st.session_state.comments
            if c['target_type'] == target_type and c['target_id'] == target_id and not c.get('parent_id')
        ]

    @staticmethod
    def get_replies(parent_id: str) -> List[Dict]:
        """Get all replies to a comment"""
        return [
            c for c in st.session_state.comments
            if c.get('parent_id') == parent_id
        ]

    @staticmethod
    def get_comment(comment_id: str) -> Dict:
        """Get comment by ID"""
        return next((c for c in st.session_state.comments if c['id'] == comment_id), None)

    @staticmethod
    def update_comment(comment_id: str, new_text: str):
        """Update comment text"""
        for comment in st.session_state.comments:
            if comment['id'] == comment_id:
                comment['text'] = new_text
                comment['edited_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                comment['mentions'] = CommentsSystem.extract_mentions(new_text)
                CommentsSystem.create_mention_notifications(comment)
                break

    @staticmethod
    def delete_comment(comment_id: str):
        """Delete comment and all its replies"""
        # Delete replies first
        replies = CommentsSystem.get_replies(comment_id)
        for reply in replies:
            CommentsSystem.delete_comment(reply['id'])

        # Delete comment
        st.session_state.comments = [c for c in st.session_state.comments if c['id'] != comment_id]

    @staticmethod
    def toggle_like(comment_id: str, user: str):
        """Toggle like for comment"""
        for comment in st.session_state.comments:
            if comment['id'] == comment_id:
                if user in comment['likes']:
                    comment['likes'].remove(user)
                else:
                    comment['likes'].append(user)
                break

    @staticmethod
    def get_unread_mentions(user: str) -> int:
        """Get count of unread mentions for user"""
        return len([
            n for n in st.session_state.comment_notifications
            if n['user'] == user and not n['read']
        ])


def render_comments_section(target_type: str, target_id: str, current_user: str):
    """Render comments section for a target (project, task, etc.)"""
    CommentsSystem.initialize_session_state()

    st.markdown("### 💬 Kommentare & Diskussionen")

    # Get comments
    comments = CommentsSystem.get_comments_for_target(target_type, target_id)

    # Comment input
    with st.form(f"new_comment_{target_type}_{target_id}"):
        st.markdown("**Neuer Kommentar**")

        comment_text = st.text_area(
            "Kommentar",
            placeholder="Schreibe einen Kommentar... (Nutze @username für Mentions)",
            label_visibility="collapsed"
        )

        col1, col2 = st.columns([3, 1])

        with col1:
            st.caption("💡 Tipp: Nutze @username um Team-Mitglieder zu erwähnen")

        submitted = col2.form_submit_button("💬 Posten", type="primary", use_container_width=True)

        if submitted and comment_text.strip():
            CommentsSystem.add_comment(
                target_type=target_type,
                target_id=target_id,
                author=current_user,
                text=comment_text
            )
            st.success("✅ Kommentar gepostet!")
            st.rerun()

    st.divider()

    # Display comments
    if not comments:
        st.info("Noch keine Kommentare. Sei der Erste!")
    else:
        st.markdown(f"**{len(comments)} Kommentar(e)**")

        # Sort by date (newest first)
        comments.sort(key=lambda x: x['created_at'], reverse=True)

        for comment in comments:
            render_comment_card(comment, current_user, target_type, target_id)


def render_comment_card(comment: Dict, current_user: str, target_type: str, target_id: str):
    """Render a single comment card with replies"""
    # Highlight mentions
    text = comment['text']
    for mention in comment['mentions']:
        text = text.replace(f'@{mention}', f'**@{mention}**')

    # Container for comment
    with st.container():
        # Comment header
        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(f"**{comment['author']}** • {comment['created_at']}")
            if comment.get('edited_at'):
                st.caption(f"(Bearbeitet: {comment['edited_at']})")

        with col2:
            # Like button
            like_count = len(comment.get('likes', []))
            is_liked = current_user in comment.get('likes', [])

            if st.button(f"{'❤️' if is_liked else '🤍'} {like_count}", key=f"like_{comment['id']}"):
                CommentsSystem.toggle_like(comment['id'], current_user)
                st.rerun()

        # Comment text
        st.markdown(text)

        # Comment actions
        col1, col2, col3 = st.columns([1, 1, 2])

        # Reply button
        if col1.button("↩️ Antworten", key=f"reply_btn_{comment['id']}"):
            st.session_state[f"replying_to_{comment['id']}"] = True

        # Edit/Delete (only for author)
        if comment['author'] == current_user:
            if col2.button("✏️ Bearbeiten", key=f"edit_{comment['id']}"):
                st.session_state[f"editing_{comment['id']}"] = True

            if col3.button("🗑 Löschen", key=f"delete_{comment['id']}"):
                CommentsSystem.delete_comment(comment['id'])
                st.success("Kommentar gelöscht!")
                st.rerun()

        # Edit form
        if st.session_state.get(f"editing_{comment['id']}", False):
            with st.form(f"edit_form_{comment['id']}"):
                new_text = st.text_area("Kommentar bearbeiten", value=comment['text'])

                col1, col2 = st.columns(2)

                if col1.form_submit_button("💾 Speichern"):
                    CommentsSystem.update_comment(comment['id'], new_text)
                    st.session_state[f"editing_{comment['id']}"] = False
                    st.success("Kommentar aktualisiert!")
                    st.rerun()

                if col2.form_submit_button("❌ Abbrechen"):
                    st.session_state[f"editing_{comment['id']}"] = False
                    st.rerun()

        # Reply form
        if st.session_state.get(f"replying_to_{comment['id']}", False):
            with st.form(f"reply_form_{comment['id']}"):
                reply_text = st.text_area(
                    "Antwort",
                    placeholder=f"Antwort auf {comment['author']}...",
                    label_visibility="collapsed"
                )

                col1, col2 = st.columns(2)

                if col1.form_submit_button("💬 Antworten"):
                    if reply_text.strip():
                        CommentsSystem.add_comment(
                            target_type=target_type,
                            target_id=target_id,
                            author=current_user,
                            text=reply_text,
                            parent_id=comment['id']
                        )
                        st.session_state[f"replying_to_{comment['id']}"] = False
                        st.success("Antwort gepostet!")
                        st.rerun()

                if col2.form_submit_button("❌ Abbrechen"):
                    st.session_state[f"replying_to_{comment['id']}"] = False
                    st.rerun()

        # Display replies
        replies = CommentsSystem.get_replies(comment['id'])

        if replies:
            # Sort replies by date
            replies.sort(key=lambda x: x['created_at'])

            st.markdown(f"**{len(replies)} Antwort(en):**")

            for reply in replies:
                # Indent replies
                with st.container():
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;↳ **{reply['author']}** • {reply['created_at']}")

                    # Highlight mentions in reply
                    reply_text = reply['text']
                    for mention in reply['mentions']:
                        reply_text = reply_text.replace(f'@{mention}', f'**@{mention}**')

                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{reply_text}")

                    # Like button for reply
                    like_count = len(reply.get('likes', []))
                    is_liked = current_user in reply.get('likes', [])

                    if st.button(f"{'❤️' if is_liked else '🤍'} {like_count}", key=f"like_{reply['id']}"):
                        CommentsSystem.toggle_like(reply['id'], current_user)
                        st.rerun()

        st.divider()


def render_comment_notifications(current_user: str):
    """Render comment notifications for user"""
    CommentsSystem.initialize_session_state()

    st.title("🔔 Mentions & Benachrichtigungen")

    # Get user notifications
    user_notifications = [
        n for n in st.session_state.comment_notifications
        if n['user'] == current_user
    ]

    if not user_notifications:
        st.info("Keine Benachrichtigungen")
        return

    # Sort by date (newest first)
    user_notifications.sort(key=lambda x: x['created_at'], reverse=True)

    # Tabs for read/unread
    unread_count = len([n for n in user_notifications if not n['read']])

    tabs = st.tabs([f"📬 Ungelesen ({unread_count})", "📭 Alle"])

    # Tab 1: Unread
    with tabs[0]:
        unread = [n for n in user_notifications if not n['read']]

        if not unread:
            st.success("✅ Alle Benachrichtigungen gelesen!")
        else:
            for notification in unread:
                render_notification_card(notification)

    # Tab 2: All
    with tabs[1]:
        for notification in user_notifications:
            render_notification_card(notification)


def render_notification_card(notification: Dict):
    """Render a single notification card"""
    comment = CommentsSystem.get_comment(notification['comment_id'])

    if not comment:
        return

    # Highlight if unread
    bg_color = "#00cc9922" if not notification['read'] else "#22222244"

    with st.container():
        st.markdown(f"""
        <div style="
            background: {bg_color};
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 4px solid {'#00cc99' if not notification['read'] else '#666'};
        ">
            <div style="font-weight: bold;">{notification['message']}</div>
            <div style="font-size: 0.9em; opacity: 0.8; margin-top: 5px;">{notification['created_at']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Show comment preview
        st.caption(f"Kommentar von {comment['author']}:")
        st.info(comment['text'][:200] + ('...' if len(comment['text']) > 200 else ''))

        col1, col2 = st.columns(2)

        # Mark as read
        if not notification['read']:
            if col1.button("✅ Als gelesen markieren", key=f"read_{notification['id']}"):
                notification['read'] = True
                st.rerun()

        # Go to comment
        if col2.button("➡️ Zum Kommentar", key=f"goto_{notification['id']}"):
            # Navigate to the target (would need routing in main app)
            st.info(f"Navigation zu {comment['target_type']} {comment['target_id']}")

        st.divider()


def render_comment_analytics(manager):
    """Render comment analytics dashboard"""
    st.title("📊 Comment Analytics")

    CommentsSystem.initialize_session_state()

    if not st.session_state.comments:
        st.info("Noch keine Kommentare für Analysen")
        return

    # KPIs
    col1, col2, col3, col4 = st.columns(4)

    total_comments = len(st.session_state.comments)
    total_replies = len([c for c in st.session_state.comments if c.get('parent_id')])
    total_mentions = sum(len(c.get('mentions', [])) for c in st.session_state.comments)
    total_likes = sum(len(c.get('likes', [])) for c in st.session_state.comments)

    col1.metric("Kommentare", total_comments)
    col2.metric("Antworten", total_replies)
    col3.metric("Mentions", total_mentions)
    col4.metric("Likes", total_likes)

    st.divider()

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        # Comments by author
        st.markdown("#### 👥 Kommentare pro Autor")

        author_counts = {}
        for comment in st.session_state.comments:
            author = comment['author']
            author_counts[author] = author_counts.get(author, 0) + 1

        if author_counts:
            import plotly.graph_objects as go

            fig = go.Figure(data=[go.Bar(
                x=list(author_counts.keys()),
                y=list(author_counts.values()),
                marker_color='#00cc99'
            )])

            fig.update_layout(
                height=300,
                margin=dict(t=0, b=0, l=20, r=0),
                xaxis_title="Autor",
                yaxis_title="Anzahl Kommentare"
            )

            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Comments by target type
        st.markdown("#### 📊 Kommentare nach Typ")

        type_counts = {}
        for comment in st.session_state.comments:
            target_type = comment['target_type']
            type_counts[target_type] = type_counts.get(target_type, 0) + 1

        if type_counts:
            fig = go.Figure(data=[go.Pie(
                labels=list(type_counts.keys()),
                values=list(type_counts.values()),
                hole=0.4
            )])

            fig.update_layout(
                height=300,
                margin=dict(t=0, b=0, l=0, r=0),
                showlegend=True
            )

            st.plotly_chart(fig, use_container_width=True)

    # Activity timeline
    st.markdown("#### 📈 Aktivitäts-Timeline")

    # Group comments by date
    from collections import defaultdict
    import pandas as pd

    date_counts = defaultdict(int)

    for comment in st.session_state.comments:
        date = comment['created_at'].split()[0]  # Get date part
        date_counts[date] += 1

    if date_counts:
        df = pd.DataFrame({
            'Date': list(date_counts.keys()),
            'Comments': list(date_counts.values())
        })

        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')

        import plotly.express as px

        fig = px.line(
            df,
            x='Date',
            y='Comments',
            title='',
            markers=True
        )

        fig.update_layout(
            height=300,
            margin=dict(t=0, b=0, l=20, r=0),
            xaxis_title="Datum",
            yaxis_title="Anzahl Kommentare"
        )

        st.plotly_chart(fig, use_container_width=True)

    # Most active discussions
    st.markdown("#### 🔥 Aktivste Diskussionen")

    # Count comments per target
    target_counts = defaultdict(lambda: {'count': 0, 'target_type': '', 'target_id': ''})

    for comment in st.session_state.comments:
        key = f"{comment['target_type']}:{comment['target_id']}"
        target_counts[key]['count'] += 1
        target_counts[key]['target_type'] = comment['target_type']
        target_counts[key]['target_id'] = comment['target_id']

    # Sort by count
    sorted_targets = sorted(target_counts.items(), key=lambda x: x[1]['count'], reverse=True)

    for key, data in sorted_targets[:10]:  # Top 10
        target_type = data['target_type']
        target_id = data['target_id']
        count = data['count']

        # Try to get target name
        target_name = "Unknown"
        if target_type == 'project':
            project = manager.get_project(target_id)
            if project:
                target_name = project['title']

        st.write(f"📌 **{target_name}** ({target_type}) - {count} Kommentar(e)")
