import streamlit as st
import pandas as pd
import sqlite3
import smtplib
import hashlib
import re
import uuid
import json
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# =========================================================
#  AYARLAR
# =========================================================
st.set_page_config(page_title="YARENART | Sanat & İllüstrasyon Mağazası", page_icon="🎨", layout="wide")

DB_FILE = "yarenart.db"
UPLOAD_DIR = "uploaded_images"
ADMIN_EMAIL = "skus42173@gmail.com"
WHATSAPP_PHONE = "905527920708"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

TURKEY_CITIES = {
    "İstanbul": ["Adalar", "Arnavutköy", "Ataşehir", "Avcılar", "Bağcılar", "Bahçelievler", "Bakırköy", "Başakşehir", "Bayrampaşa", "Beşiktaş", "Beykoz", "Beylikdüzü", "Beyoğlu", "Büyükçekmece", "Çatalca", "Çekmeköy", "Esenler", "Esenyurt", "Eyüpsultan", "Fatih", "Gaziosmanpaşa", "Güngören", "Kadıköy", "Kağıthane", "Kartal", "Küçükçekmece", "Maltepe", "Pendik", "Sancaktepe", "Sarıyer", "Silivri", "Sultanbeyli", "Sultangazi", "Tuzla", "Ümraniye", "Üsküdar", "Zeytinburnu"],
    "Ankara": ["Akyurt", "Altındağ", "Ayaş", "Bala", "Beypazarı", "Çamlıdere", "Çankaya", "Çubuk", "Elmadağ", "Etimesgut", "Evren", "Gölbaşı", "Hasköy", "Haymana", "Kahramankazan", "Kalecik", "Keçiören", "Kızılcahamam", "Mamak", "Nallıhan", "Polatlı", "Pursaklar", "Sincan", "Şereflikoçhisar", "Yenimahalle"],
    "İzmir": ["Aliağa", "Balçova", "Bayındır", "Bayraklı", "Bergama", "Beydağ", "Bornova", "Buca", "Çeşme", "Çiğli", "Dikili", "Foça", "Gaziemir", "Güzelbahçe", "Karabağlar", "Karaburun", "Karşıyaka", "Kemalpaşa", "Kınık", "Kiraz", "Konak", "Menderes", "Menemen", "Narlıdere", "Ödemiş", "Seferihisar", "Selçuk", "Tire", "Torbalı", "Urla"],
    "Bursa": ["Nilüfer", "Osmangazi", "Yıldırım", "İnegöl", "Gemlik", "Bandırma", "Mudanya", "Kestel", "Gürsu"],
    "Antalya": ["Akseki", "Aksu", "Alanya", "Demre", "Döşemealtı", "Elmalı", "Finike", "Gazipaşa", "Gündoğmuş", "İbradı", "Kaş", "Kemer", "Kepez", "Konyaaltı", "Korkuteli", "Kumluca", "Manavgat", "Muratpaşa", "Serik"],
    "Adana": ["Seyhan", "Yüreğir", "Çukurova", "Sarıçam", "Ceyhan", "Kozan"],
    "Konya": ["Selçuklu", "Meram", "Karatay", "Ereğli", "Akşehir", "Beyşehir"],
    "Gaziantep": ["Şahinbey", "Şehitkamil", "Nizip", "İslahiye"],
    "Diğer": ["Merkez / Diğer İlçe"]
}

