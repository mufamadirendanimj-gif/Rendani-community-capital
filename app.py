import os
import sqlite3
import streamlit as st

# ==========================================
# 1. PAGE CONFIGURATION & CULTURAL THEMING (CSS)
# ==========================================
st.set_page_config(
    page_title="Rendani Community Capital", page_icon="🏛️", layout="centered"
)

# Custom Venda Cultural Theme CSS
st.markdown(
    """
    <style>
    /* Hide Streamlit UI elements & badges */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QSob, .styles_viewerBadge__1yB5_, 
    [data-testid="stDecoration"], [data-testid="stStatusWidget"],
    .floating-badge, #webintoapp-badge, iframe[src*="webintoapp"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* Venda Pattern Header Border */
    .stAppViewContainer {
        border-top: 6px solid #D4AF37;
    }

    /* Styling Custom Tab Headers */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #1A1D20;
        border-radius: 8px 8px 0px 0px;
        color: #D4AF37;
        font-weight: bold;
        border: 1px solid #333;
    }
    .stTabs [aria-selected="true"] {
        background-color: #8B0000 !important;
        color: #FFFFFF !important;
        border-bottom: 3px solid #D4AF37 !important;
    }

    /* Culturally Styled Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #8B0000 0%, #B22222 100%);
        color: #FFFFFF;
        font-weight: bold;
        border-radius: 8px;
        border: 1px solid #D4AF37;
        padding: 0.6rem 1rem;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #D4AF37 0%, #FFD700 100%);
        color: #1A1D20;
        border: 1px solid #8B0000;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Display Custom R.C.C. Logo if present
if os.path.exists("logo.png"):
    st.image("logo.png", use_container_width=True)
elif os.path.exists("logo.jpg"):
    st.image("logo.jpg", use_container_width=True)
else:
    st.title("🏛️ Rendani Community Capital")

st.caption(" Powered by Mufamadi AI | R.C.C. Digital Finance")
st.divider()


# ==========================================
# 2. SAFE DATABASE SETUP & MIGRATION
# ==========================================
def init_db():
    conn = sqlite3.connect("rendani.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            pin TEXT DEFAULT '1234',
            gender TEXT DEFAULT 'Male',
            stokvel_balance REAL,
            loan_status TEXT,
            savings_goal REAL DEFAULT 10000.0
        )
    """)

    cursor.execute("PRAGMA table_info(members)")
    existing_columns = [column[1] for column in cursor.fetchall()]

    if "pin" not in existing_columns:
        cursor.execute("ALTER TABLE members ADD COLUMN pin TEXT DEFAULT '1234'")
    if "gender" not in existing_columns:
        cursor.execute(
            "ALTER TABLE members ADD COLUMN gender TEXT DEFAULT 'Male'"
        )

    cursor.execute("SELECT COUNT(*) FROM members")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO members (name, pin, gender, stokvel_balance, loan_status, savings_goal)
            VALUES ('Vho-Makhadzi', '1234', 'Female', 5400.0, 'Approved for R2,000 Micro-loan', 10000.0)
        """)
        cursor.execute("""
            INSERT INTO members (name, pin, gender, stokvel_balance, loan_status, savings_goal)
            VALUES ('Ndivhuwo M.', '1234', 'Male', 12000.0, 'Approved for R5,000 Business Loan', 15000.0)
        """)

    cursor.execute(
        "UPDATE members SET gender = 'Female' WHERE LOWER(name) LIKE '%makhadzi%'"
    )
    cursor.execute(
        "UPDATE members SET pin = '1234' WHERE pin IS NULL OR pin = ''"
    )

    conn.commit()
    conn.close()


init_db()


def authenticate_user(name, pin):
    conn = sqlite3.connect("rendani.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT stokvel_balance, loan_status, savings_goal, gender FROM members WHERE LOWER(TRIM(name)) = LOWER(TRIM(?)) AND pin = ?",
        (name, pin),
    )
    user = cursor.fetchone()
    conn.close()
    return user


def register_user(name, pin, gender, balance, goal):
    try:
        conn = sqlite3.connect("rendani.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO members (name, pin, gender, stokvel_balance, loan_status, savings_goal)
            VALUES (?, ?, ?, ?, 'Eligible for Micro-loan', ?)
        """,
            (name.strip(), pin.strip(), gender, balance, goal),
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def update_savings_goal(name, new_goal):
    conn = sqlite3.connect("rendani.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE members SET savings_goal = ? WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))",
        (new_goal, name),
    )
    conn.commit()
    conn.close()


