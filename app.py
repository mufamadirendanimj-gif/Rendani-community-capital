import streamlit as st
import sqlite3
import pandas as pd
import datetime
import random
import json
import io

# ==============================================================================
# 1. PAGE CONFIGURATION & VENDA STYLING (Deep Navy, Gold, Emerald Green)
# ==============================================================================
st.set_page_config(
    page_title="Rendani Community Capital (R.C.C)",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Venda Cultural Motifs & Mobile Styling
st.markdown("""
<style>
    /* Theme Colors */
    :root {
        --deep-navy: #0B132B;
        --venda-gold: #D4AF37;
        --emerald-green: #097969;
        --light-bg: #F8F9FA;
        --card-bg: #FFFFFF;
    }

    /* Main Container Customization */
    .stApp {
        background-color: #F4F6F9;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Header Banner */
    .venda-header {
        background: linear-gradient(135deg, #0B132B 0%, #1C2541 60%, #097969 100%);
        border-bottom: 5px solid #D4AF37;
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }

    .venda-header h1 {
        color: #D4AF37 !important;
        font-weight: 800;
        margin: 0;
        font-size: 2.2rem;
        letter-spacing: 0.5px;
    }

    .venda-header p {
        color: #E0E6ED;
        margin-top: 5px;
        font-size: 1rem;
    }

    /* Custom Cards */
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 18px;
        border-left: 5px solid #097969;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 15px;
    }

    .metric-card.gold {
        border-left-color: #D4AF37;
    }

    .metric-card.navy {
        border-left-color: #0B132B;
    }

    .metric-title {
        font-size: 0.85rem;
        color: #6C757D;
        text-transform: uppercase;
        font-weight: 600;
    }

    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #0B132B;
        margin-top: 5px;
    }

    /* WhatsApp Simulator Box */
    .whatsapp-box {
        background-color: #E5DDD5;
        border-radius: 12px;
        padding: 15px;
        max-width: 450px;
        margin: 0 auto;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        font-family: Arial, sans-serif;
    }

    .whatsapp-bubble {
        background-color: #DCF8C6;
        border-radius: 8px;
        padding: 12px 15px;
        color: #000;
        font-size: 0.95rem;
        position: relative;
        box-shadow: 0 1px 2px rgba(0,0,0,0.15);
    }

    .whatsapp-time {
        font-size: 0.7rem;
        color: #777;
        text-align: right;
        margin-top: 5px;
    }

    /* Streamlit UI Overrides */
    .stButton>button {
        background: linear-gradient(180deg, #097969 0%, #065449 100%);
        color: white !important;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        transition: all 0.2s ease;
    }

    .stButton>button:hover {
        background: linear-gradient(180deg, #D4AF37 0%, #B38F2A 100%);
        color: #0B132B !important;
    }

    /* Mobile Responsive Optimizations */
    @media (max-width: 768px) {
        .venda-header h1 {
            font-size: 1.6rem;
        }
        .venda-header {
            padding: 15px;
        }
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 2. DATABASE INITIALIZATION & MANAGEMENT (SQLite)
# ==============================================================================
DB_FILE = "rcc_stokvel.db"

def get_db_connection():
    """Establish connection to SQLite DB."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_sqlite_db():
    """Create initial schema and insert seed data if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            role TEXT DEFAULT 'Member',
            balance REAL DEFAULT 0.0,
            preferred_language TEXT DEFAULT 'English'
        )
    """)

    # Groups Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT NOT NULL,
            monthly_contribution REAL DEFAULT 500.0,
            pool_balance REAL DEFAULT 0.0,
            treasurer_id INTEGER,
            FOREIGN KEY (treasurer_id) REFERENCES users (id)
        )
    """)

    # Transactions Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            group_id INTEGER,
            amount REAL NOT NULL,
            transaction_type TEXT NOT NULL, -- Contribution, Withdrawal, Loan Repayment, Fee
            status TEXT DEFAULT 'Completed',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            reference TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (group_id) REFERENCES groups (id)
        )
    """)

    # Loans Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL NOT NULL,
            interest_rate REAL DEFAULT 0.05,
            status TEXT DEFAULT 'Active', -- Pending, Active, Paid
            issued_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Pending Multi-Sig Approvals Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pending_approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            requested_by INTEGER,
            amount REAL NOT NULL,
            recipient_info TEXT NOT NULL,
            signatures_required INTEGER DEFAULT 2,
            signatures_count INTEGER DEFAULT 1,
            signed_by_json TEXT DEFAULT '[]', -- JSON list of user IDs who signed
            status TEXT DEFAULT 'Pending', -- Pending, Approved, Rejected
            request_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES groups (id),
            FOREIGN KEY (requested_by) REFERENCES users (id)
        )
    """)

    # Seed initial data if tables are empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO users (full_name, phone, role, balance, preferred_language)
            VALUES (?, ?, ?, ?, ?)
        """, [
            ("Rendani Mufamadi", "+27821234567", "Treasurer", 12500.00, "Tshivenḓa"),
            ("Ndivhuho Khorommbi", "+27839876543", "Member", 4500.00, "Tshivenḓa"),
            ("Thabo Mokoena", "+27715551234", "Member", 3200.00, "Sepedi"),
            ("Lindiwe Chauke", "+27840001122", "Auditor", 8900.00, "Xitsonga"),
            ("Sipho Mabena", "+27723334455", "Member", 1500.00, "English")
        ])

        cursor.execute("""
            INSERT INTO groups (group_name, monthly_contribution, pool_balance, treasurer_id)
            VALUES ('Thohoyandou Unity Stokvel', 1000.00, 85000.00, 1)
        """)

        cursor.executemany("""
            INSERT INTO transactions (user_id, group_id, amount, transaction_type, status, reference)
            VALUES (?, 1, ?, ?, 'Completed', ?)
        """, [
            (1, 1000.00, 'Contribution', 'REF-CONT-101'),
            (2, 1000.00, 'Contribution', 'REF-CONT-102'),
            (3, 1000.00, 'Contribution', 'REF-CONT-103'),
            (4, 1000.00, 'Contribution', 'REF-CONT-104'),
            (1, 5000.00, 'Loan Repayment', 'REF-LOAN-001')
        ])

        cursor.execute("""
            INSERT INTO pending_approvals (group_id, requested_by, amount, recipient_info, signatures_required, signatures_count, signed_by_json)
            VALUES (1, 1, 15000.00, 'Payout to Ndivhuho (Rotational Distribution)', 3, 1, '[1]')
        """)

    conn.commit()
    conn.close()

