import os
import sqlite3
import streamlit as st

# ==========================================
# 1. PAGE CONFIGURATION & STYLING (BLUE CULTURAL DESIGN)
# ==========================================
st.set_page_config(
    page_title="Rendani Community Capital", page_icon="🏛️", layout="centered"
)

# Custom CSS matching your exact design design mock-up
st.markdown(
    """
    <style>
    /* Hide default Streamlit headers, footers & badges */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QSob, .styles_viewerBadge__1yB5_, 
    [data-testid="stDecoration"], [data-testid="stStatusWidget"],
    .floating-badge, #webintoapp-badge, iframe[src*="webintoapp"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* Set main background to royal cultural blue */
    .stApp {
        background-color: #0A3B82 !important;
        color: #FFFFFF !important;
    }

    /* White bold main heading */
    .signup-title {
        text-align: center;
        color: #FFFFFF;
        font-weight: 800;
        font-size: 26px;
        letter-spacing: 1.5px;
        margin-bottom: 25px;
        margin-top: 10px;
        text-transform: uppercase;
    }

    /* Input fields with Venda stripe bottom border */
    .stTextInput input {
        background-color: #FFFFFF !important;
        color: #333333 !important;
        border-radius: 14px !important;
        padding: 12px 16px !important;
        border: none !important;
        border-bottom: 6px solid #8B0000 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
        font-size: 15px !important;
    }

    /* Colorful Divider Bar */
    .cultural-divider {
        height: 12px;
        background: linear-gradient(90deg, 
            #000000 0%, #000000 10%, 
            #8B0000 10%, #8B0000 25%, 
            #D4AF37 25%, #D4AF37 40%, 
            #008000 40%, #008000 55%, 
            #8B0000 55%, #8B0000 70%, 
            #000000 70%, #000000 85%,
            #D4AF37 85%, #D4AF37 100%);
        border-radius: 4px;
        margin: 25px 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.4);
    }

    /* Radio button selection styling for Gender */
    div[data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
        font-weight: 600;
    }

    /* Main Action Button (SIGN UP) */
    div.stButton > button {
        background-color: #0F2D6B !important;
        color: #FFFFFF !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        letter-spacing: 1.2px !important;
        border-radius: 16px !important;
        padding: 14px !important;
        border: none !important;
        border-left: 8px solid #8B0000 !important;
        border-right: 8px solid #8B0000 !important;
        box-shadow: 0 6px 14px rgba(0,0,0,0.4) !important;
        text-transform: uppercase !important;
        transition: transform 0.2s ease !important;
    }
    div.stButton > button:hover {
        transform: scale(1.02) !important;
        background-color: #163B88 !important;
    }

    /* Custom Labels */
    label {
        color: #FFFFFF !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        letter-spacing: 0.8px !important;
        text-transform: uppercase !important;
    }

    /* Subtext links */
    .switch-link {
        text-align: center;
        color: #E0E0E0;
        font-size: 14px;
        margin-top: 15px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Optional Custom Logo
if os.path.exists("logo.png"):
    st.image("logo.png", width=140)
elif os.path.exists("logo.jpg"):
    st.image("logo.jpg", width=140)


# ==========================================
# 2. SAFE DATABASE SETUP
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
# 5. CUSTOM DESIGNED SIGN-UP & LOGIN SCREEN
# ==========================================
if not st.session_state["logged_in"]:

    tab1, tab2 = st.tabs(["SIGN UP", "LOG IN"])

    # SIGN UP TAB (Matching Image Design)
    with tab1:
        st.markdown(
            '<div class="signup-title">CREATE YOUR<br>ACCOUNT</div>',
            unsafe_allow_html=True,
        )

        reg_name = st.text_input(
            "Username / Email",
            placeholder="Username / Email",
            key="reg_name_input",
            label_visibility="collapsed",
        )
        reg_pin = st.text_input(
            "Password",
            type="password",
            placeholder="Password / PIN",
            key="reg_pin_input",
            label_visibility="collapsed",
        )

        # Cultural Pattern Divider Line
        st.markdown(
            '<div class="cultural-divider"></div>', unsafe_allow_html=True
        )

        st.markdown(
            '<p style="text-align: center; font-weight: bold; font-size: 14px; letter-spacing: 1px; color: #FFFFFF;">SELECT GENDER</p>',
            unsafe_allow_html=True,
        )

        # Gender Selection Cards
        gender_col1, gender_col2 = st.columns(2)
        with gender_col1:
            male_selected = st.checkbox("🧔 MALE (NDAA!)", value=True)
        with gender_col2:
            female_selected = st.checkbox("👩 FEMALE (AA!)", value=False)

        gender_val = "Male" if male_selected else "Female"

        reg_balance = st.number_input(
            "Initial Stokvel Contribution (R):",
            min_value=0.0,
            value=1000.0,
            step=100.0,
        )
        reg_goal = st.number_input(
            "Target Savings Goal (R):",
            min_value=500.0,
            value=10000.0,
            step=500.0,
        )

        st.write("")
        if st.button("SIGN UP", use_container_width=True):
            if reg_name and reg_pin:
                success = register_user(
                    reg_name, reg_pin, gender_val, reg_balance, reg_goal
                )
                if success:
                    greeting_preview = "NDAA!" if gender_val == "Male" else "AA!"
                    st.success(
                        f"✅ Account created successfully for {reg_name}! Mufamadi AI will greet you with '{greeting_preview}'. Please click LOG IN tab above."
                    )
                else:
                    st.warning("⚠️ Member name already exists. Please Log In.")
            else:
                st.warning("⚠️ Please fill in both Username and Password.")

        st.markdown(
            '<p class="switch-link">Already have an account? Switch to <b>LOG IN</b> tab above.</p>',
            unsafe_allow_html=True,
        )

    # LOG IN TAB
    with tab2:
        st.markdown(
            '<div class="signup-title">LOG IN TO YOUR<br>ACCOUNT</div>',
            unsafe_allow_html=True,
        )

        login_name = st.text_input(
            "Username / Email",
            placeholder="Username / Email",
            key="login_name_input",
            label_visibility="collapsed",
        )
        login_pin = st.text_input(
            "Password",
            type="password",
            placeholder="Password / PIN",
            key="login_pin_input",
            label_visibility="collapsed",
        )

        st.markdown(
            '<div class="cultural-divider"></div>', unsafe_allow_html=True
        )

        if st.button("LOG IN", use_container_width=True):
            user_data = authenticate_user(login_name, login_pin)
            if user_data:
                st.session_state["logged_in"] = True
                st.session_state["user_name"] = login_name.strip()
                st.rerun()
            else:
                st.error("❌ Invalid Username or Password. Please try again.")


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