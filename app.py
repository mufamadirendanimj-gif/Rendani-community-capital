import os
import sqlite3
import streamlit as st

# ==========================================
# 1. PAGE CONFIGURATION & LOGO
# ==========================================
st.set_page_config(
    page_title="Rendani Community Capital", page_icon="🏛️", layout="centered"
)

# Display Custom R.C.C. Logo if present in the folder
if os.path.exists("logo.png"):
    st.image("logo.png", use_container_width=True)
elif os.path.exists("logo.jpg"):
    st.image("logo.jpg", use_container_width=True)
else:
    st.title("🏛️ Rendani Community Capital")

st.caption("Powered by Mufamadi AI | R.C.C. Digital Finance")
st.divider()


# ==========================================
# 2. DATABASE SETUP
# ==========================================
def init_db():
    conn = sqlite3.connect("rendani.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            stokvel_balance REAL,
            loan_status TEXT,
            savings_goal REAL DEFAULT 10000.0
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM members")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO members (name, stokvel_balance, loan_status, savings_goal)
            VALUES ('Vho-Makhadzi', 5400.0, 'Approved for R2,000 Micro-loan', 10000.0)
        """)
        cursor.execute("""
            INSERT INTO members (name, stokvel_balance, loan_status, savings_goal)
            VALUES ('Ndivhuwo M.', 12000.0, 'Approved for R5,000 Business Loan', 15000.0)
        """)
    conn.commit()
    conn.close()


init_db()


def get_member_data(name):
    conn = sqlite3.connect("rendani.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT stokvel_balance, loan_status, savings_goal FROM members WHERE name = ?",
        (name,),
    )
    data = cursor.fetchone()
    conn.close()
    return data


def get_all_member_names():
    conn = sqlite3.connect("rendani.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM members")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


def update_savings_goal(name, new_goal):
    conn = sqlite3.connect("rendani.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE members SET savings_goal = ? WHERE name = ?", (new_goal, name)
    )
    conn.commit()
    conn.close()


# ==========================================
# 3. MUFAMADI AI BRAIN
# ==========================================
def mufamadi_ai_response(user_text, member_name, balance, loan_status):
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
            f"🤖 **Mufamadi AI:** Ndaa {member_name}! Your total Stokvel savings balance is **R{balance:,.2f}**.\n\n"
            f"*(Tshivenḓa: Mugaganyo wau wa tshitaka u na R{balance:,.2f} zwa zwino.)*"
        )
    elif any(word in query for word in loan_keywords):
        return (
            f"🤖 **Mufamadi AI:** Hello {member_name}! Your alternative credit status: **{loan_status}**.\n\n"
            f"*(Tshivenḓa: Mufamadi AI credit score yau i sumbedza uri status yau ndi: {loan_status}.)*"
        )
    else:
        return (
            f"🤖 **Mufamadi AI:** Ndaa! I am analyzing your request. "
            f"You can ask me about your **stokvel balance**, **loan eligibility**, or **savings status** in Tshivenḓa, Sepedi, or English!"
        )


# ==========================================
# 4. USER INTERFACE
# ==========================================
st.markdown("### 👤 Select Community Member Profile")
member_list = get_all_member_names()
member_name = st.selectbox("Choose Profile:", member_list)

user_data = get_member_data(member_name)

if user_data:
    stokvel_bal, loan_stat, savings_goal = user_data
    if savings_goal is None:
        savings_goal = 10000.0

    st.markdown(f"### 🖐️ Ndaa, {member_name}!")

    # Quick One-Tap Action Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💰 Check Stokvel Balance", use_container_width=True):
            st.success(
                f"Mufamadi AI: Your current balance is R{stokvel_bal:,.2f}"
            )

    with col2:
        if st.button("💳 Check Credit & Loans", use_container_width=True):
            st.info(f"Mufamadi AI: Credit Status — {loan_stat}")

    st.divider()

    # 🎯 STOKVEL SAVINGS GOAL TRACKER
    st.markdown("### 🎯 Stokvel Savings Goal Tracker")
    progress = min(stokvel_bal / savings_goal, 1.0) if savings_goal > 0 else 0
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
            user_query, member_name, stokvel_bal, loan_stat
        )
        st.success(response)

st.divider()

# Register New Member Form
st.markdown("### ➕ Register New Member to Database")
new_name = st.text_input("Member Full Name:")
new_balance = st.number_input("Initial Stokvel Deposit (R):", min_value=0.0)
new_goal = st.number_input(
    "Target Savings Goal (R):", min_value=500.0, value=10000.0
)

if st.button("Save New Member"):
    if new_name:
        conn = sqlite3.connect("rendani.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO members (name, stokvel_balance, loan_status, savings_goal)
            VALUES (?, ?, 'Eligible for Micro-loan', ?)
        """,
            (new_name, new_balance, new_goal),
        )
        conn.commit()
        conn.close()
        st.success(f"Successfully added {new_name} to database!")
        st.rerun()
    else:
        st.warning("Please enter a member name.")