# Run initialization
init_sqlite_db()


# ==============================================================================
# 3. HELPER FUNCTIONS
# ==============================================================================
def log_transaction(user_id, group_id, amount, t_type, reference="AUTO-GEN"):
    """Helper to safely record transactions into SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if reference == "AUTO-GEN":
        reference = f"REF-{random.randint(100000, 999999)}"

    cursor.execute("""
        INSERT INTO transactions (user_id, group_id, amount, transaction_type, status, reference)
        VALUES (?, ?, ?, ?, 'Completed', ?)
    """, (user_id, group_id, amount, t_type, reference))

    # Update group pool balance if contribution or payout
    if t_type == "Contribution":
        cursor.execute("UPDATE groups SET pool_balance = pool_balance + ? WHERE id = ?", (amount, group_id))
        cursor.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, user_id))
    elif t_type == "Withdrawal":
        cursor.execute("UPDATE groups SET pool_balance = pool_balance - ? WHERE id = ?", (amount, group_id))

    conn.commit()
    conn.close()

def get_mufamadi_response(prompt, language):
    """Multi-lingual rules engine for Mufamadi AI Assistant."""
    prompt_lower = prompt.lower()

    responses = {
        "Tshivenḓa": {
            "balance": "Mugagano wavho wa zwino u kha R.C.C ndi : balance_placeholder. Ndaa!",
            "deposit": "U itela u vhea tshelede, shumisani R.C.C Pay/EFT u ya kha akhawunthi ya tshitshavha nga tsumbo ya reference yanu.",
            "withdrawal": "U bvisa tshelede zwi ṱoḓa thempelo ya vhavhusi vhavhili kha vhararu (2-of-3 Multi-Sig).",
            "greeting": "Ndaa/Aa! Nne ndi Mufamadi AI, muthusi wavho wa zwa masheleni a R.C.C Stokvel. Ndi nga vha fhasi hani ṱhoho?",
            "default": "Ndo livhuwa mbudziso yanu. Kha vha ṱole zva zwiimela zva masheleni kana vha ambe na mulanguli wa Stokvel."
        },
        "Sepedi": {
            "balance": "Tekanyo ya gago ya bjale go R.C.C ke : balance_placeholder. Re a leboga!",
            "deposit": "Go pea tšhelete, šomiša R.C.C Pay/EFT go akhaonto ya Stokvel o šomiše poledišo ya gago.",
            "withdrawal": "Go ntšha tšhelete go nyaka amogelo go tšwa go bahlankedi ba babedi go ba bararo (2-of-3 Multi-Sig).",
            "greeting": "Thobela! Nna ke Mufamadi AI, mothusi wa gago wa matlotlo wa R.C.C Stokvel. Nka go thuša ka eng?",
            "default": "Ke lebogela potšišo ya gago. Hle lekola lenaneo la gago kapa o ikgolaganye le molaodi."
        },
        "Xitsonga": {
            "balance": "Xiyimo xa akhawunte ya n’wina eka R.C.C i : balance_placeholder. Inkomu!",
            "deposit": "Kona ku hoxa mali, tirhisani R.C.C Pay/EFT eka akhawunte ya Stokvel hi ku tirhisa kombo ra n'wina.",
            "withdrawal": "Ku humesa mali swi lava mpfumelelo wa vawundli vambirhi eka vanharhu (2-of-3 Multi-Sig).",
            "greeting": "Avuxeni/Ahee! Hi mina Mufamadi AI, mupfuni wa n'wina wa swa timali eka R.C.C Stokvel. Ndzi nga mi pfuna yini?",
            "default": "Inkomu hi xivutiso xa n'wina. Hi kombela mi langutisa swiyimo swa n'wina swa timali kumbe mi tihlanganisa na mufambisi."
        },
        "English": {
            "balance": "Your current ledger balance with R.C.C Stokvel is: balance_placeholder. Thank you!",
            "deposit": "To make a deposit, perform an Instant EFT to the group bank account using your unique phone number as reference.",
            "withdrawal": "Withdrawals require multi-signature authentication (2-of-3 consensus) from group executive members.",
            "greeting": "Hello! I am Mufamadi AI, your dedicated financial assistant for R.C.C Stokvel. How may I assist you today?",
            "default": "Thank you for reaching out. Please check your dashboard or consult your group treasurer for detailed reports."
        }
    }

    lang_dict = responses.get(language, responses["English"])

    if any(w in prompt_lower for w in ["hi", "hello", "ndaa", "aa", "thobela", "avuxeni"]):
        return lang_dict["greeting"]
    elif any(w in prompt_lower for w in ["balance", "tshelede", "mali", "tšhelete", "how much"]):
        return lang_dict["balance"]
    elif any(w in prompt_lower for w in ["deposit", "contribute", "pay", "vhea", "hoxa", "pea"]):
        return lang_dict["deposit"]
    elif any(w in prompt_lower for w in ["withdraw", "bvisa", "ntšha", "humesa", "payout"]):
        return lang_dict["withdrawal"]
    else:
        return lang_dict["default"]


# ==============================================================================
# 4. APPLICATION UI LAYOUT & SIDEBAR NAVIGATION
# ==============================================================================

# Header Section
st.markdown("""
    <div class="venda-header">
        <h1>Rendani Community Capital (R.C.C)</h1>
        <p>🔒 Secure Stokvel Management System • Multi-Sig Governance • Mufamadi AI Engine</p>
    </div>