# ==========================================
# 3. MUFAMADI AI BRAIN
# ==========================================
def mufamadi_ai_response(
    user_text, member_name, greeting, balance, loan_status
):
    query = user_text.lower()
    balance_keywords = [
        "stokvel",
        "balance",
        "tshelede",
        "vhugala",
        "mali",
        "gontshi",
        "muṅwaloni",
        "chelete",
        "savings",
    ]
    loan_keywords = [
        "loan",
        "credit",
        "loni",
        "chikolodo",
        "chikolo",
        "mubhadhalo",
        "borrow",
        "kolodo",
    ]

    if any(word in query for word in balance_keywords):
        return (
            f"🤖 **Mufamadi AI:** {greeting} {member_name}! Your total Stokvel savings balance is **R{balance:,.2f}**.\n\n"
            f"*(Tshivenḓa: Mugaganyo wau wa tshitaka u na R{balance:,.2f} zwa zwino.)*"
        )
    elif any(word in query for word in loan_keywords):
        return (
            f"🤖 **Mufamadi AI:** Hello {member_name}! Your alternative credit status: **{loan_status}**.\n\n"
            f"*(Tshivenḓa: Mufamadi AI credit score yau i sumbedza uri status yau ndi: {loan_status}.)*"
        )
    else:
        return (
            f"🤖 **Mufamadi AI:** {greeting}! I am analyzing your request. "
            f"You can ask me about your **stokvel balance**, **loan eligibility**, or **savings status** in Tshivenḓa, Sepedi, or English!"
        )


# ==========================================
# 4. SESSION STATE AUTHENTICATION CONTROL
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_name" not in st.session_state:
    st.session_state["user_name"] = ""


