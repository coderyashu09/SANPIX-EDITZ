import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Sanpix Editz", layout="wide")

# ---------------- DATABASE ----------------
conn = sqlite3.connect("sanpix.db", check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS work (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    studio TEXT,
    date TEXT,
    description TEXT,
    duration TEXT,
    total REAL
)""")

c.execute("""CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    studio TEXT,
    amount REAL,
    date TEXT
)""")

# 🔥 HISTORY TABLE
c.execute("""CREATE TABLE IF NOT EXISTS history (
    studio TEXT PRIMARY KEY
)""")

conn.commit()

# ---------------- CSS ----------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg,#0f0c29,#302b63,#24243e);
    color:white;
}

.neon {
    font-size: 40px;
    font-weight: bold;
    text-align:center;
    color:#fff;
    text-shadow:
    0 0 5px #00f2ff,
    0 0 10px #00f2ff,
    0 0 20px #00f2ff;
    animation: glow 2s infinite alternate;
}

@keyframes glow {
    from { text-shadow:0 0 10px #00f2ff; }
    to { text-shadow:0 0 30px #ff00ff; }
}

.card {
    background: rgba(255,255,255,0.05);
    padding:20px;
    border-radius:15px;
    backdrop-filter: blur(10px);
    transition:0.3s;
}
.card:hover {
    transform: translateY(-5px);
    box-shadow:0 0 25px #00f2ff;
}
</style>
""", unsafe_allow_html=True)

# ---------------- FUNCTIONS ----------------
def add_work(studio, date, desc, dur, total):
    c.execute("INSERT INTO work (studio,date,description,duration,total) VALUES (?,?,?,?,?)",
              (studio, date, desc, dur, total))
    conn.commit()

def add_payment(studio, amount):
    c.execute("INSERT INTO payments (studio,amount,date) VALUES (?,?,?)",
              (studio, amount, str(datetime.now())))
    conn.commit()

def move_to_history(studio):
    c.execute("INSERT OR IGNORE INTO history (studio) VALUES (?)", (studio,))
    conn.commit()

def delete_permanent(studio):
    c.execute("DELETE FROM work WHERE studio=?", (studio,))
    c.execute("DELETE FROM payments WHERE studio=?", (studio,))
    c.execute("DELETE FROM history WHERE studio=?", (studio,))
    conn.commit()

def get_history():
    return pd.read_sql("SELECT * FROM history", conn)

def get_data():
    df = pd.read_sql("SELECT * FROM work", conn)
    hist = get_history()
    if not hist.empty:
        df = df[~df["studio"].isin(hist["studio"])]
    return df

def get_payments():
    df = pd.read_sql("SELECT * FROM payments", conn)
    hist = get_history()
    if not hist.empty:
        df = df[~df["studio"].isin(hist["studio"])]
    return df

def studio_summary():
    df = get_data()
    pay = get_payments()

    summary = []
    for studio in df["studio"].unique():
        sdf = df[df["studio"] == studio]
        spay = pay[pay["studio"] == studio]

        total = sdf["total"].sum()
        paid = spay["amount"].sum()
        remaining = total - paid

        summary.append({
            "Studio": studio,
            "Total": total,
            "Paid": paid,
            "Remaining": remaining
        })

    return pd.DataFrame(summary)

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 🎬 Sanpix Editz")
page = st.sidebar.radio("", ["Dashboard","Add Work","Studio Panel","History"])

# ---------------- DASHBOARD ----------------
if page == "Dashboard":
    st.markdown('<div class="neon">SANPIX EDITZ</div>', unsafe_allow_html=True)

    df = get_data()
    pay = get_payments()

    total = df["total"].sum() if not df.empty else 0
    paid = pay["amount"].sum() if not pay.empty else 0
    remaining = total - paid

    c1,c2,c3 = st.columns(3)
    c1.markdown(f'<div class="card">💰 Total<br><h2>{total}</h2></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="card">✅ Paid<br><h2>{paid}</h2></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="card">⏳ Remaining<br><h2>{remaining}</h2></div>', unsafe_allow_html=True)

    st.markdown("### 📊 Recent Work")
    recent = df[["studio","date","description","total"]]
    st.dataframe(recent.tail(5))

    st.markdown("### 💼 Studio Summary")
    st.dataframe(studio_summary())

# ---------------- ADD WORK ----------------
elif page == "Add Work":
    st.markdown('<div class="neon">Add Work</div>', unsafe_allow_html=True)

    df = get_data()
    existing_studios = df["studio"].unique().tolist() if not df.empty else []

    with st.form("form"):
        col1,col2 = st.columns(2)

        with col1:
            selected = st.selectbox("Select Studio", [""]+existing_studios)
        with col2:
            new = st.text_input("New Studio")

        studio = new if new else selected

        date = st.date_input("Date")
        desc = st.text_area("Description")
        dur = st.text_input("Duration")
        total = st.number_input("Total Amount")

        if st.form_submit_button("Save"):
            if not studio:
                st.error("Enter studio")
            else:
                add_work(studio,str(date),desc,dur,total)
                st.success("Saved ✅")
                st.rerun()

# ---------------- STUDIO PANEL ----------------
elif page == "Studio Panel":
    st.markdown('<div class="neon">Studio Panel</div>', unsafe_allow_html=True)

    df = get_data()
    pay = get_payments()

    if not df.empty:
        studios = df["studio"].unique()
        selected = st.selectbox("Select Studio", studios)

        sdf = df[df["studio"] == selected]
        spay = pay[pay["studio"] == selected]

        total = sdf["total"].sum()
        paid = spay["amount"].sum()
        remaining = total - paid

        st.markdown("### Work")
        st.dataframe(sdf[["date","description","duration","total"]])

        st.markdown("### 💸 Add Payment")
        amt = st.number_input("Amount")

        if st.button("Add Payment"):
            add_payment(selected, amt)
            st.success("Added ✅")
            st.rerun()

        # 🔥 DELETE BUTTON
        st.markdown("### ⚠️ Delete Studio")
        if st.button("Move to History"):
            move_to_history(selected)
            st.warning("Moved to History")
            st.rerun()

        # TOTAL BOXES
        c1,c2,c3 = st.columns(3)
        c1.markdown(f'<div class="card">💰 Total<br><h2>{total}</h2></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="card">✅ Paid<br><h2>{paid}</h2></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="card">⏳ Remaining<br><h2>{remaining}</h2></div>', unsafe_allow_html=True)

# ---------------- HISTORY ----------------
elif page == "History":
    st.markdown('<div class="neon">History</div>', unsafe_allow_html=True)

    hist = get_history()

    if hist.empty:
        st.info("No deleted studios")
    else:
        selected = st.selectbox("Select Studio", hist["studio"])

        col1,col2 = st.columns(2)

        with col1:
            if st.button("Restore"):
                c.execute("DELETE FROM history WHERE studio=?", (selected,))
                conn.commit()
                st.success("Restored")
                st.rerun()

        with col2:
            if st.button("Delete Permanently"):
                delete_permanent(selected)
                st.error("Deleted Forever ❌")
                st.rerun()