""", unsafe_allow_html=True)

# User Session Context
conn = get_db_connection()
users_df = pd.read_sql_query("SELECT id, full_name, role FROM users", conn)
groups_df = pd.read_sql_query("SELECT id, group_name FROM groups", conn)
conn.close()

st.sidebar.image("https://img.icons8.com/color/96/000000/shield-with-sign-top-right.png", width=64)
st.sidebar.title("R.C.C Navigation")

# Active User Selection
selected_user_id = st.sidebar.selectbox(
    "👤 Select Active User",
    options=users_df["id"].tolist(),
    format_func=lambda x: f"{users_df[users_df['id'] == x]['full_name'].values[0]} ({users_df[users_df['id'] == x]['role'].values[0]})"
)

# Navigation Menu
nav_choice = st.sidebar.radio(
    "Go to Module:",
    [
        "📊 Overview & Dashboard",
        "👥 Member Portal & Receipts",
        "🔑 Treasurer Multi-Sig Hub",
        "🤖 Mufamadi AI Assistant",
        "📈 Financial Growth Simulator",
        "📜 Transaction Audit Log"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Fully optimized for mobile screens and Android WebView/PWA wrappers.")


# ==============================================================================
# MODULE 1: OVERVIEW & DASHBOARD
# ==============================================================================
if nav_choice == "📊 Overview & Dashboard":
    st.subheader("🏛️ High-Level Financial Overview")

    conn = get_db_connection()
    total_savings = conn.execute("SELECT SUM(balance) FROM users").fetchone()[0] or 0.0
    group_pool = conn.execute("SELECT SUM(pool_balance) FROM groups").fetchone()[0] or 0.0
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    pending_withdrawals = conn.execute("SELECT COUNT(*) FROM pending_approvals WHERE status='Pending'").fetchone()[0]
    conn.close()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="metric-card gold">
                <div class="metric-title">Total Pool Savings</div>
                <div class="metric-value">R {group_pool:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card navy">
                <div class="metric-title">Individual Balances</div>
                <div class="metric-value">R {total_savings:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Active Stokvel Members</div>
                <div class="metric-value">{total_users}</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="metric-card gold">
                <div class="metric-title">Pending Multi-Sig Req</div>
                <div class="metric-value">{pending_withdrawals}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📋 Group Performance & Ledger")
    conn = get_db_connection()
    df_users = pd.read_sql_query("SELECT full_name, phone, role, balance, preferred_language FROM users", conn)
    conn.close()

    st.dataframe(df_users, use_container_width=True)


# ==============================================================================
# MODULE 2: MEMBER PORTAL & INSTANT RECEIPT SIMULATOR
# ==============================================================================
elif nav_choice == "👥 Member Portal & Receipts":
    st.subheader("💳 Member Actions & Digital Receipts")

    conn = get_db_connection()
    user_data = conn.execute("SELECT * FROM users WHERE id = ?", (selected_user_id,)).fetchone()
    conn.close()

    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown(f"### Welcome, **{user_data['full_name']}**")
        st.write(f"**Role:** `{user_data['role']}` | **Current Balance:** `R {user_data['balance']:,.2f}`")

        st.markdown("#### 📥 Perform Contribution Deposit")
        deposit_amount = st.number_input("Deposit Amount (ZAR)", min_value=50.0, value=500.0, step=50.0)
        ref_note = st.text_input("Reference/Note", f"CONT-{user_data['full_name'].split()[0].upper()}")

        if st.button("Submit Instant Deposit"):
            log_transaction(selected_user_id, 1, deposit_amount, "Contribution", ref_note)
            st.success(f"Deposit of R {deposit_amount:,.2f} recorded successfully!")
            st.rerun()

    with col_b:
        st.markdown("### 📲 Instant WhatsApp / SMS Receipt Simulator")
        st.caption("Simulated real-time automated message generated for mobile confirmation.")

        conn = get_db_connection()
        latest_tx = conn.execute("""
            SELECT * FROM transactions 
            WHERE user_id = ? 
            ORDER BY timestamp DESC LIMIT 1
        """, (selected_user_id,)).fetchone()
        conn.close()

        if latest_tx:
            now_str = datetime.datetime.now().strftime("%H:%M")
            tx_time = latest_tx['timestamp']
            
            st.markdown(f"""
                <div class="whatsapp-box">
                    <div style="font-weight: bold; color: #075E54; margin-bottom: 8px;">🟢 R.C.C Notification Bot</div>
                    <div class="whatsapp-bubble">
                        <b>R.C.C STOKVEL RECEIPT</b><br/>
                        ----------------------------------<br/>
                        <b>Member:</b> {user_data['full_name']}<br/>
                        <b>Type:</b> {latest_tx['transaction_type']}<br/>
                        <b>Amount:</b> R {latest_tx['amount']:,.2f}<br/>
                        <b>Ref:</b> {latest_tx['reference']}<br/>
                        <b>Status:</b> SUCCESSFUL ✅<br/>
                        <b>Timestamp:</b> {tx_time}<br/>
                        ----------------------------------<br/>
                        <i>Ndaa! Thank you for strengthening our community capital.</i>
                        <div class="whatsapp-time">{now_str} ✓✓</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No recent transaction history found for receipt preview.")