# ==========================================
# 5. CULTURAL LOGIN / SIGN UP SCREEN
# ==========================================
if not st.session_state["logged_in"]:
    st.markdown(
        """
        <div style="text-align: center; background-color: #1A1D20; padding: 15px; border-radius: 10px; border-left: 5px solid #D4AF37; margin-bottom: 20px;">
            <h2 style="color: #D4AF37; margin:0;">🥁 Ndaa & Aa! Welcome to R.C.C.</h2>
            <p style="color: #CCCCCC; font-size: 14px; margin-top: 5px;">Empowering Rural Community Finance & Savings</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(
        ["🔑 Member Sign In (Log In)", "➕ New Member Sign Up"]
    )

    # LOGIN TAB
    with tab1:
        st.markdown("#### 🔒 Sign In to Your Community Account")
        login_name = st.text_input(
            "👤 Full Member Name:",
            placeholder="e.g., Ndivhuwo M. or Vho-Makhadzi",
            key="login_name_input",
        )
        login_pin = st.text_input(
            "🔐 4-Digit Security PIN:",
            type="password",
            placeholder="Enter PIN (Default: 1234)",
            key="login_pin_input",
        )

        if st.button("🔑 Log In to Dashboard", use_container_width=True):
            user_data = authenticate_user(login_name, login_pin)
            if user_data:
                st.session_state["logged_in"] = True
                st.session_state["user_name"] = login_name.strip()
                st.rerun()
            else:
                st.error("❌ Invalid Member Name or PIN. Please try again.")

    # REGISTER TAB
    with tab2:
        st.markdown("#### 📝 Register New Community Profile")
        reg_name = st.text_input("👤 Full Name:", key="reg_name_input")
        reg_pin = st.text_input(
            "🔐 Set 4-Digit Security PIN:",
            type="password",
            max_chars=4,
            key="reg_pin_input",
        )

        # Culturally Grounded Gender Greeting Selector
        reg_gender = st.radio(
            "👑 Select Gender (for Traditional Greeting Etiquette):",
            [
                "🧔 Male Member (Greets with NDAA!)",
                "👩 Female Member (Greets with AA!)",
            ],
            key="reg_gender_input",
        )
        gender_val = "Male" if "Male" in reg_gender else "Female"

        reg_balance = st.number_input(
            "💰 Initial Stokvel Contribution (R):",
            min_value=0.0,
            value=1000.0,
            step=100.0,
        )
        reg_goal = st.number_input(
            "🎯 Target Savings Goal (R):",
            min_value=500.0,
            value=10000.0,
            step=500.0,
        )

        if st.button(
            "🥁 Register & Join Rendani Capital", use_container_width=True
        ):
            if reg_name and reg_pin:
                success = register_user(
                    reg_name, reg_pin, gender_val, reg_balance, reg_goal
                )
                if success:
                    greeting_preview = "NDAA!" if gender_val == "Male" else "AA!"
                    st.success(
                        f"✅ Welcome {reg_name}! Your account has been registered. "
                        f"Mufamadi AI will greet you with '{greeting_preview}'. Please switch to the Sign In tab to log in."
                    )
                else:
                    st.warning(
                        "⚠️ Member name already exists. Please log in under the Sign In tab."
                    )
            else:
                st.warning("⚠️ Please provide both a Full Name and PIN.")

# ==========================================
# 6. MAIN MEMBER DASHBOARD (POST-LOGIN)
# ==========================================
else:
    member_name = st.session_state["user_name"]

    # Fetch User Data from DB
    conn = sqlite3.connect("rendani.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT stokvel_balance, loan_status, savings_goal, gender FROM members WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))",
        (member_name,),
    )
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        stokvel_bal, loan_stat, savings_goal, gender = user_data
        if savings_goal is None:
            savings_goal = 10000.0

        # Traditional Greeting Assignment
        greeting = "NDAA!!!" if gender == "Male" else "AA!!!"

        # Header & Log Out
        col_head1, col_head2 = st.columns([3, 1])
        with col_head1:
            st.markdown(f"### 🖐️ {greeting} {member_name}!")
        with col_head2:
            if st.button("🚪 Log Out"):
                st.session_state["logged_in"] = False
                st.session_state["user_name"] = ""
                st.rerun()

        # Quick Action Buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💰 Check Stokvel Balance", use_container_width=True):
                st.success(
                    f"Mufamadi AI: {greeting} Your current balance is R{stokvel_bal:,.2f}"
                )

        with col2:
            if st.button("💳 Check Credit & Loans", use_container_width=True):
                st.info(f"Mufamadi AI: Credit Status — {loan_stat}")

        st.divider()

        # 🎯 STOKVEL SAVINGS GOAL TRACKER
        st.markdown("### 🎯 Stokvel Savings Goal Tracker")
        progress = (
            min(stokvel_bal / savings_goal, 1.0) if savings_goal > 0 else 0
        )
        st.write(
            f"**Target Goal:** R{savings_goal:,.2f} | **Current Balance:** R{stokvel_bal:,.2f}"
        )
        st.progress(progress)
        st.write(f"📊 **Progress:** {progress * 100:.1f}% of goal reached.")

        with st.expander("⚙️ Adjust Target Savings Goal"):
            new_goal_val = st.number_input(
                "Set New Target Goal Amount (R):",
                value=float(savings_goal),
                step=500.0,
            )
            if st.button("Update Goal"):
                update_savings_goal(member_name, new_goal_val)
                st.success("Target savings goal updated successfully!")
                st.rerun()

        # Monthly Contribution Calculator
        st.markdown("#### 🧮 Group Monthly Contribution Calculator")
        months = st.slider(
            "Number of months to reach remaining target:",
            min_value=1,
            max_value=24,
            value=6,
        )
        remaining_balance = max(savings_goal - stokvel_bal, 0)
        monthly_payment = remaining_balance / months if months > 0 else 0

        st.info(
            f"💡 **Mufamadi AI Calculation:** To reach your remaining goal of **R{remaining_balance:,.2f}** in {months} months, "
            f"you need to contribute **R{monthly_payment:,.2f} / month**."
        )

        st.divider()

        # 🤖 MUFAMADI AI CHATBOX
        st.markdown("### 🎙️ Talk to Mufamadi AI Assistant")
        st.write(
            "Ask any financial question in **Tshivenḓa**, **Sepedi**, **Xitsonga**, or **English**:"
        )

        user_query = st.text_input(
            "Type or tap mic on your keyboard to speak:",
            placeholder="e.g., Ndi na gontshi muṅwaloni wanga?",
        )

        if user_query:
            st.markdown(f"**You asked:** *\"{user_query}\"*")
            response = mufamadi_ai_response(
                user_query, member_name, greeting, stokvel_bal, loan_stat
            )
            st.success(response)