# =========================================================
#  STİL
# =========================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #FBF8F3 !important; color: #2C2A29 !important; }
    [data-testid="stSidebar"] { background-color: #F4EFEA !important; border-right: 1px solid #E6DFD5; }
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: #3E332B !important; }
    input, textarea, select { background-color: #FFFFFF !important; color: #2C2A29 !important; border-radius: 8px !important; border: 1px solid #D4C9BC !important; }
    .stButton>button { background-color: #BC6C25 !important; color: #FFFFFF !important; font-weight: 600; border-radius: 8px; border: none; padding: 0.5rem 1rem; transition: all 0.15s ease-in-out; }
    .stButton>button:hover { background-color: #9C5419 !important; color: #FFFFFF !important; transform: translateY(-1px); box-shadow: 0 3px 8px rgba(0,0,0,0.15); }
    .stButton>button:disabled { background-color: #D9CFC2 !important; color: #8C7A6B !important; transform: none; box-shadow: none; }
    .product-card { background: #FFFFFF; border-radius: 14px; overflow: hidden; border: 1px solid #ECE4D8; box-shadow: 0 3px 10px rgba(74,59,50,0.06); transition: box-shadow 0.2s ease, transform 0.2s ease; margin-bottom: 14px; }
    .product-card:hover { box-shadow: 0 8px 20px rgba(74,59,50,0.14); transform: translateY(-2px); }
    .product-badge { display: inline-block; background: #F4EFEA; color: #8C5A2B; font-size: 11px; font-weight: 600; padding: 2px 10px; border-radius: 20px; margin-bottom: 4px; letter-spacing: 0.3px; }
    .stock-low { color: #B3401D; font-weight: 600; font-size: 12px; }
    .stock-out { color: #A3A3A3; font-weight: 600; font-size: 12px; }
    .slider-wrapper { overflow: hidden; width: 100%; background: linear-gradient(135deg, #E6DFD5, #F5F1EB); padding: 20px 0; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
    .slider-track { display: flex; gap: 20px; width: max-content; animation: scrollAuto 30s linear infinite; }
    .slider-wrapper:hover .slider-track { animation-play-state: paused; }
    .slide-item { width: 240px; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.08); border: 1px solid #E6DFD5; text-align: center; padding-bottom: 12px; flex-shrink: 0; }
    .slide-item img { width: 100%; height: 160px; object-fit: cover; }
    .slide-title { font-family: 'Playfair Display', serif; font-weight: 700; color: #4A3B32; font-size: 15px; margin: 10px 5px 5px 5px; }
    @keyframes scrollAuto { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
    h1, h2, h3 { font-family: 'Playfair Display', serif; }
    .verify-banner { background:#FFF4E5; border:1px solid #F0C68A; padding:12px 16px; border-radius:10px; color:#7A4A12; font-size:14px; margin-bottom:10px; }
    </style>
""", unsafe_allow_html=True)

# =========================================================
#  VERİTABANI (SQLite)
# =========================================================
def get_conn():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            description TEXT,
            image_url TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            verified INTEGER NOT NULL DEFAULT 0,
            verify_token TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            title TEXT,
            city TEXT,
            district TEXT,
            neighborhood TEXT,
            postal_code TEXT,
            detail TEXT,
            phone TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            timestamp TEXT,
            user_email TEXT,
            user_name TEXT,
            items_json TEXT,
            total REAL,
            address_json TEXT,
            status TEXT
        )
    """)
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM products")
    if cur.fetchone()[0] == 0:
        seed = [
            ("Surreal Bakış & Rüya Odası", "Baş Yapıt", 2500.0, 1, "Sanatçının elinden çıkan orijinal başyapıt.", "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?auto=format&fit=crop&w=600&q=80"),
            ("Soyut Düşler (Tuval Baskı)", "Baskı", 450.0, 5, "Yüksek kaliteli mat kuşe kağıda sınırlı sayıdaki imzalı baskı.", "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=600&q=80"),
            ("Suluboya Botanik Serisi", "Suluboya", 350.0, 4, "Özel suluboya kağıdı üzerine el yapımı botanik illüstrasyon.", "https://images.unsplash.com/photo-1541701494587-cb58502866ab?auto=format&fit=crop&w=600&q=80"),
            ("Portre Çalışması - 01", "Portre", 900.0, 2, "Detaylı portre çalışması.", "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=600&q=80"),
        ]
        cur.executemany("INSERT INTO products (title, category, price, stock, description, image_url) VALUES (?,?,?,?,?,?)", seed)
        conn.commit()

    conn.close()

init_db()


def fetch_df(query, params=()):
    conn = get_conn()
    try:
        return pd.read_sql_query(query, conn, params=params)
    finally:
        conn.close()

def run_query(query, params=()):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def load_products():
    return fetch_df("SELECT * FROM products")

def load_users():
    return fetch_df("SELECT * FROM users")

def load_addresses(email=None):
    if email:
        return fetch_df("SELECT * FROM addresses WHERE email = ?", (email,))
    return fetch_df("SELECT * FROM addresses")

def load_orders(email=None):
    if email:
        return fetch_df("SELECT * FROM orders WHERE user_email = ?", (email,))
    return fetch_df("SELECT * FROM orders")


# =========================================================
#  GÜVENLİK
# =========================================================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def is_valid_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email or ""))


# =========================================================
#  UYGULAMA URL'Sİ (doğrulama linki için)
# =========================================================
def get_app_url():
    try:
        url = st.secrets.get("APP_URL", os.environ.get("APP_URL"))
    except Exception:
        url = os.environ.get("APP_URL")
    return url or "http://localhost:8501"


# =========================================================
#  E-POSTA
# =========================================================
def get_smtp_config():
    """.streamlit/secrets.toml içine ekleyin:
    SMTP_EMAIL = "your@gmail.com"
    SMTP_PASSWORD = "16-haneli-uygulama-sifresi"
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    APP_URL = "https://uygulama-adresiniz.streamlit.app"
    """
    try:
        email = st.secrets.get("SMTP_EMAIL", os.environ.get("SMTP_EMAIL"))
        password = st.secrets.get("SMTP_PASSWORD", os.environ.get("SMTP_PASSWORD"))
        server = st.secrets.get("SMTP_SERVER", os.environ.get("SMTP_SERVER", "smtp.gmail.com"))
        port = int(st.secrets.get("SMTP_PORT", os.environ.get("SMTP_PORT", 587)))
    except Exception:
        email = os.environ.get("SMTP_EMAIL")
        password = os.environ.get("SMTP_PASSWORD")
        server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        port = int(os.environ.get("SMTP_PORT", 587))

    if not email or not password:
        return None
    return {"email": email, "password": password, "server": server, "port": port}


def send_real_email(to_email: str, subject: str, body_text: str, body_html: str = None) -> bool:
    config = get_smtp_config()
    if not config:
        print("[UYARI] SMTP bilgileri tanımlı değil (.streamlit/secrets.toml). E-posta gönderilemedi.")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = config["email"]
        msg["To"] = to_email
        msg.attach(MIMEText(body_text, "plain", "utf-8"))
        if body_html:
            msg.attach(MIMEText(body_html, "html", "utf-8"))
        with smtplib.SMTP(config["server"], config["port"], timeout=15) as server:
            server.starttls()
            server.login(config["email"], config["password"])
            server.sendmail(config["email"], to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[HATA] Mail gönderilemedi -> {to_email}: {e}")
        return False


def send_verification_email(name: str, email: str, token: str) -> bool:
    link = f"{get_app_url()}/?verify_token={token}"
    body = f"""Sayın {name},

YARENART'a üyeliğiniz için son bir adım kaldı. Hesabınızı doğrulamak için aşağıdaki bağlantıya tıklayın:

{link}

Bu bağlantıyı siz talep etmediyseniz bu e-postayı yok sayabilirsiniz.

YARENART Ekibi"""
    html = f"""<p>Sayın {name},</p>
<p>YARENART'a üyeliğiniz için son bir adım kaldı. Hesabınızı doğrulamak için aşağıdaki bağlantıya tıklayın:</p>
<p><a href="{link}" style="background:#BC6C25;color:#fff;padding:10px 18px;border-radius:6px;text-decoration:none;">Hesabımı Doğrula</a></p>
<p>Bu bağlantıyı siz talep etmediyseniz bu e-postayı yok sayabilirsiniz.</p>
<p>YARENART Ekibi</p>"""
    return send_real_email(email, "YARENART - Hesabınızı Doğrulayın", body, html)


# =========================================================
#  OTURUM DURUMU
# =========================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "cart" not in st.session_state:
    st.session_state.cart = []

def add_to_cart(product_id, title, price, stock, qty=1):
    for item in st.session_state.cart:
        if item["id"] == product_id:
            if item["qty"] + qty > stock:
                st.warning(f"Stokta yalnızca {stock} adet var.")
                return
            item["qty"] += qty
            st.success("Sepet güncellendi!")
            return
    if qty > stock:
        st.warning(f"Stokta yalnızca {stock} adet var.")
        return
    st.session_state.cart.append({"id": product_id, "title": title, "price": price, "qty": qty})
    st.success("Sepete eklendi!")


# =========================================================
#  E-POSTA DOĞRULAMA LİNKİ İŞLEME (?verify_token=...)
# =========================================================
qp = st.query_params
if "verify_token" in qp:
    token = qp["verify_token"]
    users_df = load_users()
    match = users_df[users_df["verify_token"] == token]
    if not match.empty:
        run_query("UPDATE users SET verified = 1, verify_token = NULL WHERE verify_token = ?", (token,))
        st.success("✅ E-posta adresiniz doğrulandı! Artık giriş yapabilirsiniz.")
    else:
        st.error("Geçersiz veya süresi dolmuş doğrulama bağlantısı.")
    st.query_params.clear()
    st.stop()

# =========================================================
#  BAŞLIK
# =========================================================
st.markdown("""
    <div style='text-align: center; padding: 10px 0;'>
        <h1 style='font-size: 52px; font-weight: 700; color: #4A3B32; letter-spacing: 2px;'>✨ YARENART ✨</h1>
        <p style='color: #8C7A6B; font-size: 18px; font-style: italic;'>Ressamın Elinden Sanatsal Dokunuşlar & Tablolar</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="slider-wrapper">
        <div class="slider-track">
            <div class="slide-item"><img src="https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?auto=format&fit=crop&w=500&q=80"><div class="slide-title">Surreal Başyapıt</div></div>
            <div class="slide-item"><img src="https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=500&q=80"><div class="slide-title">Soyut Düşler</div></div>
            <div class="slide-item"><img src="https://images.unsplash.com/photo-1541701494587-cb58502866ab?auto=format&fit=crop&w=500&q=80"><div class="slide-title">Botanik Serisi</div></div>
            <div class="slide-item"><img src="https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=500&q=80"><div class="slide-title">Portre Çalışması</div></div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.divider()

# =========================================================
#  SIDEBAR: KULLANICI & HESAP
# =========================================================
st.sidebar.header("👤 Kullanıcı & Hesap")

if not st.session_state.logged_in:
    auth_mode = st.sidebar.radio("İşlem Seçin", ["Giriş Yap", "Üye Ol"], key="auth_mode_radio")

    if auth_mode == "Üye Ol":
        name_input = st.sidebar.text_input("Ad Soyad", key="reg_name")
        email_input = st.sidebar.text_input("E-posta Adresi", key="reg_email")
        pass_input = st.sidebar.text_input("Şifre", type="password", key="reg_pass")
    else:
        email_input = st.sidebar.text_input("E-posta Adresi", key="login_email")
        pass_input = st.sidebar.text_input("Şifre", type="password", key="login_pass")

    users_df = load_users()

    if auth_mode == "Üye Ol":
        if st.sidebar.button("Kayıt Ol", key="btn_register"):
            if not (name_input and email_input and pass_input):
                st.sidebar.warning("Lütfen tüm alanları doldurun.")
            elif not is_valid_email(email_input):
                st.sidebar.warning("Lütfen geçerli bir e-posta adresi girin.")
            elif len(pass_input) < 6:
                st.sidebar.warning("Şifre en az 6 karakter olmalı.")
            elif email_input in users_df["email"].values:
                st.sidebar.warning("Bu e-posta zaten kayıtlı!")
            else:
                token = uuid.uuid4().hex
                run_query(
                    "INSERT INTO users (name, email, password_hash, verified, verify_token) VALUES (?,?,?,0,?)",
                    (name_input, email_input, hash_password(pass_input), token)
                )
                mail_ok = send_verification_email(name_input, email_input, token)
                if mail_ok:
                    st.sidebar.success("Kayıt alındı! Doğrulama bağlantısı e-postanıza gönderildi.")
                else:
                    st.sidebar.warning("Kayıt alındı ama doğrulama e-postası gönderilemedi (SMTP ayarlarını kontrol edin).")
    else:
        if st.sidebar.button("Giriş Yap", key="btn_login"):
            hashed = hash_password(pass_input) if pass_input else ""
            matched = users_df[(users_df["email"] == email_input) & (users_df["password_hash"] == hashed)]
            if matched.empty:
                st.sidebar.error("Hatalı e-posta veya şifre!")
            elif matched.iloc[0]["verified"] != 1:
                st.sidebar.warning("Hesabınız henüz doğrulanmamış. E-postanızı kontrol edin.")
                if st.sidebar.button("Doğrulama e-postasını tekrar gönder", key="resend_verify"):
                    new_token = uuid.uuid4().hex
                    run_query("UPDATE users SET verify_token = ? WHERE email = ?", (new_token, email_input))
                    if send_verification_email(matched.iloc[0]["name"], email_input, new_token):
                        st.sidebar.success("Doğrulama e-postası tekrar gönderildi.")
                    else:
                        st.sidebar.error("E-posta gönderilemedi. SMTP ayarlarını kontrol edin.")
            else:
                st.session_state.logged_in = True
                st.session_state.user_name = matched.iloc[0]["name"]
                st.session_state.user_email = email_input
                st.sidebar.success("Giriş başarılı!")
                st.rerun()
else:
    st.sidebar.markdown(f"<p style='color: #4A3B32; font-weight: bold; font-size: 16px;'>Hoş geldin, {st.session_state.user_name}</p>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='color: #6C5B52; font-size: 13px;'>{st.session_state.user_email}</p>", unsafe_allow_html=True)

    with st.sidebar.expander("➕ Yeni Adres Kaydet"):
        addr_title = st.text_input("Adres Başlığı (Örn: Ev, İş)", key="new_addr_title")
        addr_city = st.selectbox("İl", list(TURKEY_CITIES.keys()), key="new_addr_city")
        addr_district = st.selectbox("İlçe", TURKEY_CITIES[addr_city], key="new_addr_dist")
        addr_neigh = st.text_input("Mahalle", key="new_addr_neigh")
        addr_postal = st.text_input("Posta Kodu", key="new_addr_postal")
        addr_phone = st.text_input("İletişim Telefonu", key="new_addr_phone")
        addr_detail = st.text_area("Cadde, Sokak, Bina No / Daire", key="new_addr_detail")

        if st.button("Adresi Kaydet", key="btn_save_addr"):
            if addr_title and addr_neigh and addr_detail:
                run_query(
                    "INSERT INTO addresses (email, title, city, district, neighborhood, postal_code, detail, phone) VALUES (?,?,?,?,?,?,?,?)",
                    (st.session_state.user_email, addr_title, addr_city, addr_district, addr_neigh, addr_postal, addr_detail, addr_phone)
                )
                st.success("Adres başarıyla kaydedildi!")
            else:
                st.warning("Lütfen başlık, mahalle ve adres detayını doldurun.")

    with st.sidebar.expander("📦 Siparişlerim"):
        my_orders = load_orders(st.session_state.user_email)
        if my_orders.empty:
            st.write("Henüz siparişiniz yok.")
        else:
            for _, o in my_orders.sort_values("timestamp", ascending=False).iterrows():
                st.markdown(f"**#{o['order_id']}** — {o['timestamp']}")
                st.write(f"Tutar: {o['total']:.2f} TL — Durum: {o['status']}")
                st.markdown("---")

    if st.sidebar.button("Çıkış Yap", key="btn_logout"):
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.session_state.user_email = ""
        st.rerun()

st.sidebar.divider()

# =========================================================
#  SEPET
# =========================================================
st.sidebar.subheader("🛒 Sepetim")

if len(st.session_state.cart) > 0:
    total_price = 0.0
    for idx, item in enumerate(list(st.session_state.cart)):
        subtotal = item["price"] * item["qty"]
        total_price += subtotal
        c1, c2, c3 = st.sidebar.columns([3, 2, 1])
        c1.write(f"**{item['title']}**")
        c1.caption(f"{item['price']:,.2f} TL x {item['qty']} = {subtotal:,.2f} TL")
        new_qty = c2.number_input("Adet", min_value=1, value=int(item["qty"]), key=f"qty_{item['id']}", label_visibility="collapsed")
        if new_qty != item["qty"]:
            item["qty"] = new_qty
            st.rerun()
        if c3.button("✕", key=f"remove_{item['id']}"):
            st.session_state.cart.pop(idx)
            st.rerun()

    st.sidebar.markdown(f"**Toplam Tutar: {total_price:,.2f} TL**")

    if st.sidebar.button("🗑️ Sepeti Temizle", key="btn_clear_cart"):
        st.session_state.cart = []
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("📦 Teslimat Adresi")

    if not st.session_state.logged_in:
        st.sidebar.warning("Sipariş vermek için önce giriş yapmalısınız!")
    else:
        user_addrs = load_addresses(st.session_state.user_email)

        selected_address_info = None
        chosen_addr_title = "Yeni Adres Gir..."

        if not user_addrs.empty:
            addr_options = [f"{row['title']} - {row['city']}/{row['district']}" for _, row in user_addrs.iterrows()]
            chosen_addr_title = st.sidebar.selectbox("Kayıtlı Adreslerim", ["Yeni Adres Gir..."] + addr_options, key="select_saved_addr")

            if chosen_addr_title != "Yeni Adres Gir...":
                selected_row = user_addrs.iloc[addr_options.index(chosen_addr_title)]
                selected_address_info = {
                    "city": selected_row["city"], "district": selected_row["district"],
                    "neighborhood": selected_row["neighborhood"], "postal_code": selected_row["postal_code"],
                    "detail": selected_row["detail"], "phone": selected_row["phone"]
                }

        if user_addrs.empty or chosen_addr_title == "Yeni Adres Gir...":
            ship_phone = st.sidebar.text_input("Telefon Numarası", key="ord_phone")
            ship_city = st.sidebar.selectbox("Şehir (İl)", list(TURKEY_CITIES.keys()), key="ord_city")
            ship_district = st.sidebar.selectbox("İlçe", TURKEY_CITIES[ship_city], key="ord_dist")
            ship_neighborhood = st.sidebar.text_input("Mahalle", key="ord_neigh")
            ship_postal = st.sidebar.text_input("Posta Kodu", key="ord_postal")
            ship_address_detail = st.sidebar.text_area("Cadde, Sokak, Bina No / Daire", key="ord_detail")

            if ship_phone and ship_neighborhood and ship_address_detail:
                selected_address_info = {
                    "city": ship_city, "district": ship_district, "neighborhood": ship_neighborhood,
                    "postal_code": ship_postal, "detail": ship_address_detail, "phone": ship_phone
                }

        if st.sidebar.button("Siparişi Tamamla ve Onayla", key="btn_confirm_order"):
            if not selected_address_info:
                st.sidebar.error("Lütfen eksiksiz bir teslimat adresi belirtin veya kayıtlı adres seçin.")
            else:
                product_df = load_products()
                stock_problem = False
                for item in st.session_state.cart:
                    row = product_df[product_df["id"] == item["id"]]
                    if row.empty or row.iloc[0]["stock"] < item["qty"]:
                        st.sidebar.error(f"'{item['title']}' için yeterli stok yok.")
                        stock_problem = True

                if not stock_problem:
                    order_id = uuid.uuid4().hex[:8].upper()
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    for item in st.session_state.cart:
                        run_query("UPDATE products SET stock = stock - ? WHERE id = ?", (item["qty"], item["id"]))

                    run_query(
                        "INSERT INTO orders (order_id, timestamp, user_email, user_name, items_json, total, address_json, status) VALUES (?,?,?,?,?,?,?,?)",
                        (order_id, timestamp, st.session_state.user_email, st.session_state.user_name,
                         json.dumps(st.session_state.cart, ensure_ascii=False), total_price,
                         json.dumps(selected_address_info, ensure_ascii=False), "Alındı")
                    )

                    order_summary = f"""Sayın {st.session_state.user_name},

YARENART mağazasından verdiğiniz sipariş başarıyla alınmıştır!

Sipariş No: {order_id}
Tarih: {timestamp}

Teslimat Adresi:
{selected_address_info['neighborhood']} Mah. {selected_address_info['detail']}
{selected_address_info['district']} / {selected_address_info['city']} - Posta Kodu: {selected_address_info['postal_code']}
Telefon: {selected_address_info['phone']}

Sipariş Edilen Ürünler:
"""
                    for item in st.session_state.cart:
                        order_summary += f"- {item['title']} x{item['qty']} ({item['price'] * item['qty']:,.2f} TL)\n"
                    order_summary += f"\nToplam Tutar: {total_price:,.2f} TL\n\nBizi tercih ettiğiniz için teşekkür ederiz!\nYARENART"

                    admin_ok = send_real_email(ADMIN_EMAIL, f"Yeni Sipariş Alındı - #{order_id}", order_summary)
                    customer_ok = send_real_email(st.session_state.user_email, f"Siparişiniz Alındı - #{order_id} - YARENART", order_summary)

                    st.sidebar.success(f"Siparişiniz oluşturuldu! Sipariş No: {order_id}")
                    if not (admin_ok and customer_ok):
                        st.sidebar.info("Not: Sipariş kaydedildi, ancak e-posta bildirimi gönderilemedi (SMTP ayarlarını kontrol edin).")
                    st.balloons()
                    st.session_state.cart = []
                    st.rerun()
else:
    st.sidebar.write("Sepetiniz boş.")

# =========================================================
#  ANA EKRAN: VİTRİN
# =========================================================
df = load_products()

st.markdown("### 🎨 Tüm Sanat Eserleri")
selected_cat = st.selectbox("Kategoriye Göre Filtrele", ["Tümü", "Soyut Kanvas", "Baş Yapıt", "Siyah Beyaz", "Manzara", "Özel Seri", "Baskı", "Suluboya", "Portre"], key="filter_cat")

display_df = df if selected_cat == "Tümü" else df[df["category"] == selected_cat]
products_list = display_df.to_dict('records')

is_admin = st.session_state.logged_in and st.session_state.user_email == ADMIN_EMAIL

total_slots = len(products_list) + (1 if is_admin else 0)
num_cols = 4

for i in range(0, total_slots, num_cols):
    cols = st.columns(num_cols)
    for col_idx in range(num_cols):
        item_index = i + col_idx
        if item_index < len(products_list):
            row = products_list[item_index]
            with cols[col_idx]:
                st.markdown('<div class="product-card">', unsafe_allow_html=True)
                st.image(row["image_url"], use_container_width=True)
                st.markdown(f"<div style='padding: 0 12px;'><span class='product-badge'>{row['category']}</span></div>", unsafe_allow_html=True)
                st.markdown(f"<div style='padding: 0 12px;'><b>{row['title']}</b></div>", unsafe_allow_html=True)
                st.markdown(f"<div style='padding: 0 12px 8px 12px; font-size:17px; font-weight:700; color:#BC6C25;'>{row['price']:,.2f} TL</div>", unsafe_allow_html=True)

                stock = int(row["stock"])
                if stock <= 0:
                    st.markdown("<div style='padding: 0 12px;'><span class='stock-out'>Stokta yok</span></div>", unsafe_allow_html=True)
                    st.button("Sepete Ekle", key=f"product_{row['id']}", disabled=True)
                else:
                    if stock <= 2:
                        st.markdown(f"<div style='padding: 0 12px;'><span class='stock-low'>Son {stock} adet!</span></div>", unsafe_allow_html=True)
                    qty = st.number_input("Adet", min_value=1, max_value=stock, value=1, key=f"qty_input_{row['id']}", label_visibility="collapsed")
                    if st.button("Sepete Ekle", key=f"product_{row['id']}"):
                        add_to_cart(row['id'], row['title'], row['price'], stock, qty)

                st.markdown('</div>', unsafe_allow_html=True)

                if is_admin:
                    with st.expander(f"⚙️ Yönet: {row['title']}"):
                        new_p = st.number_input("Fiyat Güncelle (TL)", value=float(row['price']), key=f"p_{row['id']}")
                        new_stock = st.number_input("Stok Güncelle", min_value=0, value=int(row['stock']), key=f"s_{row['id']}")
                        if st.button("Değişiklikleri Kaydet", key=f"save_p_{row['id']}"):
                            run_query("UPDATE products SET price = ?, stock = ? WHERE id = ?", (new_p, new_stock, row['id']))
                            st.success("Ürün güncellendi!")
                            st.rerun()

                        if st.button("🗑️ Ürünü Kaldır", key=f"del_{row['id']}"):
                            run_query("DELETE FROM products WHERE id = ?", (row['id'],))
                            st.warning("Ürün silindi!")
                            st.rerun()

        elif is_admin and item_index == len(products_list):
            with cols[col_idx]:
                st.markdown("""
                    <div style='border: 2px dashed #D4A373; border-radius: 12px; padding: 40px 10px; text-align: center; background-color: #FAF6F0; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center;'>
                        <h1 style='color: #D4A373; margin: 0; font-size: 40px;'>+</h1>
                        <p style='color: #8C7A6B; font-weight: bold; margin-top: 10px;'>Yeni Ürün Ekle</p>
                    </div>
                """, unsafe_allow_html=True)

                image_mode = st.radio("Görsel Kaynağı", ["Bilgisayardan Yükle", "URL ile Ekle"], key="img_mode_choice", horizontal=True)

                with st.form(key=f"add_slot_form_{item_index}"):
                    n_title = st.text_input("Eser Adı", placeholder="Tablo adı...")
                    n_cat = st.selectbox("Kategori", ["Baş Yapıt", "Soyut Kanvas", "Baskı", "Suluboya", "Portre", "Siyah Beyaz", "Manzara"], key="n_cat_box")
                    n_price = st.number_input("Fiyat (TL)", min_value=0.0, value=1000.0)
                    n_stock = st.number_input("Stok Adedi", min_value=0, value=1)
                    n_desc = st.text_input("Kısa Açıklama", placeholder="Örn: Tuval üzerine akrilik...")

                    n_img_file = None
                    n_img_url = ""
                    if image_mode == "Bilgisayardan Yükle":
                        n_img_file = st.file_uploader("Görsel Seç", type=["png", "jpg", "jpeg", "webp"])
                    else:
                        n_img_url = st.text_input("Görsel URL", placeholder="https://...")

                    submitted_slot = st.form_submit_button("Vitrine Ekle 🚀")
                    if submitted_slot:
                        final_image_path = n_img_url
                        new_id = None
                        if n_title and (n_img_file is not None or n_img_url):
                            new_id = run_query(
                                "INSERT INTO products (title, category, price, stock, description, image_url) VALUES (?,?,?,?,?,?)",
                                (n_title, n_cat, n_price, n_stock, n_desc, "")
                            )
                            if image_mode == "Bilgisayardan Yükle" and n_img_file is not None:
                                ext = os.path.splitext(n_img_file.name)[1]
                                saved_path = os.path.join(UPLOAD_DIR, f"product_{new_id}{ext}")
                                with open(saved_path, "wb") as f:
                                    f.write(n_img_file.getbuffer())
                                final_image_path = saved_path
                            run_query("UPDATE products SET image_url = ? WHERE id = ?", (final_image_path, new_id))
                            st.success("Yeni ürün vitrine eklendi!")
                            st.rerun()
                        else:
                            st.warning("Eser adı ve görsel (dosya veya URL) zorunludur.")

# =========================================================
#  WHATSAPP & FOOTER
# =========================================================
whatsapp_url = f"https://wa.me/{WHATSAPP_PHONE}?text=Merhaba%2C%20YARENART%20ürünleri%20hakkında%20bilgi%20almak%20istiyorum."

st.markdown(f"""
    <a href="{whatsapp_url}" target="_blank" style="position: fixed; bottom: 30px; right: 30px; z-index: 9999; background-color: #25D366; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 2px 4px 12px rgba(0,0,0,0.25); text-decoration: none;">
        <svg viewBox="0 0 32 32" width="36" height="36" fill="white">
            <path d="M16.5 3C9.04 3 3 9.04 3 16.5c0 2.37.62 4.63 1.74 6.6L3 29l6.11-1.6c1.9 1.03 4.12 1.6 6.39 1.6 7.46 0 13.5-6.04 13.5-13.5S23.96 3 16.5 3zm0 24.5c-1.99 0-3.87-.56-5.46-1.53l-.39-.23-3.61.95.97-3.52-.25-.41A10.98 10.98 0 015.5 16.5C5.5 10.48 10.48 5.5 16.5 5.5S27.5 10.48 27.5 16.5 22.52 27.5 16.5 27.5zm6.05-8.24c-.33-.17-1.95-.96-2.25-1.07-.3-.11-.52-.17-.74.17-.22.33-.85 1.07-1.04 1.29-.19.22-.38.25-.71.08-.33-.17-1.4-.52-2.67-1.65-.99-.88-1.66-1.97-1.85-2.3-.19-.33-.02-.51.14-.68.15-.15.33-.38.5-.57.17-.19.22-.33.33-.55.11-.22.06-.41-.03-.57-.09-.17-.74-1.78-1.01-2.44-.27-.64-.54-.55-.74-.56h-.63c-.22 0-.57.08-.87.41-.3.33-1.14 1.11-1.14 2.72 0 1.61 1.17 3.17 1.33 3.39.17.22 2.3 3.51 5.57 4.92.78.34 1.39.54 1.87.69.79.25 1.51.21 2.08.13.64-.1 1.95-.8 2.23-1.57.28-.77.28-1.43.2-1.57-.08-.14-.3-.22-.63-.39z"/>
        </svg>
    </a>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown(f"""
### 📞 YARENART İletişim & Destek
- **WhatsApp Destek Hattı:** [{WHATSAPP_PHONE}](https://wa.me/{WHATSAPP_PHONE})
- **E-posta:** `{ADMIN_EMAIL}`
- **Instagram:** [@yarenart](https://instagram.com)
- **Atölye Konumu:** İstanbul / Kadıköy
""")