# ==============================================================================
# MODULE 3: TREASURER MULTI-SIG HUB
# ==============================================================================
elif nav_choice == "🔑 Treasurer Multi-Sig Hub":
    st.subheader("🛡️ Executive Multi-Sig Governance Engine")
    st.info("🔒 Security Protocol: Large fund distributions require a 2-of-3 or 3-of-3 threshold consensus before funds are unlocked from SQLite records.")

    conn = get_db_connection()
    pending_df = pd.read_sql_query("""
        SELECT p.id, p.amount, p.recipient_info, p.signatures_required, p.signatures_count, 
               p.signed_by_json, p.status, u.full_name as requested_by_name
        FROM pending_approvals p
        JOIN users u ON p.requested_by = u.id
        WHERE p.status = 'Pending'
    """, conn)
    conn.close()

    st.markdown("### ⏳ Active Withdrawal Authorization Requests")

    if pending_df.empty:
        st.success("No pending withdrawal approvals requiring executive signature.")
    else:
        for idx, row in pending_df.iterrows():
            with st.expander(f"REQ-00{row['id']}: Payout R {row['amount']:,.2f} - {row['recipient_info']}", expanded=True):
                col1, col2 = st.columns([2, 1])

                signed_by = json.loads(row['signed_by_json'])
                
                with col1:
                    st.write(f"**Requested By:** {row['requested_by_name']}")
                    st.write(f"**Purpose / Recipient:** {row['recipient_info']}")
                    st.write(f"**Signatures Collected:** `{row['signatures_count']} of {row['signatures_required']}`")
                    st.progress(row['signatures_count'] / row['signatures_required'])

                with col2:
                    if selected_user_id in signed_by:
                        st.warning("⚠️ You have already signed this transaction.")
                    else:
                        if st.button(f"✍️ Sign & Approve Request #{row['id']}", key=f"sig_{row['id']}"):
                            signed_by.append(selected_user_id)
                            new_count = row['signatures_count'] + 1
                            new_status = 'Approved' if new_count >= row['signatures_required'] else 'Pending'

                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("""
                                UPDATE pending_approvals 
                                SET signatures_count = ?, signed_by_json = ?, status = ?
                                WHERE id = ?
                            """, (new_count, json.dumps(signed_by), new_status, row['id']))

                            if new_status == 'Approved':
                                # Deduct from pool balance
                                cursor.execute("UPDATE groups SET pool_balance = pool_balance - ? WHERE id = 1", (row['amount'],))
                                cursor.execute("""
                                    INSERT INTO transactions (user_id, group_id, amount, transaction_type, status, reference)
                                    VALUES (?, 1, ?, 'Withdrawal', 'Completed', ?)
                                """, (selected_user_id, row['amount'], f"MULTISIG-APPROVED-{row['id']}"))

                            conn.commit()
                            conn.close()

                            st.success("Signature appended!")
                            st.rerun()

    st.markdown("---")
    st.markdown("### ➕ Initiate New Multi-Sig Withdrawal Request")
    with st.form("new_multisig_form"):
        req_amount = st.number_input("Request Amount (ZAR)", min_value=100.0, step=500.0)
        recipient = st.text_input("Recipient Account Details / Purpose")
        req_sigs = st.slider("Required Signature Threshold", min_value=2, max_value=3, value=2)

        submit_req = st.form_submit_button("Initiate Request")
        if submit_req:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO pending_approvals (group_id, requested_by, amount, recipient_info, signatures_required, signatures_count, signed_by_json)
                VALUES (1, ?, ?, ?, ?, 1, ?)
            """, (selected_user_id, req_amount, recipient, req_sigs, json.dumps([selected_user_id])))
            conn.commit()
            conn.close()
            st.success("New Multi-Sig transaction successfully broadcasted for approvals!")
            st.rerun()


# ==============================================================================
# MODULE 4: MULTI-LINGUAL MUFAMADI AI ASSISTANT
# ==============================================================================
elif nav_choice == "🤖 Mufamadi AI Assistant":
    st.subheader("🤖 Mufamadi AI - Intelligent Stokvel Advisor")
    st.caption("Supporting indigenous South African languages: Tshivenḓa, Sepedi, Xitsonga, and English.")

    # Select Language Mode
    col_lang, _ = st.columns([1, 2])
    with col_lang:
        selected_lang = st.selectbox("🌐 Select AI Assistant Language", ["Tshivenḓa", "Sepedi", "Xitsonga", "English"])

    # Chat Session State Setup
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display existing chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user interaction
    if prompt := st.chat_input("Ask Mufamadi AI (e.g., 'What is my balance?' or 'Ndi ṱoḓa u bvisa tshelede')"):
        # User message display
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        conn = get_db_connection()
        user_bal = conn.execute("SELECT balance FROM users WHERE id = ?", (selected_user_id,)).fetchone()[0]
        conn.close()

        raw_response = get_mufamadi_response(prompt, selected_lang)
        final_response = raw_response.replace("balance_placeholder", f"R {user_bal:,.2f}")

        # Assistant response display
        with st.chat_message("assistant"):
            st.markdown(final_response)
        st.session_state.messages.append({"role": "assistant", "content": final_response})


# ==============================================================================
# MODULE 5: FINANCIAL MONETIZATION & GROWTH SIMULATOR
# ==============================================================================
elif nav_choice == "📈 Financial Growth Simulator":
    st.subheader("📊 Financial Monetization & Scalability Engine")
    st.write("Simulate platform ecosystem revenue growth, SaaS subscription margins, and tax projections across South African Stokvel markets.")

    col_sim_1, col_sim_2 = st.columns([1, 2])

    with col_sim_1:
        st.markdown("#### ⚙️ Simulation Parameters")
        user_scale = st.slider("Active Platform Users", min_value=500, max_value=10000, value=2500, step=500)
        sub_fee = st.number_input("Monthly Platform Fee per User (ZAR)", value=25.0, step=5.0)
        loan_volume_per_user = st.number_input("Avg Micro-Loan Volume / User / Yr", value=1200.0, step=100.0)
        loan_interest_margin = st.slider("Platform Micro-Loan Interest Rate (%)", min_value=2.0, max_value=15.0, value=5.0) / 100.0
        tax_rate = 0.27 # SA Corporate Tax Rate (27%)

    with col_sim_2:
        # Business Logic calculations
        annual_sub_revenue = user_scale * sub_fee * 12
        total_loan_book = user_scale * loan_volume_per_user
        annual_loan_revenue = total_loan_book * loan_interest_margin
        gross_revenue = annual_sub_revenue + annual_loan_revenue

        estimated_opex = gross_revenue * 0.35 # 35% operational costs (hosting, banking APIs, SMS)
        taxable_income = gross_revenue - estimated_opex
        estimated_tax = taxable_income * tax_rate
        net_profit = taxable_income - estimated_tax

        st.markdown("#### 📈 Pro-Forma Annual Financial Model")

        m1, m2, m3 = st.columns(3)
        m1.metric("Gross Revenue", f"R {gross_revenue:,.2f}")
        m2.metric("Corporate Tax (27%)", f"R {estimated_tax:,.2f}")
        m3.metric("Net Profit Margin", f"R {net_profit:,.2f}")

        # Visualization Chart Data
        months = [f"Month {i}" for i in range(1, 13)]
        revenue_curve = [(gross_revenue / 12) * (1 + (i * 0.05)) for i in range(12)]
        profit_curve = [(net_profit / 12) * (1 + (i * 0.05)) for i in range(12)]

        chart_df = pd.DataFrame({
            "Month": months,
            "Monthly Gross Revenue": revenue_curve,
            "Monthly Net Profit": profit_curve
        }).set_index("Month")

        st.line_chart(chart_df)

    st.markdown("---")
    st.markdown("#### 💡 Monetization Breakdown Breakdown")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.write(f"- **SaaS Subscription Revenue:** R {annual_sub_revenue:,.2f} / yr")
        st.write(f"- **Micro-Lending Margin Revenue:** R {annual_loan_revenue:,.2f} / yr")
    with col_b2:
        st.write(f"- **Estimated Infrastructure/OPEX:** R {estimated_opex:,.2f} / yr")
        st.write(f"- **Effective SA Tax Contribution:** R {estimated_tax:,.2f} / yr")


# ==============================================================================
# MODULE 6: TRANSACTION AUDIT LOG
# ==============================================================================
elif nav_choice == "📜 Transaction Audit Log":
    st.subheader("📜 Real-Time SQLite Ledger & Audit Trail")

    conn = get_db_connection()
    logs_df = pd.read_sql_query("""
        SELECT t.id, u.full_name as member_name, g.group_name, t.amount, 
               t.transaction_type, t.status, t.timestamp, t.reference
        FROM transactions t
        JOIN users u ON t.user_id = u.id
        JOIN groups g ON t.group_id = g.id
        ORDER BY t.timestamp DESC
    """, conn)
    conn.close()

    st.dataframe(logs_df, use_container_width=True)

    # Export CSV feature
    csv_data = logs_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Ledger to CSV (Auditor Format)",
        data=csv_data,
        file_name="RCC_Stokvel_Audit_Ledger.csv",
        mime="text/csv"
    )