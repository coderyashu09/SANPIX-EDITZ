import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

import smtplib
import random
import streamlit as st
import sqlite3
import pandas as pd
import random
import smtplib
from email.mime.text import MIMEText

# ---------------- CONFIG FIRST (IMPORTANT FIX) ----------------
st.set_page_config(page_title="Sanpix Editz", layout="wide")

# ---------------- DATABASE ----------------
conn = sqlite3.connect("sanpix.db", check_same_thread=False)
c = conn.cursor()

# 🔥 ADD THIS HERE
try:
    c.execute("ALTER TABLE videos ADD COLUMN views INTEGER DEFAULT 0")
    conn.commit()
except:
    pass

# PUBLIC TABLES
c.execute("""CREATE TABLE IF NOT EXISTS profile (
    id INTEGER PRIMARY KEY,
    name TEXT,
    bio TEXT,
    image TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file TEXT,
    caption TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS likes (
    video_id INTEGER,
    user TEXT
)""")

conn.commit()

# ---------------- EMAIL CONFIG ----------------
EMAIL = "ykanzariya109@gmail.com"
APP_PASSWORD = "mcmagrgmfadwrxpu"
ADMIN_EMAIL = "sanjayparmar9428@gmail.com"

# ---------------- SESSION ----------------
# SESSION INIT (FIX)
if "logged" not in st.session_state:
    st.session_state.logged = False

if "otp" not in st.session_state:
    st.session_state.otp = ""

if "show_login" not in st.session_state:
    st.session_state.show_login = False

# 🔥 ADD THIS LINE (IMPORTANT FIX)
if "user" not in st.session_state:
    st.session_state.user = ""


# ---------------- SEND OTP ----------------
def send_email_otp(to_email, otp):
    try:
        msg = MIMEText(f"Your OTP is {otp}")
        msg["Subject"] = "Sanpix OTP"
        msg["From"] = EMAIL
        msg["To"] = to_email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(e)
        return False

