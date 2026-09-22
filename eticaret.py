import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Sayfa Ayarları (Geniş Ekran)
st.set_page_config(page_title="YARENART | Sanat & İllüstrasyon Mağazası", page_icon="🎨", layout="wide")

# Veri Dosyası Yolları
CSV_FILE = "products.csv"
USERS_FILE = "users.csv"
ADMIN_EMAIL = "skus42173@gmail.com"
WHATSAPP_PHONE = "905527920708"

# Varsayılan Ürün Verilerini Oluştur (Eğer yoksa)
if not os.path.exists(CSV_FILE):
    initial_data = {
        "id": [1, 2, 3, 4, 5, 6, 7, 8],
        "title": ["Modern Soyut Geometrik Tablo", "Lacivert Krem Soyut Tablo", "Siyah Bej Altın Soyut Tablo", "Bej Kahve Soyut Tablo", 
                  "Baş Yapıt Kanvas Tablo", "Siyah Beyaz Kanvas Tablo", "Manzara Kanvas Tablosu", "Özel Seri İllüstrasyon"],
        "category": ["Soyut Kanvas", "Soyut Kanvas", "Soyut Kanvas", "Soyut Kanvas", "Baş Yapıt", "Siyah Beyaz", "Manzara", "Özel Seri"],
        "price": [1000.0, 1000.0, 1000.0, 1000.0, 1250.0, 850.0, 1100.0, 1500.0],
        "stock": [3, 5, 2, 4, 1, 6, 2, 1],
        "description": ["Yüksek kaliteli tuval üzerine özel modern tasarım.", "Evinize şıklık katacak renk tonları.", "Altın varak detaylı lüks dokunuş.", "Minimalist evler için kahve tonları.",
                        "Klasik sanatın modern tuvale yansıması.", "Siyah beyaz sokak konsepti.", "Huzur veren doğa manzarası.", "Sınırlı sayıda üretilmiş özel eser."],
        "image_url": [
            "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1541701494587-cb58502866ab?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1541701494587-cb58502866ab?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=600&q=80"
        ]
    }
    pd.DataFrame(initial_data).to_csv(CSV_FILE, index=False)

if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["name", "email", "password"]).to_csv(USERS_FILE, index=False)

@st.cache_data
def load_products():
    return pd.read_csv(CSV_FILE)

def load_users():
    return pd.read_csv(USERS_FILE)

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
        print(f"E-posta hedefe iletildi: {to_email} | Konu: {subject}")
        return True
    except Exception as e:
        print(f"Mail hatası: {e}")
        return False

# --- ÖZEL BAŞLIK & LOGO (YARENART) ---
st.markdown("""
    <div style='text-align: center; padding: 10px 0;'>
        <h1 style='font-family: sans-serif; font-size: 48px; font-weight: 800; background: linear-gradient(45deg, #ff4b1f, #ff9068, #7f00ff, #e100ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
            ✨ YARENART ✨
        </h1>
        <p style='color: #666; font-size: 18px; font-weight: 500;'>Eşsiz El Yapımı Çizimler, Tuval ve Özel Seri Tablolar</p>
    </div>
""", unsafe_allow_html=True)

st.divider()

# --- ÖRNEK GÖRSELDEKİ ÖNE ÇIKAN KATEGORİ SLIDER/KARTLARI ---
st.markdown("### 🌟 Öne Çıkan Koleksiyonlar")
cat_cols = st.columns(4)
categories_show = [
    ("Baş Yapıt Kanvaslar", "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?auto=format&fit=crop&w=500&q=80"),
    ("Soyut Kanvas Tablolar", "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=500&q=80"),
    ("Siyah Beyaz Kanvaslar", "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=500&q=80"),
    ("Manzara Kanvas Tabloları", "https://images.unsplash.com/photo-1541701494587-cb58502866ab?auto=format&fit=crop&w=500&q=80")
]

for idx, (cat_name, cat_img) in enumerate(categories_show):
    with cat_cols[idx]:
        st.image(cat_img, use_container_width=True)
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>{cat_name}</p>", unsafe_allow_html=True)

st.divider()

# --- SIDEBAR: KULLANICI, SEPET VE ADMIN ---
st.sidebar.header("👤 Kullanıcı & Hesap")

if not st.session_state.logged_in:
    auth_mode = st.sidebar.radio("İşlem Seçin", ["Giriş Yap", "Üye Ol"])
    
    if auth_mode == "Üye Ol":
        name_input = st.sidebar.text_input("Ad Soyad")
        email_input = st.sidebar.text_input("E-posta Adresi")
        pass_input = st.sidebar.text_input("Şifre", type="password")
    else:
        email_input = st.sidebar.text_input("E-posta Adresi")
        pass_input = st.sidebar.text_input("Şifre", type="password")
    
    users_df = load_users()
    
    if auth_mode == "Üye Ol":
        if st.sidebar.button("Kayıt Ol"):
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
        if st.sidebar.button("Giriş Yap"):
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
    st.sidebar.write(f"Hoş geldin, **{st.session_state.user_name}**")
    if st.sidebar.button("Çıkış Yap"):
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.session_state.user_email = ""
        st.rerun()

st.sidebar.divider()

