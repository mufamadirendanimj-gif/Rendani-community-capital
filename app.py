import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# Page Configuration
st.set_page_config(
    page_title="Rendani Community Capital (R.C.C)",
    page_icon="🏛️",
    layout="centered"
)

# Initialize Database with safe column updates
def init_db():
    conn = sqlite3.connect('rcc_stokvel.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    role TEXT,
                    group_name TEXT,
                    phone TEXT,
                    gender TEXT,
                    status TEXT DEFAULT 'Approved',
                    balance REAL DEFAULT 0.0)''')
    
    # Check if status or gender columns exist in older DB versions, add if missing
    try:
        c.execute("ALTER TABLE users ADD COLUMN gender TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'Approved'")
    except sqlite3.OperationalError:
        pass

    c.execute('''CREATE TABLE IF NOT EXISTS contributions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_name TEXT,
                    group_name TEXT,
                    amount REAL,
                    date TEXT,
                    type TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Session State Initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    st.session_state.group_name = None

# Custom Venda Theme Styling (Deep Blue & Traditional Stripes)
st.markdown("""
    <style>
    .stApp {
        background-color: #0A1931;
        color: #FFFFFF;
    }
    .venda-stripes {
        height: 10px;
        background: linear-gradient(90deg, #006633 0%, #006633 20%, #FFCC00 20%, #FFCC00 40%, #CC0000 40%, #CC0000 60%, #000000 60%, #000000 80%, #FFFFFF 80%, #FFFFFF 100%);
        border-radius: 4px;
        margin: 15px 0;
    }
    .main-title {
        text-align: center;
        font-size: 28px;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #1C3144 0%, #0A1931 100%);
        color: #FFFFFF;
        font-weight: bold;
        border-radius: 12px;
        border: 2px solid #D4AF37;
        padding: 12px 20px;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #D4AF37;
        color: #0A1931;
        border-color: #FFFFFF;
    }
    .stTextInput>div>div>input {
        background-color: #172A45;
        color: white;
        border-radius: 8px;
        border: 1px solid #303C55;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 1. WELCOME & SIGN UP / LOGIN PAGE
# -------------------------------------------------------------
if not st.session_state.logged_in:
    # Display Logo if available
    if os.path.exists("logo.jpg"):
        col_l, col_c, col_r = st.columns([1, 2, 1])
        with col_c:
            st.image("logo.jpg", use_column_width=True)
            
    st.markdown('<div class="main-title">CREATE YOUR ACCOUNT</div>', unsafe_allow_html=True)
    st.markdown('<div class="venda-stripes"></div>', unsafe_allow_html=True)
    
    tab_signup, tab_login = st.tabs(["📝 Self Register (Needs Approval)", "🔑 Treasurer / Existing Login"])
    
    with tab_signup:
        st.markdown("### Member & Treasurer Registration")
        with st.form("signup_form"):
            name = st.text_input("Full Name")
            group_name = st.text_input("Stokvel / Group Name (e.g., Mafhafha Savings)")
            phone = st.text_input("Phone Number")
            role = st.selectbox("Select Role", ["Member", "Treasurer"])
            gender = st.selectbox("Select Gender", ["Male", "Female"])
            
            signup_btn = st.form_submit_button("SIGN UP")
            
            if signup_btn:
                if name.strip() and group_name.strip():
                    conn = sqlite3.connect('rcc_stokvel.db')
                    c = conn.cursor()
                    
                    # Treasurers are auto-approved, Self-registered members start as 'Pending'
                    initial_status = 'Approved' if role == 'Treasurer' else 'Pending'
                    
                    c.execute("INSERT INTO users (name, role, group_name, phone, gender, status) VALUES (?, ?, ?, ?, ?, ?)", 
                              (name.strip(), role, group_name.strip(), phone.strip(), gender, initial_status))
                    conn.commit()
                    conn.close()
                    
                    if role == 'Treasurer':
                        st.session_state.logged_in = True
                        st.session_state.username = name.strip()
                        st.session_state.role = role
                        st.session_state.group_name = group_name.strip()
                        st.success("Treasurer account created successfully! Entering dashboard...")
                        st.rerun()
                    else:
                        st.success("Registration submitted! Your account is **Pending** group Treasurer approval. You can log in once approved.")
                else:
                    st.error("Please enter your Full Name and Group Name.")

    with tab_login:
        st.markdown("### Sign In to Dashboard")
        with st.form("login_form"):
            login_name = st.text_input("Registered Full Name")
            login_group = st.text_input("Stokvel Group Name")
            login_btn = st.form_submit_button("LOG IN")
            
            if login_btn:
                conn = sqlite3.connect('rcc_stokvel.db')
                c = conn.cursor()
                c.execute("SELECT role, status FROM users WHERE name = ? AND group_name = ?", (login_name.strip(), login_group.strip()))
                user_record = c.fetchone()
                conn.close()
                
                if user_record:
                    db_role, db_status = user_record
                    if db_status == 'Approved':
                        st.session_state.logged_in = True
                        st.session_state.username = login_name.strip()
                        st.session_state.role = db_role
                        st.session_state.group_name = login_group.strip()
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.warning("⚠️ Your account is still **Pending** approval from your group Treasurer.")
                else:
                    st.error("Account not found. Please check your name and group name or sign up.")

# -------------------------------------------------------------
# 2. MAIN APPLICATION (LOGGED IN VIEW)
# -------------------------------------------------------------
else:
    st.sidebar.markdown(f"""
        <div style="text-align: center; padding: 15px; background: #172A45; border-radius: 10px; color: white; margin-bottom: 20px; border-left: 4px solid #D4AF37;">
            <div style="font-size: 20px; color: #D4AF37;">🏛️ R.C.C</div>
            <div style="font-size: 15px; margin-top: 5px;"><b>{st.session_state.username}</b></div>
            <div style="font-size: 13px; color: #48BB78;">Role: <b>{st.session_state.role}</b></div>
            <div style="font-size: 12px; color: #CBD5E0; margin-top: 3px;">Group: {st.session_state.group_name}</div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("Logout / Switch Account"):
        st.session_state.logged_in = False
        st.rerun()

    st.title(f"Dashboard — {st.session_state.group_name}")
    st.markdown('<div class="venda-stripes"></div>', unsafe_allow_html=True)

    # ==========================================
    # TREASURER INTERFACE & PERMISSIONS
    # ==========================================
    if st.session_state.role == "Treasurer":
        st.info("👑 **Treasurer Control Center:** Approve pending registrations, add members directly, and manage group funds.")
        
        tab1, tab2, tab3, tab4 = st.tabs(["⏳ Pending Approvals", "👥 Manage Members", "💰 Log Contribution", "📊 Treasury Ledger"])
        
        with tab1:
            st.subheader("Member Registration Requests")
            conn = sqlite3.connect('rcc_stokvel.db')
            df_pending = pd.read_sql_query(f"SELECT id, name, phone, gender FROM users WHERE group_name='{st.session_state.group_name}' AND status='Pending' AND role='Member'", conn)
            conn.close()
            
            if not df_pending.empty:
                for index, row in df_pending.iterrows():
                    col_info, col_btn = st.columns([3, 1])
                    col_info.write(f"**{row['name']}** ({row['gender']}) - Phone: {row['phone']}")
                    if col_btn.button("Approve", key=f"app_{row['id']}"):
                        conn = sqlite3.connect('rcc_stokvel.db')
                        c = conn.cursor()
                        c.execute("UPDATE users SET status='Approved' WHERE id=?", (row['id'],))
                        conn.commit()
                        conn.close()
                        st.success(f"Approved {row['name']}!")
                        st.rerun()
            else:
                st.info("No pending member registrations awaiting approval.")

        with tab2:
            st.subheader("Directly Add New Member")
            with st.form("add_member_form"):
                new_name = st.text_input("New Member Full Name")
                new_phone = st.text_input("New Member Phone Number")
                new_gender = st.selectbox("Gender", ["Male", "Female"], key="new_m_gender")
                add_btn = st.form_submit_button("Add Member (Auto-Approved)")
                
                if add_btn:
                    if new_name.strip():
                        conn = sqlite3.connect('rcc_stokvel.db')
                        c = conn.cursor()
                        c.execute("SELECT id FROM users WHERE name = ? AND group_name = ?", (new_name.strip(), st.session_state.group_name))
                        if c.fetchone():
                            st.warning(f"{new_name} already exists in this group.")
                        else:
                            c.execute("INSERT INTO users (name, role, group_name, phone, gender, status) VALUES (?, 'Member', ?, ?, ?, 'Approved')", 
                                      (new_name.strip(), st.session_state.group_name, new_phone.strip(), new_gender))
                            conn.commit()
                            st.success(f"Successfully added and approved {new_name.strip()}!")
                        conn.close()
                    else:
                        st.error("Please enter a valid name.")
            
            st.markdown("---")
            st.subheader("Approved Member Roster")
            conn = sqlite3.connect('rcc_stokvel.db')
            df_users = pd.read_sql_query(f"SELECT name, phone, gender, balance FROM users WHERE group_name='{st.session_state.group_name}' AND status='Approved'", conn)
            conn.close()
            st.dataframe(df_users, use_container_width=True)

        with tab3:
            st.subheader("Record Contribution")
            conn = sqlite3.connect('rcc_stokvel.db')
            c = conn.cursor()
            c.execute(f"SELECT name FROM users WHERE group_name='{st.session_state.group_name}' AND status='Approved'")
            members_list = [row[0] for row in c.fetchall()]
            conn.close()
            
            if members_list:
                with st.form("contrib_form"):
                    chosen_member = st.selectbox("Select Approved Member", members_list)
                    contrib_amount = st.number_input("Contribution Amount (R)", min_value=0.0, value=500.0, step=50.0)
                    payment_type = st.selectbox("Payment Channel", ["Cash to Treasurer", "Instant EFT / Capitec Pay", "Retail Voucher (Flash/OTT)"])
                    record_btn = st.form_submit_button("Save Contribution & Send Receipt")
                    
                    if record_btn:
                        conn = sqlite3.connect('rcc_stokvel.db')
                        c = conn.cursor()
                        c.execute("INSERT INTO contributions (member_name, group_name, amount, date, type) VALUES (?, ?, ?, ?, ?)",
                                  (chosen_member, st.session_state.group_name, contrib_amount, datetime.now().strftime("%Y-%m-%d %H:%M"), payment_type))
                        c.execute("UPDATE users SET balance = balance + ? WHERE name = ? AND group_name = ?", 
                                  (contrib_amount, chosen_member, st.session_state.group_name))
                        conn.commit()
                        conn.close()
                        st.success(f"Successfully logged R{contrib_amount:,.2f} for {chosen_member}!")
            else:
                st.warning("No approved members available in this group.")

        with tab4:
            st.subheader("Group Treasury Ledger")
            conn = sqlite3.connect('rcc_stokvel.db')
            df_contribs = pd.read_sql_query(f"SELECT member_name, amount, date, type FROM contributions WHERE group_name='{st.session_state.group_name}'", conn)
            conn.close()
            
            if not df_contribs.empty:
                st.dataframe(df_contribs, use_container_width=True)
                total_pool = df_contribs['amount'].sum()
                st.metric("Total Group Treasury Pool", f"R {total_pool:,.2f}")
            else:
                st.info("No financial contributions recorded yet.")

    # ==========================================
    # MEMBER INTERFACE & PERMISSIONS
    # ==========================================
    else:
        st.info("👤 **Member Portal:** View your personal savings and contribution statements below.")
        
        conn = sqlite3.connect('rcc_stokvel.db')
        c = conn.cursor()
        c.execute("SELECT balance FROM users WHERE name = ? AND group_name = ?", (st.session_state.username, st.session_state.group_name))
        res = c.fetchone()
        my_balance = res[0] if res else 0.0
        conn.close()
        
        col1, col2 = st.columns(2)
        col1.metric("My Total Saved Contributions", f"R {my_balance:,.2f}")
        col2.metric("Stokvel Group", st.session_state.group_name)
        
        st.markdown("---")
        st.subheader("My Contribution Statement")
        conn = sqlite3.connect('rcc_stokvel.db')
        df_my_contribs = pd.read_sql_query(f"SELECT amount, date, type FROM contributions WHERE member_name='{st.session_state.username}' AND group_name='{st.session_state.group_name}'", conn)
        conn.close()
        
        if not df_my_contribs.empty:
            st.dataframe(df_my_contribs, use_container_width=True)
        else:
            st.info("You do not have any recorded contributions yet.")