# ---------------- PUBLIC PAGE ----------------
def public_page():

    import streamlit as st
    import pandas as pd

    # 🎨 STYLE
    st.markdown("""
    <style>

    .title {
        text-align:center;
        font-size:48px;
        font-weight:800;
        background: linear-gradient(90deg,#00f2ff,#c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom:20px;
    }

    .name {
        text-align:center;
        font-size:22px;
        font-weight:600;
        margin-top:10px;
    }

    .bio {
        text-align:center;
        color:#aaa;
        margin-bottom:20px;
    }

    </style>
    """, unsafe_allow_html=True)

    # 📦 DATA
    prof = pd.read_sql("SELECT * FROM profile", conn)
    vids = pd.read_sql("SELECT * FROM videos", conn)

    # 🔥 TITLE
    st.markdown('<div class="title">SANPIX EDITZ</div>', unsafe_allow_html=True)

    # 🔥 NAME + BIO
    if not prof.empty:
        st.markdown(f'<div class="name">{prof["name"][0]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="bio">{prof["bio"][0]}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="name">sanpix editz</div>', unsafe_allow_html=True)
        st.markdown('<div class="bio">by Sanjay Parmar</div>', unsafe_allow_html=True)

    # 🔘 BUTTONS
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <a href="https://www.instagram.com/its_editor7777?igsh=MWppdTNhMW11MmJoYw==" target="_blank">
        <button style="width:100%;border-radius:25px;background:linear-gradient(90deg,#00f2ff,#c084fc);color:black;font-weight:600;padding:10px;">
        Instagram
        </button></a>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <a href="https://wa.me/919428508840" target="_blank">
        <button style="width:100%;border-radius:25px;background:linear-gradient(90deg,#00f2ff,#c084fc);color:black;font-weight:600;padding:10px;">
        WhatsApp
        </button></a>
        """, unsafe_allow_html=True)

    with col3:
        if st.button("Admin Login", use_container_width=True):
            st.session_state.show_login = True
            st.rerun()

    st.markdown("---")
    st.markdown("## 🎬 Latest Reels")

    # 🔥 SESSION INIT
    if "selected_video" not in st.session_state:
        st.session_state.selected_video = None

    # ================= FULL VIDEO VIEW =================
    if st.session_state.selected_video:

        vid = pd.read_sql(
            f"SELECT * FROM videos WHERE id={st.session_state.selected_video}",
            conn
        )

        if not vid.empty:

            # 🔙 BACK BUTTON
            if st.button("⬅ Back"):
                st.session_state.selected_video = None
                st.rerun()

            # 🎥 ORIGINAL SIZE VIDEO
            st.video(vid["file"][0])
            st.caption(vid["caption"][0])

    # ================= GRID VIEW =================
    else:

        if vids.empty:
            st.info("No videos available")

        else:
            cols = st.columns(3)

            for i, row in enumerate(vids.itertuples()):
                with cols[i % 3]:

                    # 🎯 CLICKABLE VIDEO (NO EXTRA BUTTON)
                    if st.button("", key=f"open_{row.id}"):

                        # increase view
                        c.execute("UPDATE videos SET views = views + 1 WHERE id=?", (row.id,))
                        conn.commit()

                        st.session_state.selected_video = row.id
                        st.rerun()

                    # 🎥 SAME SIZE LOOK
                    st.video(row.file, format="video/mp4")

# ---------------- PUBLIC FLOW ----------------
if not st.session_state.logged and not st.session_state.show_login:
    public_page()
    st.stop()

# 🔙 Back to Public Profile (LOGIN PAGE)
col1, col2 = st.columns([1,6])
with col1:
    if st.button("⬅"):
        st.session_state.show_login = False
        st.rerun()
# ---------------- LOGIN ----------------
if not st.session_state.logged:

    st.markdown("<h1 style='text-align:center;color:#00f2ff'>Admin Login</h1>", unsafe_allow_html=True)

    if st.button("Send OTP"):
        otp = str(random.randint(1000,9999))
        if send_email_otp(ADMIN_EMAIL, otp):
            st.session_state.otp = otp
            st.success("OTP Sent")

    otp_input = st.text_input("Enter OTP", type="password")

    if st.button("Verify"):
        if otp_input == st.session_state.otp:
            st.session_state.logged = True
            st.session_state.user = ADMIN_EMAIL   # 🔥 IMPORTANT
            st.rerun()
        else:
            st.error("Invalid OTP")

    st.stop()

# ---------------- AFTER LOGIN ----------------
st.success("Welcome Admin Dashboard (your existing app starts here)")

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

/* 🔥 BACKGROUND */
.stApp {
    background:
        radial-gradient(circle at top right, rgba(0,255,255,0.08), transparent 40%),
        radial-gradient(circle at bottom left, rgba(180,0,255,0.08), transparent 40%),
        #0b0b0f;
    color: #eaeaea;
    font-family: 'Segoe UI', sans-serif;
}

/* 🔥 TITLE */
.title {
    text-align:center;
    font-size:42px;
    font-weight:800;
    background: linear-gradient(90deg,#00f2ff,#c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow:0 0 25px rgba(0,242,255,0.4);
    margin-bottom:25px;
}

/* 🔥 CARD */
.card {
    padding:20px;
    border-radius:16px;
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(10px);
    border:1px solid rgba(0,255,255,0.15);
    text-align:center;
    transition:0.3s;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow:0 0 25px rgba(0,255,255,0.4);
}

/* 🔥 EMPTY BOX */
.empty-box {
    display:flex;
    justify-content:center;
    align-items:center;
    height:220px;
    border-radius:16px;
    background: rgba(255,255,255,0.03);
    border:1px dashed rgba(255,255,255,0.1);
    color:#aaa;
}

/* 🔥 BUTTON */
.stButton>button {
    border-radius:12px;
    background: linear-gradient(90deg,#00f2ff,#a855f7);
    color:black;
    font-weight:600;
    border:none;
    transition:0.3s;
}

.stButton>button:hover {
    box-shadow:0 0 20px #00f2ff;
    transform: scale(1.03);
}

/* 🔥 INPUT */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox div {
    background: rgba(255,255,255,0.05) !important;
    border-radius:10px !important;
    border:1px solid rgba(255,255,255,0.1) !important;
    color:white !important;
}

/* 🔥 SIDEBAR */
section[data-testid="stSidebar"] {
    background: rgba(15,15,20,0.9);
    backdrop-filter: blur(15px);
    border-right:1px solid rgba(255,255,255,0.05);
}

/* 🔥 SIDEBAR RADIO */
.stRadio > div {
    gap:10px;
}

.stRadio label {
    padding:10px;
    border-radius:10px;
    transition:0.3s;
}

.stRadio label:hover {
    background: rgba(255,255,255,0.05);
    color:#00f2ff;
}

/* 🔥 TABLE */
[data-testid="stDataFrame"] {
    border-radius:12px;
    overflow:hidden;
}

/* 🔥 MOBILE RESPONSIVE */
@media (max-width: 768px) {
    .title {
        font-size:28px;
    }

    .card {
        padding:14px;
    }
}

</style>
""", unsafe_allow_html=True)
st.markdown("### ")
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

# 🔥 NEW FUNCTION
def delete_payment(payment_id):
    c.execute("DELETE FROM payments WHERE id=?", (payment_id,))
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
page = st.sidebar.radio("", ["Dashboard","Add Work","Studio Panel","History","All Records","Public Panel"])
# 🔐 Logout Button (Sidebar)
st.sidebar.markdown("---")

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged = False
    st.session_state.otp = ""
    st.session_state.email = ""
    st.session_state.user = ""
    st.rerun()

# 🔙 Back to Public Profile
if st.sidebar.button("🌐 Public Profile"):
    st.session_state.logged = False
    st.session_state.show_login = False
    st.rerun()
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

        # 🔥 PAYMENT SECTION WITH DELETE
        st.markdown("### Payments")

        if pay.empty:
            st.markdown('<div class="empty-box">No payments</div>', unsafe_allow_html=True)
        else:
            for row in pay.itertuples():
                p1,p2,p3 = st.columns([3,3,1])
                p1.write(f"₹ {row.amount}")
                p2.write(row.date)

                if p3.button("❌", key=f"pay_del{row.id}"):
                    delete_payment(row.id)
                    st.rerun()

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


