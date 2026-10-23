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

# Initialize Database with Self-Healing Error Handling
def init_db():
    try:
        conn = sqlite3.connect('rcc_stokvel.db')
        c = conn.cursor()
        
        # Users Table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        role TEXT,
                        group_name TEXT,
                        phone TEXT,
                        gender TEXT,
                        status TEXT DEFAULT 'Approved',
                        balance REAL DEFAULT 0.0)''')
        
        # Groups Table (Stores group settings defined by Treasurer)
        c.execute('''CREATE TABLE IF NOT EXISTS groups (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        group_name TEXT UNIQUE,
                        monthly_contrib REAL,
                        active_months INTEGER,
                        treasurer_name TEXT)''')

        # Contributions Table
        c.execute('''CREATE TABLE IF NOT EXISTS contributions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        member_name TEXT,
                        group_name TEXT,
                        amount REAL,
                        date TEXT,
                        type TEXT)''')
        
        conn.commit()

        # Create 2 Test Profiles for Easy Testing
        c.execute("SELECT id FROM users WHERE name = ? AND group_name = ?", ("Rendani Mufamadi", "Mufamadi"))
        if not c.fetchone():
            c.execute("INSERT INTO users (name, role, group_name, phone, gender, status, balance) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      ("Rendani Mufamadi", "Treasurer", "Mufamadi", "0637037295", "Male", "Approved", 0.0))
            c.execute("INSERT OR IGNORE INTO groups (group_name, monthly_contrib, active_months, treasurer_name) VALUES (?, ?, ?, ?)",
                      ("Mufamadi", 500.0, 12, "Rendani Mufamadi"))

        c.execute("SELECT id FROM users WHERE name = ? AND group_name = ?", ("Test Member", "Mufamadi"))
        if not c.fetchone():
            c.execute("INSERT INTO users (name, role, group_name, phone, gender, status, balance) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      ("Test Member", "Member", "Mufamadi", "0720000000", "Female", "Approved", 500.0))
            c.execute("INSERT INTO contributions (member_name, group_name, amount, date, type) VALUES (?, ?, ?, ?, ?)",
                      ("Test Member", "Mufamadi", 500.0, datetime.now().strftime("%Y-%m-%d %H:%M"), "Instant EFT"))

        conn.commit()
        conn.close()
    except Exception as e:
        if os.path.exists('rcc_stokvel.db'):
            os.remove('rcc_stokvel.db')
        init_db()

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
    if os.path.exists("logo.jpg"):
        col_l, col_c, col_r = st.columns([1, 2, 1])
        with col_c:
            st.image("logo.jpg", use_column_width=True)
            
    st.markdown('<div class="main-title">CREATE YOUR ACCOUNT</div>', unsafe_allow_html=True)
    st.markdown('<div class="venda-stripes"></div>', unsafe_allow_html=True)
    
    tab_signup, tab_login = st.tabs(["📝 Self Register / New Group", "🔑 Existing Login (Test Profiles)"])
    
    with tab_signup:
        st.markdown("### Sign Up (Members & New Treasurers)")
        with st.form("signup_form"):
            name = st.text_input("Full Name")
            phone = st.text_input("Phone Number")
            role = st.selectbox("Select Role", ["Member", "Treasurer"])
            gender = st.selectbox("Select Gender", ["Male", "Female"])
            
            group_name = st.text_input("Stokvel Group Name (e.g., Mufamadi)")
            
            st.markdown("---")
            st.markdown("#### ⚙️ Stokvel Cycle Setup (Treasurer Only)")
            monthly_contrib = st.number_input("Monthly Contribution Amount (R)", min_value=0.0, value=500.0, step=50.0)
            active_months = st.number_input("Number of Active Months in Cycle", min_value=1, max_value=60, value=12)
            
            signup_btn = st.form_submit_button("SIGN UP")
            
            if signup_btn:
                if name.strip() and group_name.strip():
                    conn = sqlite3.connect('rcc_stokvel.db')
                    c = conn.cursor()
                    
                    initial_status = 'Approved' if role == 'Treasurer' else 'Pending'
                    
                    c.execute("INSERT INTO users (name, role, group_name, phone, gender, status) VALUES (?, ?, ?, ?, ?, ?)", 
                              (name.strip(), role, group_name.strip(), phone.strip(), gender, initial_status))
                    
                    if role == 'Treasurer':
                        c.execute("INSERT OR REPLACE INTO groups (group_name, monthly_contrib, active_months, treasurer_name) VALUES (?, ?, ?, ?)",
                                  (group_name.strip(), monthly_contrib, active_months, name.strip()))
                        
                    conn.commit()
                    conn.close()
                    
                    if role == 'Treasurer':
                        st.session_state.logged_in = True
                        st.session_state.username = name.strip()
                        st.session_state.role = role
                        st.session_state.group_name = group_name.strip()
                        st.success("Treasurer account and Stokvel group created successfully! Entering dashboard...")
                        st.rerun()
                    else:
                        st.success("Registration submitted! Your account is **Pending** Treasurer approval.")
                else:
                    st.error("Please enter your Full Name and Group Name.")

    with tab_login:
        st.markdown("### Quick Test Login or Standard Sign In")
        st.info("💡 **Test Profiles Available:**\n* **Treasurer:** Rendani Mufamadi (Group: Mufamadi)\n* **Member:** Test Member (Group: Mufamadi)")
        
        with st.form("login_form"):
            login_name = st.text_input("Registered Full Name", value="Rendani Mufamadi")
            login_group = st.text_input("Stokvel Group Name", value="Mufamadi")
            login_role = st.selectbox("Select Role", ["Treasurer", "Member"])
            login_btn = st.form_submit_button("LOG IN")
            
            if login_btn:
                conn = sqlite3.connect('rcc_stokvel.db')
                c = conn.cursor()
                c.execute("SELECT role, status FROM users WHERE name = ? AND group_name = ? AND role = ?", (login_name.strip(), login_group.strip(), login_role))
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
                    st.error("Account not found or role does not match. Please check your details.")

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

    conn = sqlite3.connect('rcc_stokvel.db')
    c = conn.cursor()
    c.execute("SELECT monthly_contrib, active_months FROM groups WHERE group_name = ?", (st.session_state.group_name,))
    group_settings = c.fetchone()
    
    monthly_contrib = group_settings[0] if group_settings and group_settings[0] else 500.0
    active_months = group_settings[1] if group_settings and group_settings[1] else 12

    c.execute("SELECT COUNT(*) FROM users WHERE group_name = ? AND status = 'Approved'", (st.session_state.group_name,))
    approved_members_count = c.fetchone()[0]
    conn.close()

    projected_total_pool = approved_members_count * monthly_contrib * active_months

    # ==========================================
    # TREASURER INTERFACE & PERMISSIONS
    # ==========================================
    if st.session_state.role == "Treasurer":
        st.info(f"👑 **Treasurer Control Center:** Group target set to **{active_months} months** at **R{monthly_contrib:,.2f}** per month.")
        
        col_p1, col_p2, col_p3 = st.columns(3)
        col_p1.metric("Active Members", approved_members_count)
        col_p2.metric("Monthly Target Pool", f"R {approved_members_count * monthly_contrib:,.2f}")
        col_p3.metric("Projected Payout at Cycle End", f"R {projected_total_pool:,.2f}", f"{active_months} Months Duration")
        
        st.markdown("---")
        
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
                    contrib_amount = st.number_input("Contribution Amount (R)", min_value=0.0, value=monthly_contrib, step=50.0)
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
                st.metric("Total Collected Treasury Pool so Far", f"R {total_pool:,.2f}")
            else:
                st.info("No financial contributions recorded yet.")

    # ==========================================
    # MEMBER INTERFACE & PERMISSIONS
    # ==========================================
    else:
        st.info(f"👤 **Member Portal:** Cycle duration: **{active_months} months** | Monthly Target: **R{monthly_contrib:,.2f}**")
        
        conn = sqlite3.connect('rcc_stokvel.db')
        c = conn.cursor()
        c.execute("SELECT balance FROM users WHERE name = ? AND group_name = ?", (st.session_state.username, st.session_state.group_name))
        res = c.fetchone()
        my_balance = res[0] if res else 0.0
        conn.close()
        
        col1, col2 = st.columns(2)
        col1.metric("My Total Saved Contributions", f"R {my_balance:,.2f}")
        col2.metric("Projected Group Payout at Term End", f"R {projected_total_pool:,.2f}")
        
        st.markdown("---")
        st.subheader("My Contribution Statement")
        conn = sqlite3.connect('rcc_stokvel.db')
        df_my_contribs = pd.read_sql_query(f"SELECT amount, date, type FROM contributions WHERE member_name='{st.session_state.username}' AND group_name='{st.session_state.group_name}'", conn)
        conn.close()
        
        if not df_my_contribs.empty:
            st.dataframe(df_my_contribs, use_container_width=True)
        else:
            st.info("You do not have any recorded contributions yet.")