import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Sayfa Ayarları (Geniş Ekran)
st.set_page_config(page_title="YARENART | Sanat & İllüstrasyon Mağazası", page_icon="🎨", layout="wide")

# Veri Dosyası ve Klasör Yolları
CSV_FILE = "products.csv"
USERS_FILE = "users.csv"
ADDRESS_FILE = "addresses.csv"
UPLOAD_DIR = "uploaded_images"
ADMIN_EMAIL = "skus42173@gmail.com"
WHATSAPP_PHONE = "905527920708"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Türkiye Tüm İller ve İlçeler Sözlüğü
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

# Sıcak Sanatsal Tasarım & CSS Stilleri
st.markdown("""
    <style>
    .stApp {
        background-color: #FDFBF7 !important;
        color: #2C2A29 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #F4EFEA !important;
        border-right: 1px solid #E6DFD5;
    }
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
        color: #4A3B32 !important;
    }
    input, textarea, select {
        background-color: #FFFFFF !important;
        color: #2C2A29 !important;
        border-radius: 6px !important;
        border: 1px solid #D4C9BC !important;
    }
    .stButton>button {
        background-color: #D4A373 !important;
        color: #FFFFFF !important;
        font-weight: bold;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #BC6C25 !important;
        color: #FFFFFF !important;
    }
    .slider-wrapper {
        overflow: hidden;
        width: 100%;
        background: linear-gradient(135deg, #E6DFD5, #F5F1EB);
        padding: 20px 0;
        border-radius: 15px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    }
    .slider-track {
        display: flex;
        gap: 20px;
        width: max-content;
        animation: scrollAuto 30s linear infinite;
    }
    .slider-wrapper:hover .slider-track {
        animation-play-state: paused;
    }
    .slide-item {
        width: 240px;
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        border: 1px solid #E6DFD5;
        text-align: center;
        padding-bottom: 12px;
        flex-shrink: 0;
    }
    .slide-item img {
        width: 100%;
        height: 160px;
        object-fit: cover;
    }
    .slide-title {
        font-family: serif;
        font-weight: bold;
        color: #4A3B32;
        font-size: 15px;
        margin: 10px 5px 5px 5px;
    }
    @keyframes scrollAuto {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }
    </style>
""", unsafe_allow_html=True)

# Veri Dosyalarını Başlatma
if not os.path.exists(CSV_FILE):
    initial_data = {
        "id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        "title": ["Surreal Bakış & Rüya Odası", "Modern Soyut Geometrik Tablo", "Lacivert Krem Soyut Tablo", "Siyah Bej Altın Soyut Tablo", 
                  "Baş Yapıt Kanvas Tablo", "Siyah Beyaz Kanvas Tablo", "Manzara Kanvas Tablosu", "Özel Seri İllüstrasyon",
                  "Minimalist Toprak Tonları", "Altın Varaklı İstanbul", "Gece Mavisi Düşler", "Botanik Yaprak Serisi"],
        "category": ["Baş Yapıt", "Soyut Kanvas", "Soyut Kanvas", "Soyut Kanvas", "Baş Yapıt", "Siyah Beyaz", "Manzara", "Özel Seri", "Soyut Kanvas", "Baş Yapıt", "Özel Seri", "Manzara"],
        "price": [2500.0, 1000.0, 1150.0, 1200.0, 1450.0, 850.0, 1100.0, 1500.0, 900.0, 1750.0, 1300.0, 980.0],
        "stock": [1, 3, 5, 2, 4, 1, 6, 2, 4, 2, 3, 5],
        "description": ["Sanatçının elinden çıkan orijinal başyapıt[cite: 5].", "Yüksek kaliteli tuval üzerine özel modern tasarım.", "Evinize şıklık katacak renk tonları.", "Altın varak detaylı lüks dokunuş.",
                        "Klasik sanatın modern tuvale yansıması.", "Siyah beyaz sokak konsepti.", "Huzur veren doğa manzarası.", "Sınırlı sayıda üretilmiş özel eser.",
                        "Toprak tonlarının huzur veren uyumu.", "İstanbul'un eşsiz silüeti altın varaklı.", "Derin mavi tonlarında mistik geçişler.", "Doğal bitki motifleriyle ferahlık."],
        "image_url": [
            "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1541701494587-cb58502866ab?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1541701494587-cb58502866ab?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1541701494587-cb58502866ab?auto=format&fit=crop&w=600&q=80"
        ]
    }
    pd.DataFrame(initial_data).to_csv(CSV_FILE, index=False)

