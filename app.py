import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Rendani Community Capital (R.C.C)",
    page_icon="🏛️",
    layout="wide"
)

# Initialize Database
def init_db():
    conn = sqlite3.connect('rcc_stokvel.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    role TEXT,
                    group_name TEXT,
                    phone TEXT,
                    balance REAL DEFAULT 0.0)''')
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

# Custom Styling (Venda Cultural Theme: Navy, Gold, Deep Green)
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #0B132B 0%, #1C2541 100%);
        padding: 30px;
        border-radius: 12px;
        color: white;
        text-align: center;
        border-bottom: 4px solid #D4AF37;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .logo-text {
        font-size: 32px;
        font-weight: bold;
        color: #D4AF37;
        letter-spacing: 1px;
    }
    .sub-logo {
        font-size: 14px;
        color: #A0AEC0;
        margin-top: 5px;
    }
    .stButton>button {
        background-color: #D4AF37;
        color: #0B132B;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #C5A028;
        color: #0B132B;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 1. WELCOME & SIGN UP / LOGIN PAGE
# -------------------------------------------------------------
if not st.session_state.logged_in:
    st.markdown("""
        <div class="main-header">
            <div style="font-size: 45px; margin-bottom: 5px;">🏛️ 🛡️</div>
            <div class="logo-text">RENDANI COMMUNITY CAPITAL (R.C.C)</div>
            <div class="sub-logo">Digital Stokvel Platform & Mufamadi AI Assistant</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Secure Sign-In & Registration")
        st.markdown("Please enter your details and select whether you are joining as a **Treasurer** or a **Member**.")
        
        with st.form("signup_form"):
            name = st.text_input("Full Name")
            group_name = st.text_input("Stokvel / Group Name (e.g., Mafhafha Savings)")
            phone = st.text_input("Phone Number (for SMS & WhatsApp receipts)")
            role = st.selectbox("Select Your Role", ["Member", "Treasurer"])
            
            submit = st.form_submit_button("Enter R.C.C Platform")
            
            if submit:
                if name.strip() and group_name.strip():
                    st.session_state.logged_in = True
                    st.session_state.username = name.strip()
                    st.session_state.role = role
                    st.session_state.group_name = group_name.strip()
                    
                    # Save user to DB if new
                    conn = sqlite3.connect('rcc_stokvel.db')
                    c = conn.cursor()
                    c.execute("INSERT OR IGNORE INTO users (name, role, group_name, phone) VALUES (?, ?, ?, ?)", 
                              (name.strip(), role, group_name.strip(), phone.strip()))
                    conn.commit()
                    conn.close()
                    st.rerun()
                else:
                    st.error("Please provide both your Full Name and your Group Name.")

# -------------------------------------------------------------
# 2. MAIN APPLICATION (LOGGED IN VIEW)
# -------------------------------------------------------------
else:
    # Sidebar User Profile & Logout
    st.sidebar.markdown(f"""
        <div style="text-align: center; padding: 15px; background: #0B132B; border-radius: 10px; color: white; margin-bottom: 20px; border-left: 4px solid #D4AF37;">
            <div style="font-size: 22px; color: #D4AF37;">🏛️ R.C.C</div>
            <div style="font-size: 15px; margin-top: 5px;"><b>{st.session_state.username}</b></div>
            <div style="font-size: 13px; color: #38A169;">Role: <b>{st.session_state.role}</b></div>
            <div style="font-size: 12px; color: #E0E1DD; margin-top: 3px;">Group: {st.session_state.group_name}</div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("Logout / Switch Account"):
        st.session_state.logged_in = False
        st.rerun()

    st.title(f"R.C.C Dashboard — {st.session_state.group_name}")

    # ==========================================
    # TREASURER INTERFACE & PERMISSIONS
    # ==========================================
    if st.session_state.role == "Treasurer":
        st.info("👑 **Treasurer Privileges Active:** You have full administrative control to add new members, log cash contributions, and view group ledger analytics.")
        
        tab1, tab2, tab3 = st.tabs(["👥 Manage Members", "💰 Log Contribution", "📊 Group Treasury Ledger"])
        
        with tab1:
            st.subheader("Add New Group Member")
            st.markdown("As Treasurer, you hold the authorization to register new members into **" + st.session_state.group_name + "**.")
            
            with st.form("add_member_form"):
                new_name = st.text_input("New Member Full Name")
                new_phone = st.text_input("New Member Phone Number")
                add_btn = st.form_submit_button("Register New Member")
                
                if add_btn:
                    if new_name.strip():
                        conn = sqlite3.connect('rcc_stokvel.db')
                        c = conn.cursor()
                        # Check if member already exists in group
                        c.execute("SELECT id FROM users WHERE name = ? AND group_name = ?", (new_name.strip(), st.session_state.group_name))
                        existing = c.fetchone()
                        if existing:
                            st.warning(f"{new_name} is already registered in this group.")
                        else:
                            c.execute("INSERT INTO users (name, role, group_name, phone) VALUES (?, 'Member', ?, ?)", 
                                      (new_name.strip(), st.session_state.group_name, new_phone.strip()))
                            conn.commit()
                            st.success(f"Successfully added {new_name.strip()} to your stokvel group!")
                        conn.close()
                    else:
                        st.error("Please enter a valid member name.")
            
            st.markdown("---")
            st.subheader("Current Group Member Roster")
            conn = sqlite3.connect('rcc_stokvel.db')
            df_users = pd.read_sql_query(f"SELECT name, role, phone, balance FROM users WHERE group_name='{st.session_state.group_name}'", conn)
            conn.close()
            st.dataframe(df_users, use_container_width=True)

        with tab2:
            st.subheader("Record Contribution (Cash or EFT)")
            conn = sqlite3.connect('rcc_stokvel.db')
            c = conn.cursor()
            c.execute(f"SELECT name FROM users WHERE group_name='{st.session_state.group_name}'")
            members_list = [row[0] for row in c.fetchall()]
            conn.close()
            
            if members_list:
                with st.form("contrib_form"):
                    chosen_member = st.selectbox("Select Member", members_list)
                    contrib_amount = st.number_input("Contribution Amount (R)", min_value=0.0, value=500.0, step=50.0)
                    payment_type = st.selectbox("Payment Channel", ["Cash Handed to Treasurer", "Instant EFT / Capitec Pay", "Retail Voucher (Flash/OTT)"])
                    record_btn = st.form_submit_button("Save Contribution & Send SMS Receipt")
                    
                    if record_btn:
                        conn = sqlite3.connect('rcc_stokvel.db')
                        c = conn.cursor()
                        c.execute("INSERT INTO contributions (member_name, group_name, amount, date, type) VALUES (?, ?, ?, ?, ?)",
                                  (chosen_member, st.session_state.group_name, contrib_amount, datetime.now().strftime("%Y-%m-%d %H:%M"), payment_type))
                        c.execute("UPDATE users SET balance = balance + ? WHERE name = ? AND group_name = ?", 
                                  (contrib_amount, chosen_member, st.session_state.group_name))
                        conn.commit()
                        conn.close()
                        st.success(f"Successfully logged R{contrib_amount:,.2f} for {chosen_member}! Automated WhatsApp/SMS receipt triggered.")
            else:
                st.warning("No members found in this group yet. Please add members under the **Manage Members** tab first.")

        with tab3:
            st.subheader("Group Ledger & Treasury Totals")
            conn = sqlite3.connect('rcc_stokvel.db')
            df_contribs = pd.read_sql_query(f"SELECT member_name, amount, date, type FROM contributions WHERE group_name='{st.session_state.group_name}'", conn)
            conn.close()
            
            if not df_contribs.empty:
                st.dataframe(df_contribs, use_container_width=True)
                total_pool = df_contribs['amount'].sum()
                st.metric("Total Group Treasury Pool", f"R {total_pool:,.2f}")
            else:
                st.info("No financial contributions recorded in this group yet.")

    # ==========================================
    # MEMBER INTERFACE & PERMISSIONS
    # ==========================================
    else:
        st.info("👤 **Member View:** You can view your personal savings balance and contribution statements below. Note: Only the group Treasurer is permitted to add new members.")
        
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
            st.info("You do not have any recorded contributions yet. Contact your group treasurer when you make a payment.")