# ================= PUBLIC PROFILE + VIDEO SYSTEM =================

# 📦 DATABASE
c.execute("""CREATE TABLE IF NOT EXISTS profile (
    id INTEGER PRIMARY KEY,
    name TEXT,
    bio TEXT,
    image TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file TEXT,
    caption TEXT,
    views INTEGER DEFAULT 0
)""")

c.execute("""CREATE TABLE IF NOT EXISTS likes (
    video_id INTEGER,
    user TEXT
)""")

conn.commit()

# 📁 CREATE FOLDERS
import os
if not os.path.exists("uploads"):
    os.makedirs("uploads")
if not os.path.exists("videos"):
    os.makedirs("videos")


# # ---------------- SIDEBAR ADD ----------------
# if "Public Panel" not in ["Dashboard","Add Work","Studio Panel","History","All Records"]:
#     pass

# # Add manually in your sidebar list:
# # "Public Panel"


# ================= PUBLIC PANEL (ADMIN ONLY) =================
if page == "Public Panel":

    st.markdown('<div class="title">PUBLIC PROFILE</div>', unsafe_allow_html=True)

    # 🔐 ADMIN CHECK
    if st.session_state.user != ADMIN_EMAIL:
        st.error("Access Denied")
        st.stop()

    # ---------- PROFILE ----------
    st.markdown("### Edit Profile")

    prof = pd.read_sql("SELECT * FROM profile", conn)

    default_name = prof["name"][0] if not prof.empty else ""
    default_bio = prof["bio"][0] if not prof.empty else ""

    name = st.text_input("Name", value=default_name)
    bio = st.text_area("Bio", value=default_bio)

    if st.button("Save Profile"):

        # keep image column empty
        c.execute("DELETE FROM profile")
        c.execute("INSERT INTO profile VALUES (1,?,?,?)", (name, bio, ""))

        conn.commit()
        st.success("Profile Updated")

    st.markdown("---")

   # ---------- VIDEO UPLOAD ----------
st.markdown("### Upload Video")

video = st.file_uploader("Upload Video", type=["mp4"])
caption = st.text_input("Caption")

if st.button("Upload Video"):
    if video:

        # 📁 Save video
        path = f"videos/{video.name}"

        with open(path, "wb") as f:
            f.write(video.getbuffer())

        # 💾 Save in DB
        c.execute(
            "INSERT INTO videos (file, caption) VALUES (?, ?)",
            (path, caption)
        )
        conn.commit()

        st.success("✅ Uploaded Successfully (Works on Mobile + Desktop)")

    # ---------- ADMIN VIDEO LIST ----------
    st.markdown("### Manage Videos")

    vids = pd.read_sql("SELECT * FROM videos", conn)

    if vids.empty:
        st.markdown('<div class="empty-box">No videos</div>', unsafe_allow_html=True)
    else:
        for row in vids.itertuples():
            st.video(row.file, format="video/mp4")
            st.write(row.caption)

            col1, col2 = st.columns([3,1])

            with col1:
                st.markdown(f"""
                    <div style="
                    display:inline-block;
                    padding:6px 12px;
                    border-radius:12px;
                    background:rgba(0,255,255,0.1);
                    border:1px solid #00f2ff;
                    font-size:13px;
                    text-align:center;
                    width:80px;
                    ">
                    👁 {row.views}
                     </div>
                    """, unsafe_allow_html=True)

            if col2.button("❌ Delete", key=f"del_vid{row.id}"):
                c.execute("DELETE FROM videos WHERE id=?", (row.id,))
                conn.commit()
                st.rerun()


# ================= PUBLIC VIEW =================
def show_public_page():

    st.markdown('<div class="title">SANPIX EDITZ</div>', unsafe_allow_html=True)

    prof = pd.read_sql("SELECT * FROM profile", conn)
    vids = pd.read_sql("SELECT * FROM videos", conn)

    # PROFILE
    if not prof.empty:
        if prof["image"][0]:
            st.image(prof["image"][0], width=120)

        st.markdown(f"### {prof['name'][0]}")
        st.write(prof["bio"][0])

    st.markdown("---")

    # VIDEOS
    if vids.empty:
        st.markdown('<div class="empty-box">No videos available</div>', unsafe_allow_html=True)
    else:
        for row in vids.itertuples():

            st.video(row.file, format="video/mp4")
            st.write(row.caption)

            c1, c2, c3 = st.columns(3)

            # ❤️ LIKE (NO COUNT SHOWN)
            if c1.button("❤️", key=f"like_{row.id}"):
                c.execute("INSERT INTO likes VALUES (?,?)", (row.id,"public"))
                conn.commit()

            c2.button("💬", key=f"comment_{row.id}")
            c3.button("🔗", key=f"share_{row.id}")

            # 👁 VIEW COUNT (ADMIN ONLY LOGIC)
            c.execute("UPDATE videos SET views = views + 1 WHERE id=?", (row.id,))
            conn.commit()
