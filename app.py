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

c.execute("""CREATE TABLE IF NOT EXISTS history (
    studio TEXT PRIMARY KEY
)""")

c.execute("""CREATE TABLE IF NOT EXISTS completed (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    studio TEXT,
    date TEXT,
    description TEXT,
    duration TEXT,
    total REAL
)""")

c.execute("""CREATE TABLE IF NOT EXISTS all_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    studio TEXT,
    date TEXT,
    description TEXT,
    duration TEXT,
    total REAL
)""")

conn.commit()

# ---------------- UI ----------------
st.markdown("""
<style>
body { background: linear-gradient(135deg,#0f0c29,#302b63,#24243e); color:white;}

.card {
    padding:18px;
    border-radius:16px;
    background: rgba(255,255,255,0.05);
    text-align:center;
    box-shadow:0 0 20px #00f2ff40;
}

.title {
    text-align:center;
    font-size:36px;
    color:#00f2ff;
    margin-bottom:20px;
}

.empty-box {
    display:flex;
    justify-content:center;
    align-items:center;
    height:200px;
    border-radius:15px;
    background: rgba(255,255,255,0.05);
}
</style>
""", unsafe_allow_html=True)

# ---------------- FUNCTIONS ----------------
def add_work(studio, date, desc, dur, total):
    c.execute("DELETE FROM history WHERE studio=?", (studio,))
    c.execute("INSERT INTO work (studio,date,description,duration,total) VALUES (?,?,?,?,?)",
              (studio,date,desc,dur,total))
    c.execute("INSERT INTO all_records (studio,date,description,duration,total) VALUES (?,?,?,?,?)",
              (studio,date,desc,dur,total))
    conn.commit()

def add_payment(studio, amount):
    c.execute("INSERT INTO payments (studio,amount,date) VALUES (?,?,?)",
              (studio,amount,str(datetime.now())))
    conn.commit()

def get_studios():
    work = pd.read_sql("SELECT DISTINCT studio FROM work", conn)
    comp = pd.read_sql("SELECT DISTINCT studio FROM completed", conn)
    pay = pd.read_sql("SELECT DISTINCT studio FROM payments", conn)
    hist = pd.read_sql("SELECT studio FROM history", conn)

    all_s = pd.concat([work,comp,pay]).drop_duplicates()
    if not hist.empty:
        all_s = all_s[~all_s["studio"].isin(hist["studio"])]
    return all_s["studio"].tolist()

# ---------------- SIDEBAR ----------------
page = st.sidebar.radio("", ["Dashboard","Add Work","Studio Panel","History","All Records"])

# ---------------- DASHBOARD ----------------
if page == "Dashboard":
    st.markdown('<div class="title">SANPIX EDITZ</div>', unsafe_allow_html=True)

    work = pd.read_sql("SELECT * FROM work", conn)
    comp = pd.read_sql("SELECT * FROM completed", conn)
    pay = pd.read_sql("SELECT * FROM payments", conn)

    total = work["total"].sum() + comp["total"].sum()
    paid = pay["amount"].sum()
    remaining = total - paid

    c1,c2,c3 = st.columns(3)
    c1.markdown(f'<div class="card">Total<br><h2>{total}</h2></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="card">Paid<br><h2>{paid}</h2></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="card">Remaining<br><h2>{remaining}</h2></div>', unsafe_allow_html=True)

    st.markdown("### Recent Work")
    full = pd.concat([work,comp])
    if full.empty:
        st.markdown('<div class="empty-box">No work available</div>', unsafe_allow_html=True)
    else:
        st.dataframe(full[["studio","date","description","total"]])

# ---------------- ADD WORK ----------------
elif page == "Add Work":
    studios = get_studios()

    with st.form("form", clear_on_submit=True):
        selected = st.selectbox("Select Studio", [""]+studios)
        new = st.text_input("New Studio")
        studio = new if new else selected

        date = st.date_input("Date")
        desc = st.text_area("Description")
        dur = st.text_input("Duration")
        total = st.number_input("Total Amount")

        if st.form_submit_button("Save"):
            if not studio or not desc or total==0:
                st.error("Fill required")
            else:
                add_work(studio,str(date),desc,dur,total)
                st.rerun()