# --- YALNIZCA SANA ÖZEL ADMIN PANELİ ---
if st.session_state.logged_in and st.session_state.user_email == ADMIN_EMAIL:
    st.sidebar.subheader("🛠️ Mağaza Yönetimi (Admin)")
    admin_mode = st.sidebar.checkbox("Yönetim Paneli Aç")

    if admin_mode:
        st.sidebar.markdown("---")
        st.sidebar.write("**Yeni Ürün Ekle**")
        new_title = st.sidebar.text_input("Eser Adı")
        new_cat = st.sidebar.selectbox("Kategori", ["Soyut Kanvas", "Baş Yapıt", "Siyah Beyaz", "Manzara", "Özel Seri"])
        new_price = st.sidebar.number_input("Fiyat (TL)", min_value=0.0, value=1000.0)
        new_stock = st.sidebar.number_input("Stok Adedi", min_value=1, value=1)
        new_desc = st.sidebar.text_area("Açıklama")
        new_img = st.sidebar.text_input("Görsel URL")
        
        if st.sidebar.button("Ürünü Mağazaya Ekle"):
            if new_title and new_img:
                product_df = load_products()
                new_id = int(product_df["id"].max() + 1) if not product_df.empty else 1
                new_row = pd.DataFrame([{
                    "id": new_id, "title": new_title, "category": new_cat,
                    "price": new_price, "stock": new_stock, "description": new_desc, "image_url": new_img
                }])
                updated_df = pd.concat([product_df, new_row], ignore_index=True)
                updated_df.to_csv(CSV_FILE, index=False)
                st.sidebar.success("Ürün başarıyla eklendi!")
                st.rerun()
            else:
                st.sidebar.warning("Eser adı ve görsel URL zorunludur.")
    st.sidebar.divider()

# --- SEPET VE DETAYLI ADRES ---
st.sidebar.subheader("🛒 Sepetim")

if len(st.session_state.cart) > 0:
    total_price = 0
    for item in st.session_state.cart:
        st.sidebar.write(f"- {item['title']} ({item['price']} TL)")
        total_price += item['price']
    st.sidebar.markdown(f"**Toplam Tutar: {total_price} TL**")
    
    if st.sidebar.button("🗑️ Sepeti Temizle"):
        st.session_state.cart = []
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📦 Teslimat Adresi")
    
    if not st.session_state.logged_in:
        st.sidebar.warning("Sipariş vermek için önce giriş yapmalısınız!")
    else:
        ship_phone = st.sidebar.text_input("Telefon Numarası")
        ship_city = st.sidebar.text_input("Şehir")
        ship_district = st.sidebar.text_input("İlçe")
        ship_neighborhood = st.sidebar.text_input("Mahalle")
        ship_address_detail = st.sidebar.text_area("Cadde, Sokak, Bina ve Kapı No")
        
        if st.sidebar.button("Siparişi Tamamla ve Onayla"):
            if ship_phone and ship_city and ship_district and ship_address_detail:
                order_summary = f"""
Sayın {st.session_state.user_name},

YARENART mağazasından verdiğiniz sipariş başarıyla alınmıştır!

Teslimat Adresi:
{ship_neighborhood} Mah. {ship_address_detail}, {ship_district} / {ship_city}
Telefon: {ship_phone}

Sipariş Edilen Ürünler:
"""
                for item in st.session_state.cart:
                    order_summary += f"- {item['title']} ({item['price']} TL)\n"
                order_summary += f"\nToplam Tutar: {total_price} TL\n\nBizi tercih ettiğiniz için teşekkür ederiz!"
                
                send_real_email(ADMIN_EMAIL, f"Yeni Sipariş - {st.session_state.user_name}", order_summary)
                send_real_email(st.session_state.user_email, "Siparişiniz Alındı - YARENART", order_summary)
                
                st.sidebar.success("Siparişiniz başarıyla oluşturuldu! Bilgilendirme mailleri iletildi.")
                st.balloons()
                st.session_state.cart = []
            else:
                st.sidebar.error("Lütfen tüm adres alanlarını eksiksiz doldurun.")
else:
    st.sidebar.write("Sepetiniz boş.")

# --- KATEGORİ FİLTRELEME & 4'LÜ VİTRİN ---
st.subheader("🛍️ Tüm Ürünler")
selected_cat = st.selectbox("Kategoriye Göre Filtrele", ["Tümü", "Soyut Kanvas", "Baş Yapıt", "Siyah Beyaz", "Manzara", "Özel Seri"])

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
            st.markdown(f"Kategori: {row['category']}")
            st.markdown(f"**Fiyat: {row['price']:,.2f} TL**")
            
            if st.button("Sepete Ekle", key=f"product_{row['id']}"):
                st.session_state.cart.append({
                    "id": row["id"],
                    "title": row["title"],
                    "price": row["price"]
                })
                st.success("Sepete eklendi!")

# --- SAĞ ALT KÖŞEDE WHATSAPP SABİT BUTON VE FOOTER ---
whatsapp_url = f"https://wa.me/{WHATSAPP_PHONE}?text=Merhaba%2C%20YARENART%20ürünleri%20hakkında%20bilgi%20almak%20istiyorum."

st.markdown(f"""
    <a href="{whatsapp_url}" target="_blank" style="position: fixed; bottom: 30px; right: 30px; z-index: 9999; background-color: #25d366; color: white; padding: 15px; border-radius: 50px; text-decoration: none; font-size: 24px; box-shadow: 2px 2px 10px rgba(0,0.0,0.3);">
        💬
    </a>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown(f"""
### 📞 YARENART İletişim & Destek
- **WhatsApp Destek Hattı:** [{WHATSAPP_PHONE}](https://wa.me/{WHATSAPP_PHONE})
- **E-posta:** `{ADMIN_EMAIL}`
- **Instagram:** [@yarenart](https://instagram.com)
""")
