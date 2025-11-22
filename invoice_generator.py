"""
Invoice Generator Module
Professional invoice creation and management
"""

import streamlit as st
from datetime import datetime, timedelta
import uuid
from typing import Dict, List
import plotly.express as px
import plotly.graph_objects as go


class InvoiceManager:
    """Manage invoices and clients"""

    @staticmethod
    def initialize_session_state():
        """Initialize invoice data in session state"""
        if 'invoices' not in st.session_state:
            st.session_state.invoices = []

        if 'clients' not in st.session_state:
            st.session_state.clients = []

    @staticmethod
    def generate_invoice_number() -> str:
        """Generate unique invoice number"""
        year = datetime.now().year
        month = datetime.now().month
        count = len(st.session_state.invoices) + 1
        return f"INV-{year}{month:02d}-{count:04d}"

    @staticmethod
    def add_client(name: str, company: str, email: str, address: str, tax_id: str = "") -> str:
        """Add new client"""
        client = {
            'id': str(uuid.uuid4()),
            'name': name,
            'company': company,
            'email': email,
            'address': address,
            'tax_id': tax_id,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        st.session_state.clients.append(client)
        return client['id']

    @staticmethod
    def add_invoice(client_id: str, project_id: str, items: List[Dict],
                    notes: str = "", tax_rate: float = 19.0) -> str:
        """Create new invoice"""
        # Calculate totals
        subtotal = sum(item['quantity'] * item['rate'] for item in items)
        tax_amount = subtotal * (tax_rate / 100)
        total = subtotal + tax_amount

        invoice = {
            'id': str(uuid.uuid4()),
            'invoice_number': InvoiceManager.generate_invoice_number(),
            'client_id': client_id,
            'project_id': project_id,
            'items': items,
            'subtotal': subtotal,
            'tax_rate': tax_rate,
            'tax_amount': tax_amount,
            'total': total,
            'notes': notes,
            'status': 'Draft',  # Draft, Sent, Paid, Overdue, Cancelled
            'created_at': datetime.now().strftime("%Y-%m-%d"),
            'due_date': (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            'paid_at': None
        }

        st.session_state.invoices.append(invoice)
        return invoice['id']

    @staticmethod
    def get_client(client_id: str) -> Dict:
        """Get client by ID"""
        return next((c for c in st.session_state.clients if c['id'] == client_id), None)

    @staticmethod
    def get_invoice(invoice_id: str) -> Dict:
        """Get invoice by ID"""
        return next((i for i in st.session_state.invoices if i['id'] == invoice_id), None)

    @staticmethod
    def update_invoice_status(invoice_id: str, status: str):
        """Update invoice status"""
        for invoice in st.session_state.invoices:
            if invoice['id'] == invoice_id:
                invoice['status'] = status
                if status == 'Paid' and not invoice.get('paid_at'):
                    invoice['paid_at'] = datetime.now().strftime("%Y-%m-%d")
                break


def render_invoice_generator(manager):
    """Render invoice generator interface"""
    st.title("💼 Invoice Generator")

    InvoiceManager.initialize_session_state()

    tabs = st.tabs(["📋 Invoices", "➕ Create Invoice", "👥 Clients", "📊 Analytics"])

    # Tab 1: Invoice List
    with tabs[0]:
        render_invoice_list(manager)

    # Tab 2: Create Invoice
    with tabs[1]:
        render_create_invoice(manager)

    # Tab 3: Clients
    with tabs[2]:
        render_clients_management()

    # Tab 4: Analytics
    with tabs[3]:
        render_invoice_analytics()


def render_invoice_list(manager):
    """Display list of invoices"""
    st.subheader("📋 Alle Rechnungen")

    if not st.session_state.invoices:
        st.info("Noch keine Rechnungen erstellt. Erstelle deine erste Rechnung im Tab 'Create Invoice'")
        return

    # Filter options
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.multiselect(
            "Status Filter",
            ['Draft', 'Sent', 'Paid', 'Overdue', 'Cancelled'],
            default=['Draft', 'Sent', 'Overdue']
        )

    with col2:
        sort_by = st.selectbox("Sortieren nach", ["Datum (neu)", "Datum (alt)", "Betrag (hoch)", "Betrag (niedrig)"])

    # Filter and sort invoices
    filtered_invoices = [i for i in st.session_state.invoices if i['status'] in status_filter]

    if sort_by == "Datum (neu)":
        filtered_invoices.sort(key=lambda x: x['created_at'], reverse=True)
    elif sort_by == "Datum (alt)":
        filtered_invoices.sort(key=lambda x: x['created_at'])
    elif sort_by == "Betrag (hoch)":
        filtered_invoices.sort(key=lambda x: x['total'], reverse=True)
    else:
        filtered_invoices.sort(key=lambda x: x['total'])

    # Display invoices
    for invoice in filtered_invoices:
        client = InvoiceManager.get_client(invoice['client_id'])
        project = manager.get_project(invoice['project_id']) if invoice.get('project_id') else None

        status_colors = {
            'Draft': '#888',
            'Sent': '#0099cc',
            'Paid': '#00cc99',
            'Overdue': '#ff4b4b',
            'Cancelled': '#666'
        }

        status_icons = {
            'Draft': '📝',
            'Sent': '📤',
            'Paid': '✅',
            'Overdue': '⚠️',
            'Cancelled': '❌'
        }

        with st.expander(f"{status_icons[invoice['status']]} {invoice['invoice_number']} - €{invoice['total']:,.2f}", expanded=False):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Kunde:** {client['company'] if client else 'N/A'}")
                st.markdown(f"**Projekt:** {project['title'] if project else 'N/A'}")
                st.markdown(f"**Erstellt:** {invoice['created_at']}")
                st.markdown(f"**Fällig:** {invoice['due_date']}")

                if invoice.get('paid_at'):
                    st.markdown(f"**Bezahlt:** {invoice['paid_at']}")

            with col2:
                st.markdown(f"**Netto:** €{invoice['subtotal']:,.2f}")
                st.markdown(f"**MwSt ({invoice['tax_rate']}%):** €{invoice['tax_amount']:,.2f}")
                st.markdown(f"**Gesamt:** €{invoice['total']:,.2f}")

                st.markdown(f"""
                <div style="
                    background: {status_colors[invoice['status']]}33;
                    color: {status_colors[invoice['status']]};
                    padding: 5px 10px;
                    border-radius: 5px;
                    text-align: center;
                    margin-top: 10px;
                    font-weight: bold;
                ">
                    {invoice['status']}
                </div>
                """, unsafe_allow_html=True)

            # Items
            st.markdown("#### Positionen")
            for idx, item in enumerate(invoice['items'], 1):
                st.write(f"{idx}. {item['description']} - {item['quantity']}x €{item['rate']:,.2f} = €{item['quantity'] * item['rate']:,.2f}")

            if invoice['notes']:
                st.markdown("#### Notizen")
                st.info(invoice['notes'])

            # Actions
            st.divider()
            col1, col2, col3, col4 = st.columns(4)

            if col1.button("📄 PDF Export", key=f"pdf_{invoice['id']}"):
                render_invoice_pdf(invoice, client, project)

            if invoice['status'] != 'Paid':
                new_status = col2.selectbox(
                    "Status ändern",
                    ['Draft', 'Sent', 'Paid', 'Overdue', 'Cancelled'],
                    index=['Draft', 'Sent', 'Paid', 'Overdue', 'Cancelled'].index(invoice['status']),
                    key=f"status_{invoice['id']}"
                )

                if col3.button("💾 Speichern", key=f"save_{invoice['id']}"):
                    InvoiceManager.update_invoice_status(invoice['id'], new_status)
                    st.success("Status aktualisiert!")
                    st.rerun()

            if col4.button("🗑 Löschen", key=f"delete_{invoice['id']}"):
                st.session_state.invoices.remove(invoice)
                st.success("Rechnung gelöscht!")
                st.rerun()


def render_create_invoice(manager):
    """Create new invoice"""
    st.subheader("➕ Neue Rechnung erstellen")

    if not st.session_state.clients:
        st.warning("⚠️ Bitte erstelle zuerst einen Kunden im Tab 'Clients'")
        return

    with st.form("create_invoice"):
        st.markdown("### 📝 Rechnungsdetails")

        col1, col2 = st.columns(2)

        with col1:
            # Client selection
            client_options = {f"{c['company']} ({c['name']})": c['id'] for c in st.session_state.clients}
            selected_client = st.selectbox("Kunde *", list(client_options.keys()))
            client_id = client_options[selected_client]

        with col2:
            # Project selection (optional)
            project_options = {"Kein Projekt": None}
            project_options.update({p['title']: p['id'] for p in manager.projects if not p.get('is_deleted')})
            selected_project = st.selectbox("Projekt (optional)", list(project_options.keys()))
            project_id = project_options[selected_project]

        # Tax rate
        tax_rate = st.number_input("MwSt-Satz (%)", min_value=0.0, max_value=100.0, value=19.0, step=0.5)

        st.markdown("### 📦 Positionen")

        # Option to import from time logs or expenses
        if project_id:
            col1, col2 = st.columns(2)

            with col1:
                if st.checkbox("🔄 Zeit-Logs importieren"):
                    project = manager.get_project(project_id)
                    if project:
                        time_logs = project.get('time_logs', [])
                        st.info(f"Gefunden: {len(time_logs)} Zeit-Einträge")

            with col2:
                if st.checkbox("🔄 Ausgaben importieren"):
                    project = manager.get_project(project_id)
                    if project:
                        expenses = project.get('budget', {}).get('expenses', [])
                        st.info(f"Gefunden: {len(expenses)} Ausgaben")

        # Manual item entry
        num_items = st.number_input("Anzahl Positionen", min_value=1, max_value=20, value=1)

        items = []
        for i in range(num_items):
            st.markdown(f"**Position {i+1}**")

            col1, col2, col3 = st.columns([3, 1, 1])

            description = col1.text_input(f"Beschreibung", key=f"desc_{i}", placeholder="z.B. Beratungsleistung")
            quantity = col2.number_input(f"Menge", min_value=0.0, value=1.0, step=0.5, key=f"qty_{i}")
            rate = col3.number_input(f"Preis (€)", min_value=0.0, value=100.0, step=5.0, key=f"rate_{i}")

            if description:
                items.append({
                    'description': description,
                    'quantity': quantity,
                    'rate': rate
                })

        # Notes
        notes = st.text_area("Notizen / Zahlungsbedingungen", placeholder="z.B. Zahlbar innerhalb von 30 Tagen")

        # Preview
        if items:
            st.markdown("### 📊 Vorschau")

            subtotal = sum(item['quantity'] * item['rate'] for item in items)
            tax_amount = subtotal * (tax_rate / 100)
            total = subtotal + tax_amount

            col1, col2 = st.columns([2, 1])

            with col1:
                for idx, item in enumerate(items, 1):
                    st.write(f"{idx}. {item['description']} - {item['quantity']}x €{item['rate']:,.2f}")

            with col2:
                st.metric("Netto", f"€{subtotal:,.2f}")
                st.metric(f"MwSt ({tax_rate}%)", f"€{tax_amount:,.2f}")
                st.metric("**Gesamt**", f"€{total:,.2f}")

        # Submit
        submitted = st.form_submit_button("💾 Rechnung erstellen", type="primary", use_container_width=True)

        if submitted:
            if not items:
                st.error("Bitte mindestens eine Position hinzufügen")
            else:
                invoice_id = InvoiceManager.add_invoice(
                    client_id=client_id,
                    project_id=project_id,
                    items=items,
                    notes=notes,
                    tax_rate=tax_rate
                )

                st.success(f"✅ Rechnung erstellt! Rechnungsnummer: {InvoiceManager.get_invoice(invoice_id)['invoice_number']}")
                st.balloons()
                st.rerun()


def render_clients_management():
    """Manage clients"""
    st.subheader("👥 Kunden verwalten")

    tabs = st.tabs(["📋 Kundenliste", "➕ Neuer Kunde"])

    # Tab 1: Client List
    with tabs[0]:
        if not st.session_state.clients:
            st.info("Noch keine Kunden angelegt")
        else:
            for client in st.session_state.clients:
                with st.expander(f"🏢 {client['company']}", expanded=False):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Name:** {client['name']}")
                        st.write(f"**Email:** {client['email']}")
                        st.write(f"**Steuernummer:** {client.get('tax_id', 'N/A')}")

                    with col2:
                        st.write(f"**Adresse:**")
                        st.write(client['address'])

                    # Show invoices for this client
                    client_invoices = [i for i in st.session_state.invoices if i['client_id'] == client['id']]

                    st.markdown(f"**Rechnungen:** {len(client_invoices)}")

                    if client_invoices:
                        total_revenue = sum(i['total'] for i in client_invoices if i['status'] == 'Paid')
                        outstanding = sum(i['total'] for i in client_invoices if i['status'] in ['Sent', 'Overdue'])

                        col1, col2 = st.columns(2)
                        col1.metric("Umsatz", f"€{total_revenue:,.2f}")
                        col2.metric("Offen", f"€{outstanding:,.2f}")

    # Tab 2: Add Client
    with tabs[1]:
        st.markdown("### ➕ Neuen Kunden anlegen")

        with st.form("add_client"):
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("Kontaktperson *", placeholder="Max Mustermann")
                company = st.text_input("Firma *", placeholder="Mustermann GmbH")
                email = st.text_input("Email *", placeholder="max@mustermann.de")

            with col2:
                address = st.text_area("Adresse *", placeholder="Musterstraße 1\n12345 Musterstadt")
                tax_id = st.text_input("Steuernummer (optional)", placeholder="DE123456789")

            submitted = st.form_submit_button("💾 Kunde speichern", type="primary", use_container_width=True)

            if submitted:
                if not all([name, company, email, address]):
                    st.error("Bitte alle Pflichtfelder ausfüllen")
                else:
                    InvoiceManager.add_client(name, company, email, address, tax_id)
                    st.success(f"✅ Kunde '{company}' angelegt!")
                    st.rerun()


def render_invoice_analytics():
    """Display invoice analytics"""
    st.subheader("📊 Rechnungs-Analysen")

    if not st.session_state.invoices:
        st.info("Noch keine Rechnungen für Analysen vorhanden")
        return

    # KPIs
    col1, col2, col3, col4 = st.columns(4)

    total_invoices = len(st.session_state.invoices)
    total_revenue = sum(i['total'] for i in st.session_state.invoices if i['status'] == 'Paid')
    outstanding = sum(i['total'] for i in st.session_state.invoices if i['status'] in ['Sent', 'Overdue'])
    overdue = len([i for i in st.session_state.invoices if i['status'] == 'Overdue'])

    col1.metric("Rechnungen", total_invoices)
    col2.metric("Umsatz", f"€{total_revenue:,.2f}")
    col3.metric("Offen", f"€{outstanding:,.2f}")
    col4.metric("Überfällig", overdue)

    st.divider()

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        # Status distribution
        st.markdown("#### Status-Verteilung")

        status_counts = {}
        for invoice in st.session_state.invoices:
            status = invoice['status']
            status_counts[status] = status_counts.get(status, 0) + 1

        fig = go.Figure(data=[go.Pie(
            labels=list(status_counts.keys()),
            values=list(status_counts.values()),
            marker=dict(colors=['#888', '#0099cc', '#00cc99', '#ff4b4b', '#666']),
            hole=0.4
        )])

        fig.update_layout(
            height=300,
            margin=dict(t=0, b=0, l=0, r=0),
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Revenue by client
        st.markdown("#### Umsatz pro Kunde")

        client_revenue = {}
        for invoice in st.session_state.invoices:
            if invoice['status'] == 'Paid':
                client = InvoiceManager.get_client(invoice['client_id'])
                if client:
                    company = client['company']
                    client_revenue[company] = client_revenue.get(company, 0) + invoice['total']

        if client_revenue:
            fig = go.Figure(data=[go.Bar(
                x=list(client_revenue.keys()),
                y=list(client_revenue.values()),
                marker_color='#00cc99'
            )])

            fig.update_layout(
                height=300,
                margin=dict(t=0, b=0, l=20, r=0),
                xaxis_title="",
                yaxis_title="Umsatz (€)"
            )

            st.plotly_chart(fig, use_container_width=True)


def render_invoice_pdf(invoice: Dict, client: Dict, project: Dict):
    """Render invoice as HTML/PDF preview"""
    st.markdown("### 📄 Rechnungsvorschau")

    html_content = f"""
    <div style="max-width: 800px; margin: 0 auto; padding: 40px; background: white; color: black; font-family: Arial, sans-serif;">
        <!-- Header -->
        <div style="text-align: right; margin-bottom: 40px;">
            <h1 style="color: #00cc99; margin: 0;">RECHNUNG</h1>
            <p style="font-size: 1.2em; margin: 5px 0;">{invoice['invoice_number']}</p>
        </div>

        <!-- Company Info -->
        <div style="margin-bottom: 30px;">
            <strong>Ihre Firma GmbH</strong><br>
            Musterstraße 123<br>
            12345 Musterstadt<br>
            info@ihrefirma.de
        </div>

        <!-- Client Info -->
        <div style="margin-bottom: 40px;">
            <strong>{client['company']}</strong><br>
            {client['name']}<br>
            {client['address'].replace(chr(10), '<br>')}
        </div>

        <!-- Invoice Details -->
        <div style="margin-bottom: 30px;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td><strong>Rechnungsdatum:</strong></td>
                    <td style="text-align: right;">{invoice['created_at']}</td>
                </tr>
                <tr>
                    <td><strong>Fälligkeitsdatum:</strong></td>
                    <td style="text-align: right;">{invoice['due_date']}</td>
                </tr>
                {f'<tr><td><strong>Projekt:</strong></td><td style="text-align: right;">{project["title"]}</td></tr>' if project else ''}
            </table>
        </div>

        <!-- Items Table -->
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px;">
            <thead>
                <tr style="background: #f0f0f0; border-bottom: 2px solid #00cc99;">
                    <th style="padding: 10px; text-align: left;">Position</th>
                    <th style="padding: 10px; text-align: right;">Menge</th>
                    <th style="padding: 10px; text-align: right;">Preis</th>
                    <th style="padding: 10px; text-align: right;">Gesamt</th>
                </tr>
            </thead>
            <tbody>
                {''.join(f'''
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 10px;">{item['description']}</td>
                    <td style="padding: 10px; text-align: right;">{item['quantity']}</td>
                    <td style="padding: 10px; text-align: right;">€{item['rate']:,.2f}</td>
                    <td style="padding: 10px; text-align: right;">€{item['quantity'] * item['rate']:,.2f}</td>
                </tr>
                ''' for item in invoice['items'])}
            </tbody>
        </table>

        <!-- Totals -->
        <div style="text-align: right; margin-bottom: 30px;">
            <table style="margin-left: auto; width: 300px;">
                <tr>
                    <td style="padding: 5px;"><strong>Nettobetrag:</strong></td>
                    <td style="padding: 5px; text-align: right;">€{invoice['subtotal']:,.2f}</td>
                </tr>
                <tr>
                    <td style="padding: 5px;"><strong>MwSt ({invoice['tax_rate']}%):</strong></td>
                    <td style="padding: 5px; text-align: right;">€{invoice['tax_amount']:,.2f}</td>
                </tr>
                <tr style="border-top: 2px solid #00cc99; font-size: 1.2em;">
                    <td style="padding: 10px;"><strong>Gesamtbetrag:</strong></td>
                    <td style="padding: 10px; text-align: right;"><strong>€{invoice['total']:,.2f}</strong></td>
                </tr>
            </table>
        </div>

        <!-- Notes -->
        {f'<div style="margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-left: 4px solid #00cc99;"><strong>Zahlungsbedingungen:</strong><br>{invoice["notes"]}</div>' if invoice['notes'] else ''}

        <!-- Footer -->
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 0.9em; text-align: center; color: #666;">
            <p>Vielen Dank für Ihr Vertrauen!</p>
            <p>Bankverbindung: IBAN DE12 3456 7890 1234 5678 90 | BIC: ABCDEFGH</p>
        </div>
    </div>
    """

    st.markdown(html_content, unsafe_allow_html=True)

    st.info("💡 Tipp: Nutze die Browser-Druckfunktion (Strg+P) um die Rechnung als PDF zu speichern")