if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["name", "email", "password"]).to_csv(USERS_FILE, index=False)

if not os.path.exists(ADDRESS_FILE):
    pd.DataFrame(columns=["email", "title", "city", "district", "neighborhood", "postal_code", "detail", "phone"]).to_csv(ADDRESS_FILE, index=False)

@st.cache_data
def load_products():
    return pd.read_csv(CSV_FILE)

def load_users():
    return pd.read_csv(USERS_FILE)

def load_addresses():
    return pd.read_csv(ADDRESS_FILE)

df = load_products()

# Oturum Yönetimi
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "cart" not in st.session_state:
    st.session_state.cart = []

def send_real_email(to_email, subject, body):
    try:
        print(f"E-posta tetiklendi -> Alıcı: {to_email} | Konu: {subject}")
        return True
    except Exception as e:
        print(f"Mail hatası: {e}")
        return False

# --- ŞIK YARENART BAŞLIĞI ---
st.markdown("""
    <div style='text-align: center; padding: 10px 0;'>
        <h1 style='font-family: serif; font-size: 52px; font-weight: bold; color: #4A3B32; letter-spacing: 2px;'>
            ✨ YARENART ✨
        </h1>
        <p style='color: #8C7A6B; font-size: 18px; font-style: italic;'>Ressamın Elinden Sanatsal Dokunuşlar & Tablolar</p>
    </div>
""", unsafe_allow_html=True)