# ---------------- STUDIO PANEL ----------------
elif page == "Studio Panel":
    studios = get_studios()

    if not studios:
        st.markdown('<div class="empty-box">No work available</div>', unsafe_allow_html=True)
    else:
        studio = st.selectbox("Studio", studios)

        sdf = pd.read_sql("SELECT * FROM work WHERE studio=?", conn, params=(studio,))
        comp = pd.read_sql("SELECT * FROM completed WHERE studio=?", conn, params=(studio,))
        pay = pd.read_sql("SELECT * FROM payments WHERE studio=?", conn, params=(studio,))

        total = sdf["total"].sum() + comp["total"].sum()
        paid = pay["amount"].sum()
        remaining = total - paid

        st.markdown("### Work")
        for row in sdf.itertuples():
            c1,c2,c3,c4,c5,c6,c7 = st.columns([2,3,2,2,1,1,1])

            c1.write(row.date)
            c2.write(row.description)
            c3.write(row.duration)
            c4.write(row.total)

            if c5.button("✔", key=f"c{row.id}"):
                c.execute("INSERT INTO completed (studio,date,description,duration,total) VALUES (?,?,?,?,?)",
                          (studio,row.date,row.description,row.duration,row.total))
                c.execute("DELETE FROM work WHERE id=?", (row.id,))
                conn.commit()
                st.rerun()

            if c6.button("✏️", key=f"e{row.id}"):
                new_desc = st.text_input("Edit", value=row.description, key=f"edit{row.id}")
                if st.button("Save", key=f"save{row.id}"):
                    c.execute("UPDATE work SET description=? WHERE id=?", (new_desc,row.id))
                    conn.commit()
                    st.rerun()

            if c7.button("❌", key=f"d{row.id}"):
                c.execute("DELETE FROM work WHERE id=?", (row.id,))
                conn.commit()
                st.rerun()

        st.markdown("### Completed Work")
        st.dataframe(comp)

        st.markdown("### Payments")
        st.dataframe(pay)

        st.markdown("### Add Payment")
        pay_amt = st.number_input("Enter Amount")
        if st.button("Add Payment"):
            add_payment(studio, pay_amt)
            st.rerun()

        st.markdown("### Summary")
        c1,c2,c3 = st.columns(3)
        c1.metric("Total", total)
        c2.metric("Paid", paid)
        c3.metric("Remaining", remaining)

        st.markdown("### Delete Studio")
        if remaining > 0:
            st.warning("Payment is pending")

        confirm = st.checkbox("I understand and want to delete")

        if st.button("Delete Studio"):
            if remaining > 0 and not confirm:
                st.error("Confirm delete first")
            else:
                c.execute("INSERT OR IGNORE INTO history VALUES (?)", (studio,))
                conn.commit()
                st.rerun()

# ---------------- HISTORY ----------------
elif page == "History":
    hist = pd.read_sql("SELECT * FROM history", conn)

    if hist.empty:
        st.markdown('<div class="empty-box">No work available</div>', unsafe_allow_html=True)
    else:
        studio = st.selectbox("Studio", hist["studio"])

        if st.button("Restore"):
            c.execute("DELETE FROM history WHERE studio=?", (studio,))
            conn.commit()
            st.rerun()

        if st.button("Delete Permanently"):
            c.execute("DELETE FROM work WHERE studio=?", (studio,))
            c.execute("DELETE FROM payments WHERE studio=?", (studio,))
            c.execute("DELETE FROM completed WHERE studio=?", (studio,))
            c.execute("DELETE FROM history WHERE studio=?", (studio,))
            conn.commit()
            st.rerun()

# ---------------- ALL RECORDS ----------------
elif page == "All Records":
    data = pd.read_sql("SELECT * FROM all_records", conn)

    if data.empty:
        st.markdown('<div class="empty-box">No work available</div>', unsafe_allow_html=True)
    else:
        st.dataframe(data)
