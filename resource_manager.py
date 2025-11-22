"""
Resource Manager Module
Manage team members, equipment, and rooms with booking system
"""

import streamlit as st
from datetime import datetime, timedelta
import uuid
from typing import Dict, List
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


class ResourceManager:
    """Manage resources and bookings"""

    RESOURCE_TYPES = {
        'person': {'icon': '👤', 'label': 'Person'},
        'equipment': {'icon': '🛠️', 'label': 'Gerät/Equipment'},
        'room': {'icon': '🏢', 'label': 'Raum/Location'}
    }

    @staticmethod
    def initialize_session_state():
        """Initialize resource data in session state"""
        if 'resources' not in st.session_state:
            st.session_state.resources = []

        if 'resource_bookings' not in st.session_state:
            st.session_state.resource_bookings = []

    @staticmethod
    def add_resource(name: str, resource_type: str, description: str = "",
                    capacity: int = 1, location: str = "", properties: Dict = None) -> str:
        """Add new resource"""
        resource = {
            'id': str(uuid.uuid4()),
            'name': name,
            'type': resource_type,
            'description': description,
            'capacity': capacity,
            'location': location,
            'properties': properties or {},
            'status': 'active',  # active, maintenance, inactive
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        st.session_state.resources.append(resource)
        return resource['id']

    @staticmethod
    def add_booking(resource_id: str, project_id: str, user_name: str,
                   start_date: str, end_date: str, notes: str = "") -> str:
        """Create resource booking"""
        booking = {
            'id': str(uuid.uuid4()),
            'resource_id': resource_id,
            'project_id': project_id,
            'user_name': user_name,
            'start_date': start_date,
            'end_date': end_date,
            'notes': notes,
            'status': 'confirmed',  # confirmed, pending, cancelled
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        st.session_state.resource_bookings.append(booking)
        return booking['id']

    @staticmethod
    def check_availability(resource_id: str, start_date: str, end_date: str) -> bool:
        """Check if resource is available for given period"""
        for booking in st.session_state.resource_bookings:
            if booking['resource_id'] == resource_id and booking['status'] == 'confirmed':
                # Check for overlap
                booking_start = datetime.strptime(booking['start_date'], "%Y-%m-%d")
                booking_end = datetime.strptime(booking['end_date'], "%Y-%m-%d")
                check_start = datetime.strptime(start_date, "%Y-%m-%d")
                check_end = datetime.strptime(end_date, "%Y-%m-%d")

                if not (check_end < booking_start or check_start > booking_end):
                    return False

        return True

    @staticmethod
    def get_resource(resource_id: str) -> Dict:
        """Get resource by ID"""
        return next((r for r in st.session_state.resources if r['id'] == resource_id), None)

    @staticmethod
    def get_resource_utilization(resource_id: str, days: int = 30) -> float:
        """Calculate resource utilization percentage"""
        today = datetime.now()
        period_start = today - timedelta(days=days)

        booked_days = 0
        for booking in st.session_state.resource_bookings:
            if booking['resource_id'] == resource_id and booking['status'] == 'confirmed':
                start = datetime.strptime(booking['start_date'], "%Y-%m-%d")
                end = datetime.strptime(booking['end_date'], "%Y-%m-%d")

                # Calculate overlap with period
                overlap_start = max(start, period_start)
                overlap_end = min(end, today)

                if overlap_start < overlap_end:
                    booked_days += (overlap_end - overlap_start).days

        return min(100, (booked_days / days) * 100)


def render_resource_manager(manager):
    """Render resource management interface"""
    st.title("📦 Resource Manager")

    ResourceManager.initialize_session_state()

    tabs = st.tabs(["📋 Resources", "📅 Bookings", "➕ Add Resource", "📊 Analytics"])

    # Tab 1: Resource List
    with tabs[0]:
        render_resource_list()

    # Tab 2: Bookings
    with tabs[1]:
        render_bookings(manager)

    # Tab 3: Add Resource
    with tabs[2]:
        render_add_resource()

    # Tab 4: Analytics
    with tabs[3]:
        render_resource_analytics()


def render_resource_list():
    """Display list of resources"""
    st.subheader("📋 Alle Ressourcen")

    if not st.session_state.resources:
        st.info("Noch keine Ressourcen angelegt. Erstelle deine erste Ressource im Tab 'Add Resource'")
        return

    # Filter by type
    filter_types = st.multiselect(
        "Filter nach Typ",
        ['person', 'equipment', 'room'],
        default=['person', 'equipment', 'room'],
        format_func=lambda x: ResourceManager.RESOURCE_TYPES[x]['label']
    )

    # Group resources by type
    for resource_type in filter_types:
        type_info = ResourceManager.RESOURCE_TYPES[resource_type]
        resources_of_type = [r for r in st.session_state.resources if r['type'] == resource_type and r['status'] == 'active']

        if resources_of_type:
            st.markdown(f"### {type_info['icon']} {type_info['label']}s")

            for resource in resources_of_type:
                utilization = ResourceManager.get_resource_utilization(resource['id'])

                with st.expander(f"{type_info['icon']} {resource['name']} - {utilization:.0f}% Auslastung", expanded=False):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.write(f"**Typ:** {type_info['label']}")
                        if resource['description']:
                            st.write(f"**Beschreibung:** {resource['description']}")
                        if resource['location']:
                            st.write(f"**Standort:** {resource['location']}")
                        if resource['capacity'] > 1:
                            st.write(f"**Kapazität:** {resource['capacity']}")

                        # Show properties
                        if resource['properties']:
                            st.write("**Eigenschaften:**")
                            for key, value in resource['properties'].items():
                                st.write(f"• {key}: {value}")

                    with col2:
                        # Utilization gauge
                        st.metric("Auslastung (30 Tage)", f"{utilization:.0f}%")

                        # Status
                        status_colors = {'active': '#00cc99', 'maintenance': '#ffa500', 'inactive': '#888'}
                        status_labels = {'active': 'Aktiv', 'maintenance': 'Wartung', 'inactive': 'Inaktiv'}

                        st.markdown(f"""
                        <div style="
                            background: {status_colors[resource['status']]}33;
                            color: {status_colors[resource['status']]};
                            padding: 5px 10px;
                            border-radius: 5px;
                            text-align: center;
                            font-weight: bold;
                            margin-top: 10px;
                        ">
                            {status_labels[resource['status']]}
                        </div>
                        """, unsafe_allow_html=True)

                    # Show bookings for this resource
                    st.markdown("#### 📅 Kommende Buchungen")

                    resource_bookings = [
                        b for b in st.session_state.resource_bookings
                        if b['resource_id'] == resource['id'] and b['status'] == 'confirmed'
                    ]

                    # Filter future bookings
                    today = datetime.now()
                    future_bookings = [
                        b for b in resource_bookings
                        if datetime.strptime(b['end_date'], "%Y-%m-%d") >= today
                    ]

                    future_bookings.sort(key=lambda x: x['start_date'])

                    if future_bookings:
                        for booking in future_bookings[:5]:  # Show next 5 bookings
                            st.write(f"• {booking['start_date']} bis {booking['end_date']} - {booking['user_name']}")
                    else:
                        st.info("Keine kommenden Buchungen")

                    # Actions
                    st.divider()

                    col1, col2 = st.columns(2)

                    new_status = col1.selectbox(
                        "Status ändern",
                        ['active', 'maintenance', 'inactive'],
                        index=['active', 'maintenance', 'inactive'].index(resource['status']),
                        format_func=lambda x: status_labels[x],
                        key=f"status_{resource['id']}"
                    )

                    if col2.button("💾 Speichern", key=f"save_{resource['id']}"):
                        resource['status'] = new_status
                        st.success("Status aktualisiert!")
                        st.rerun()


def render_bookings(manager):
    """Display and manage bookings"""
    st.subheader("📅 Ressourcen-Buchungen")

    tabs = st.tabs(["📋 Buchungsliste", "➕ Neue Buchung", "📆 Kalender"])

    # Tab 1: Booking List
    with tabs[0]:
        if not st.session_state.resource_bookings:
            st.info("Noch keine Buchungen vorhanden")
        else:
            # Filter options
            col1, col2 = st.columns(2)

            with col1:
                status_filter = st.multiselect(
                    "Status Filter",
                    ['confirmed', 'pending', 'cancelled'],
                    default=['confirmed', 'pending']
                )

            with col2:
                time_filter = st.selectbox(
                    "Zeitraum",
                    ["Alle", "Aktuell", "Zukünftig", "Vergangene"]
                )

            # Filter bookings
            filtered_bookings = [b for b in st.session_state.resource_bookings if b['status'] in status_filter]

            today = datetime.now()

            if time_filter == "Aktuell":
                filtered_bookings = [
                    b for b in filtered_bookings
                    if datetime.strptime(b['start_date'], "%Y-%m-%d") <= today <= datetime.strptime(b['end_date'], "%Y-%m-%d")
                ]
            elif time_filter == "Zukünftig":
                filtered_bookings = [
                    b for b in filtered_bookings
                    if datetime.strptime(b['start_date'], "%Y-%m-%d") > today
                ]
            elif time_filter == "Vergangene":
                filtered_bookings = [
                    b for b in filtered_bookings
                    if datetime.strptime(b['end_date'], "%Y-%m-%d") < today
                ]

            # Sort by start date
            filtered_bookings.sort(key=lambda x: x['start_date'], reverse=True)

            # Display bookings
            for booking in filtered_bookings:
                resource = ResourceManager.get_resource(booking['resource_id'])
                project = manager.get_project(booking.get('project_id')) if booking.get('project_id') else None

                if resource:
                    type_info = ResourceManager.RESOURCE_TYPES[resource['type']]

                    with st.expander(f"{type_info['icon']} {resource['name']} - {booking['start_date']} bis {booking['end_date']}", expanded=False):
                        col1, col2 = st.columns([2, 1])

                        with col1:
                            st.write(f"**Ressource:** {resource['name']}")
                            st.write(f"**Gebucht von:** {booking['user_name']}")
                            if project:
                                st.write(f"**Projekt:** {project['title']}")
                            st.write(f"**Von:** {booking['start_date']}")
                            st.write(f"**Bis:** {booking['end_date']}")

                            if booking['notes']:
                                st.info(f"**Notizen:** {booking['notes']}")

                        with col2:
                            # Calculate duration
                            start = datetime.strptime(booking['start_date'], "%Y-%m-%d")
                            end = datetime.strptime(booking['end_date'], "%Y-%m-%d")
                            duration = (end - start).days + 1

                            st.metric("Dauer", f"{duration} Tag(e)")

                            # Status badge
                            status_colors = {'confirmed': '#00cc99', 'pending': '#ffa500', 'cancelled': '#888'}
                            status_labels = {'confirmed': 'Bestätigt', 'pending': 'Ausstehend', 'cancelled': 'Storniert'}

                            st.markdown(f"""
                            <div style="
                                background: {status_colors[booking['status']]}33;
                                color: {status_colors[booking['status']]};
                                padding: 5px 10px;
                                border-radius: 5px;
                                text-align: center;
                                font-weight: bold;
                                margin-top: 10px;
                            ">
                                {status_labels[booking['status']]}
                            </div>
                            """, unsafe_allow_html=True)

                        # Actions
                        st.divider()

                        col1, col2 = st.columns(2)

                        if booking['status'] != 'cancelled':
                            if col1.button("❌ Stornieren", key=f"cancel_{booking['id']}"):
                                booking['status'] = 'cancelled'
                                st.success("Buchung storniert!")
                                st.rerun()

                        if col2.button("🗑 Löschen", key=f"delete_{booking['id']}"):
                            st.session_state.resource_bookings.remove(booking)
                            st.success("Buchung gelöscht!")
                            st.rerun()

    # Tab 2: New Booking
    with tabs[1]:
        st.markdown("### ➕ Neue Buchung erstellen")

        if not st.session_state.resources:
            st.warning("⚠️ Bitte erstelle zuerst Ressourcen")
        else:
            with st.form("create_booking"):
                # Resource selection
                active_resources = [r for r in st.session_state.resources if r['status'] == 'active']

                resource_options = {}
                for resource in active_resources:
                    type_info = ResourceManager.RESOURCE_TYPES[resource['type']]
                    label = f"{type_info['icon']} {resource['name']} ({type_info['label']})"
                    resource_options[label] = resource['id']

                selected_resource = st.selectbox("Ressource *", list(resource_options.keys()))
                resource_id = resource_options[selected_resource]

                col1, col2 = st.columns(2)

                with col1:
                    start_date = st.date_input("Von *", value=datetime.now())

                with col2:
                    end_date = st.date_input("Bis *", value=datetime.now() + timedelta(days=1))

                # Project selection (optional)
                project_options = {"Kein Projekt": None}
                project_options.update({p['title']: p['id'] for p in manager.projects if not p.get('is_deleted')})
                selected_project = st.selectbox("Projekt (optional)", list(project_options.keys()))
                project_id = project_options[selected_project]

                user_name = st.text_input("Gebucht von", value=st.session_state.auth.current_user_name() if hasattr(st.session_state, 'auth') else "")

                notes = st.text_area("Notizen", placeholder="Zweck der Buchung, besondere Anforderungen, etc.")

                # Check availability
                if start_date and end_date:
                    is_available = ResourceManager.check_availability(
                        resource_id,
                        start_date.strftime("%Y-%m-%d"),
                        end_date.strftime("%Y-%m-%d")
                    )

                    if is_available:
                        st.success("✅ Ressource ist verfügbar!")
                    else:
                        st.error("❌ Ressource ist in diesem Zeitraum bereits gebucht!")

                submitted = st.form_submit_button("📅 Buchung erstellen", type="primary", use_container_width=True)

                if submitted:
                    if not all([resource_id, start_date, end_date, user_name]):
                        st.error("Bitte alle Pflichtfelder ausfüllen")
                    elif end_date < start_date:
                        st.error("Enddatum muss nach Startdatum liegen")
                    elif not is_available:
                        st.error("Ressource ist in diesem Zeitraum nicht verfügbar")
                    else:
                        ResourceManager.add_booking(
                            resource_id=resource_id,
                            project_id=project_id,
                            user_name=user_name,
                            start_date=start_date.strftime("%Y-%m-%d"),
                            end_date=end_date.strftime("%Y-%m-%d"),
                            notes=notes
                        )

                        st.success("✅ Buchung erstellt!")
                        st.balloons()
                        st.rerun()

    # Tab 3: Calendar View
    with tabs[2]:
        st.markdown("### 📆 Buchungskalender")

        if not st.session_state.resource_bookings:
            st.info("Keine Buchungen vorhanden")
        else:
            # Create Gantt-like chart
            data = []

            for booking in st.session_state.resource_bookings:
                if booking['status'] == 'confirmed':
                    resource = ResourceManager.get_resource(booking['resource_id'])
                    if resource:
                        data.append({
                            'Resource': resource['name'],
                            'Start': booking['start_date'],
                            'End': booking['end_date'],
                            'User': booking['user_name']
                        })

            if data:
                df = pd.DataFrame(data)
                df['Start'] = pd.to_datetime(df['Start'])
                df['End'] = pd.to_datetime(df['End'])

                fig = px.timeline(
                    df,
                    x_start='Start',
                    x_end='End',
                    y='Resource',
                    color='User',
                    title='Ressourcen-Buchungskalender'
                )

                fig.update_yaxes(categoryorder='total ascending')
                fig.update_layout(height=max(400, len(df) * 40))

                st.plotly_chart(fig, use_container_width=True)


def render_add_resource():
    """Add new resource"""
    st.subheader("➕ Neue Ressource hinzufügen")

    with st.form("add_resource"):
        # Basic info
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Name *", placeholder="z.B. Meetingraum A, Beamer, Max Mustermann")
            resource_type = st.selectbox(
                "Typ *",
                ['person', 'equipment', 'room'],
                format_func=lambda x: ResourceManager.RESOURCE_TYPES[x]['label']
            )

        with col2:
            location = st.text_input("Standort (optional)", placeholder="z.B. Gebäude A, 2. OG")
            capacity = st.number_input("Kapazität", min_value=1, max_value=100, value=1,
                                      help="Anzahl gleichzeitiger Nutzungen möglich")

        description = st.text_area("Beschreibung (optional)", placeholder="Zusätzliche Informationen...")

        # Type-specific properties
        st.markdown("### 📝 Zusätzliche Eigenschaften")

        if resource_type == 'person':
            col1, col2 = st.columns(2)
            role = col1.text_input("Rolle", placeholder="z.B. Entwickler, Designer")
            skill = col2.text_input("Skills", placeholder="z.B. Python, React")
            properties = {'role': role, 'skills': skill}

        elif resource_type == 'equipment':
            col1, col2 = st.columns(2)
            model = col1.text_input("Modell", placeholder="z.B. Epson EB-2250U")
            serial = col2.text_input("Seriennummer", placeholder="z.B. SN123456")
            properties = {'model': model, 'serial': serial}

        elif resource_type == 'room':
            col1, col2 = st.columns(2)
            seats = col1.number_input("Sitzplätze", min_value=1, value=10)
            equipment_list = col2.text_input("Ausstattung", placeholder="z.B. Beamer, Whiteboard")
            properties = {'seats': seats, 'equipment': equipment_list}

        submitted = st.form_submit_button("💾 Ressource erstellen", type="primary", use_container_width=True)

        if submitted:
            if not name:
                st.error("Bitte Name eingeben")
            else:
                ResourceManager.add_resource(
                    name=name,
                    resource_type=resource_type,
                    description=description,
                    capacity=capacity,
                    location=location,
                    properties=properties
                )

                st.success(f"✅ Ressource '{name}' erstellt!")
                st.balloons()
                st.rerun()


def render_resource_analytics():
    """Display resource analytics"""
    st.subheader("📊 Ressourcen-Analysen")

    if not st.session_state.resources:
        st.info("Noch keine Ressourcen vorhanden")
        return

    # KPIs
    col1, col2, col3, col4 = st.columns(4)

    total_resources = len([r for r in st.session_state.resources if r['status'] == 'active'])
    total_bookings = len([b for b in st.session_state.resource_bookings if b['status'] == 'confirmed'])

    # Calculate average utilization
    utilizations = [ResourceManager.get_resource_utilization(r['id']) for r in st.session_state.resources if r['status'] == 'active']
    avg_utilization = sum(utilizations) / len(utilizations) if utilizations else 0

    # Count resources by type
    type_counts = {}
    for resource in st.session_state.resources:
        if resource['status'] == 'active':
            rtype = resource['type']
            type_counts[rtype] = type_counts.get(rtype, 0) + 1

    col1.metric("Aktive Ressourcen", total_resources)
    col2.metric("Buchungen", total_bookings)
    col3.metric("Ø Auslastung", f"{avg_utilization:.0f}%")
    col4.metric("Typen", len(type_counts))

    st.divider()

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        # Resource distribution by type
        st.markdown("#### Ressourcen nach Typ")

        if type_counts:
            labels = [ResourceManager.RESOURCE_TYPES[t]['label'] for t in type_counts.keys()]
            values = list(type_counts.values())

            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.4
            )])

            fig.update_layout(
                height=300,
                margin=dict(t=0, b=0, l=0, r=0),
                showlegend=True
            )

            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Top utilized resources
        st.markdown("#### Top Ausgelastete Ressourcen")

        resource_utils = []
        for resource in st.session_state.resources:
            if resource['status'] == 'active':
                util = ResourceManager.get_resource_utilization(resource['id'])
                resource_utils.append({
                    'name': resource['name'],
                    'utilization': util
                })

        resource_utils.sort(key=lambda x: x['utilization'], reverse=True)

        if resource_utils:
            top_resources = resource_utils[:10]

            fig = go.Figure(data=[go.Bar(
                x=[r['utilization'] for r in top_resources],
                y=[r['name'] for r in top_resources],
                orientation='h',
                marker_color='#00cc99'
            )])

            fig.update_layout(
                height=300,
                margin=dict(t=0, b=0, l=20, r=0),
                xaxis_title="Auslastung (%)",
                yaxis_title=""
            )

            st.plotly_chart(fig, use_container_width=True)

    # Booking timeline
    st.markdown("#### 📅 Buchungs-Zeitlinie (nächste 30 Tage)")

    if st.session_state.resource_bookings:
        # Filter future bookings
        today = datetime.now()
        future_date = today + timedelta(days=30)

        timeline_data = []
        for booking in st.session_state.resource_bookings:
            if booking['status'] == 'confirmed':
                start = datetime.strptime(booking['start_date'], "%Y-%m-%d")
                end = datetime.strptime(booking['end_date'], "%Y-%m-%d")

                if start <= future_date and end >= today:
                    resource = ResourceManager.get_resource(booking['resource_id'])
                    if resource:
                        timeline_data.append({
                            'Resource': resource['name'],
                            'Start': booking['start_date'],
                            'End': booking['end_date'],
                            'User': booking['user_name']
                        })

        if timeline_data:
            df = pd.DataFrame(timeline_data)
            df['Start'] = pd.to_datetime(df['Start'])
            df['End'] = pd.to_datetime(df['End'])

            fig = px.timeline(
                df,
                x_start='Start',
                x_end='End',
                y='Resource',
                color='User',
                title=''
            )

            fig.update_yaxes(categoryorder='total ascending')
            fig.update_layout(height=max(300, len(df) * 30))

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Keine Buchungen in den nächsten 30 Tagen")
    else:
        st.info("Noch keine Buchungen vorhanden")