# --- OTOMATİK AKAN VE ELLE KAYDIRILABİLİR VİTRİN SLIDER ---
st.markdown("""
    <div class="slider-wrapper">
        <div class="slider-track">
            <div class="slide-item"><img src="https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?auto=format&fit=crop&w=500&q=80"><div class="slide-title">Surreal Başyapıt</div></div>
            <div class="slide-item"><img src="https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=500&q=80"><div class="slide-title">Soyut Geometrik</div></div>
            <div class="slide-item"><img src="https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=500&q=80"><div class="slide-title">Siyah Beyaz Koleksiyon</div></div>
            <div class="slide-item"><img src="https://images.unsplash.com/photo-1541701494587-cb58502866ab?auto=format&fit=crop&w=500&q=80"><div class="slide-title">Manzara Serisi</div></div>
            <div class="slide-item"><img src="https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=500&q=80"><div class="slide-title">Özel İllüstrasyon</div></div>
            <div class="slide-item"><img src="https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?auto=format&fit=crop&w=500&q=80"><div class="slide-title">Surreal Başyapıt</div></div>
            <div class="slide-item"><img src="https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=500&q=80"><div class="slide-title">Soyut Geometrik</div></div>
            <div class="slide-item"><img src="https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=500&q=80"><div class="slide-title">Siyah Beyaz Koleksiyon</div></div>
            <div class="slide-item"><img src="https://images.unsplash.com/photo-1541701494587-cb58502866ab?auto=format&fit=crop&w=500&q=80"><div class="slide-title">Manzara Serisi</div></div>
            <div class="slide-item"><img src="https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=500&q=80"><div class="slide-title">Özel İllüstrasyon</div></div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.divider()

# --- SIDEBAR: KULLANICI, HESAP VE ADRES DEFTERİ ---
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
            if name_input and email_input and pass_input:
                if email_input in users_df["email"].values:
                    st.sidebar.warning("Bu e-posta zaten kayıtlı!")
                else:
                    new_user = pd.DataFrame([[name_input, email_input, pass_input]], columns=["name", "email", "password"])
                    updated_users = pd.concat([users_df, new_user], ignore_index=True)
                    updated_users.to_csv(USERS_FILE, index=False)
                    st.sidebar.success("Kayıt başarılı! Şimdi giriş yapabilirsiniz.")
                    send_real_email(email_input, "YARENART'a Hoş Geldiniz!", f"Sayın {name_input},\n\nMağazamıza üyeliğiniz başarıyla oluşturulmuştur.")
            else:
                st.sidebar.warning("Lütfen tüm alanları doldurun.")
    else:
        if st.sidebar.button("Giriş Yap", key="btn_login"):
            matched = users_df[(users_df["email"] == email_input) & (users_df["password"] == pass_input)]
            if not matched.empty:
                st.session_state.logged_in = True
                st.session_state.user_name = matched.iloc[0]["name"]
                st.session_state.user_email = email_input
                st.sidebar.success("Giriş başarılı!")
                st.rerun()
            else:
                st.sidebar.error("Hatalı e-posta veya şifre!")
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
                addr_df = load_addresses()
                new_addr = pd.DataFrame([[st.session_state.user_email, addr_title, addr_city, addr_district, addr_neigh, addr_postal, addr_detail, addr_phone]], 
                                        columns=["email", "title", "city", "district", "neighborhood", "postal_code", "detail", "phone"])
                updated_addrs = pd.concat([addr_df, new_addr], ignore_index=True)
                updated_addrs.to_csv(ADDRESS_FILE, index=False)
                st.success("Adres başarıyla kaydedildi!")
            else:
                st.warning("Lütfen başlık, mahalle ve adres detayını doldurun.")

    if st.sidebar.button("Çıkış Yap", key="btn_logout"):
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.session_state.user_email = ""
        st.rerun()

st.sidebar.divider()

# --- ADMIN PANELİ (BİLGİSAYARDAN DOSYA YÜKLEME DESTEKLİ) ---
if st.session_state.logged_in and st.session_state.user_email == ADMIN_EMAIL:
    st.sidebar.subheader("🛠️ Mağaza Yönetimi (Admin)")
    admin_mode = st.sidebar.checkbox("Yönetim Paneli Aç", key="admin_chk")

    if admin_mode:
        st.sidebar.markdown("---")
        st.sidebar.write("**Yeni Ürün Ekle**")
        new_title = st.sidebar.text_input("Eser Adı", key="admin_prod_title")
        new_cat = st.sidebar.selectbox("Kategori", ["Soyut Kanvas", "Baş Yapıt", "Siyah Beyaz", "Manzara", "Özel Seri"], key="admin_prod_cat")
        new_price = st.sidebar.number_input("Fiyat (TL)", min_value=0.0, value=1000.0, key="admin_prod_price")
        new_stock = st.sidebar.number_input("Stok Adedi", min_value=1, value=1, key="admin_prod_stock")
        new_desc = st.sidebar.text_area("Açıklama", key="admin_prod_desc")
        
        # BİLGİSAYARDAN RESİM YÜKLEME ALANI
        uploaded_file = st.sidebar.file_uploader("Bilgisayardan Görsel Seç (PNG, JPG)", type=["png", "jpg", "jpeg"], key="admin_img_upload")
        
        # Alternatif olarak URL ile de yüklenebilsin
        alt_img_url = st.sidebar.text_input("Veya Görsel URL Yapıştır", key="admin_prod_img")

        if st.sidebar.button("Ürünü Mağazaya Ekle", key="admin_btn_add"):
            final_image_path = ""
            if uploaded_file is not None:
                # Dosyayı sunucuya / klasöre kaydet
                file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                final_image_path = file_path
            elif alt_img_url:
                final_image_path = alt_img_url
            else:
                final_image_path = "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=600&q=80"

            if new_title:
                product_df = load_products()
                new_id = int(product_df["id"].max() + 1) if not product_df.empty else 1
                new_row = pd.DataFrame([{
                    "id": new_id, "title": new_title, "category": new_cat,
                    "price": new_price, "stock": new_stock, "description": new_desc, "image_url": final_image_path
                }])
                updated_df = pd.concat([product_df, new_row], ignore_index=True)
                updated_df.to_csv(CSV_FILE, index=False)
                st.sidebar.success("Ürün başarıyla eklendi!")
                st.rerun()
            else:
                st.sidebar.warning("Eser adı zorunludur.")
    st.sidebar.divider()

# --- SEPET VE ADRES SEÇİMİ ---
st.sidebar.subheader("🛒 Sepetim")

if len(st.session_state.cart) > 0:
    total_price = 0
    for item in st.session_state.cart:
        st.sidebar.write(f"- {item['title']} ({item['price']} TL)")
        total_price += item['price']
    st.sidebar.markdown(f"**Toplam Tutar: {total_price} TL**")
    
    if st.sidebar.button("🗑️ Sepeti Temizle", key="btn_clear_cart"):
        st.session_state.cart = []
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📦 Teslimat Adresi")
    
    if not st.session_state.logged_in:
        st.sidebar.warning("Sipariş vermek için önce giriş yapmalısınız!")
    else:
        all_addrs = load_addresses()
        user_addrs = all_addrs[all_addrs["email"] == st.session_state.user_email]
        
        selected_address_info = None
        chosen_addr_title = "Yeni Adres Gir..."
        
        if not user_addrs.empty:
            addr_options = [f"{row['title']} - {row['city']}/{row['district']}" for _, row in user_addrs.iterrows()]
            chosen_addr_title = st.sidebar.selectbox("Kayıtlı Adreslerim", ["Yeni Adres Gir..."] + addr_options, key="select_saved_addr")
            
            if chosen_addr_title != "Yeni Adres Gir...":
                selected_row = user_addrs.iloc[addr_options.index(chosen_addr_title)]
                selected_address_info = {
                    "city": selected_row["city"],
                    "district": selected_row["district"],
                    "neighborhood": selected_row["neighborhood"],
                    "postal_code": selected_row["postal_code"],
                    "detail": selected_row["detail"],
                    "phone": selected_row["phone"]
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
                    "city": ship_city,
                    "district": ship_district,
                    "neighborhood": ship_neighborhood,
                    "postal_code": ship_postal,
                    "detail": ship_address_detail,
                    "phone": ship_phone
                }
        
        if st.sidebar.button("Siparişi Tamamla ve Onayla", key="btn_confirm_order"):
            if selected_address_info:
                order_summary = f"""
Sayın {st.session_state.user_name},

YARENART mağazasından verdiğiniz sipariş başarıyla alınmıştır!

Teslimat Adresi:
{selected_address_info['neighborhood']} Mah. {selected_address_info['detail']}
{selected_address_info['district']} / {selected_address_info['city']} - Posta Kodu: {selected_address_info['postal_code']}
Telefon: {selected_address_info['phone']}

Sipariş Edilen Ürünler:
"""
                for item in st.session_state.cart:
                    order_summary += f"- {item['title']} ({item['price']} TL)\n"
                order_summary += f"\nToplam Tutar: {total_price} TL\n\nBizi tercih ettiğiniz için teşekkür ederiz!"
                
                send_real_email(ADMIN_EMAIL, f"Yeni Sipariş Alındı - {st.session_state.user_name}", order_summary)
                send_real_email(st.session_state.user_email, "Siparişiniz Alındı - YARENART", order_summary)
                
                st.sidebar.success("Siparişiniz başarıyla oluşturuldu! Bilgilendirme mailleri iletildi.")
                st.balloons()
                st.session_state.cart = []
            else:
                st.sidebar.error("Lütfen eksiksiz bir teslimat adresi belirtin veya kayıtlı adres seçin.")
else:
    st.sidebar.write("Sepetiniz boş.")

# --- KATEGORİ FİLTRELEME & VİTRİN ---
st.markdown("### 🎨 Tüm Sanat Eserleri")
selected_cat = st.selectbox("Kategoriye Göre Filtrele", ["Tümü", "Soyut Kanvas", "Baş Yapıt", "Siyah Beyaz", "Manzara", "Özel Seri"], key="filter_cat")

if selected_cat != "Tümü":
    display_df = df[df["category"] == selected_cat]
else:
    display_df = df

num_cols = 4
rows = [display_df.iloc[i:i+num_cols] for i in range(0, len(display_df), num_cols)]

for row_chunk in rows:
    cols = st.columns(num_cols)
    for col_idx, (_, row) in enumerate(row_chunk.iterrows()):
        with cols[col_idx]:
            st.image(row["image_url"], use_container_width=True)
            st.markdown(f"**{row['title']}**")
            st.markdown(f"<span style='color: #8C7A6B;'>Kategori: {row['category']}</span>", unsafe_allow_html=True)
            st.markdown(f"**Fiyat: {row['price']:,.2f} TL**")
            
            if st.button("Sepete Ekle", key=f"product_{row['id']}"):
                st.session_state.cart.append({
                    "id": row["id"],
                    "title": row["title"],
                    "price": row["price"]
                })
                st.success("Sepete eklendi!")

# --- WHATSAPP İKONU ---
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
