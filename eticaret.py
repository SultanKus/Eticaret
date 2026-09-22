import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Sayfa Ayarları
st.set_page_config(page_title="Sanat & İllüstrasyon Mağazası", page_icon="🎨", layout="wide")

# Veri Dosyası Yolları
CSV_FILE = "products.csv"
USERS_FILE = "users.csv"

# Varsayılan Ürün Verilerini Oluştur (Eğer yoksa)
if not os.path.exists(CSV_FILE):
    initial_data = {
        "id": [1, 2, 3, 4, 5, 6, 7, 8],
        "title": ["Kategori X - Eser 1", "Kategori X - Eser 2", "Kategori Y - Eser 1", "Kategori Y - Eser 2", 
                  "Kategori Z - Eser 1", "Kategori Z - Eser 2", "Özel Seri - 1", "Özel Seri - 2"],
        "category": ["Kategori X", "Kategori X", "Kategori Y", "Kategori Y", "Kategori Z", "Kategori Z", "Özel Seri", "Özel Seri"],
        "price": [1250.0, 850.0, 450.0, 600.0, 2100.0, 950.0, 1500.0, 1750.0],
        "stock": [1, 2, 5, 3, 1, 4, 1, 2],
        "description": ["Özel akrilik çalışma.", "Modern tuval illüstrasyonu.", "Sınırlı sayıda baskı.", "Mat kuşe kağıt baskı.", 
                        "Orijinal büyük boy tuval.", "Karakalem detaylı eser.", "Kişiselleştirilebilir sanat.", "Eşsiz tasarım."],
        "image_url": [
            "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1541701494587-cb58502866ab?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1541701494587-cb58502866ab?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=600&q=80"
        ]
    }
    pd.DataFrame(initial_data).to_csv(CSV_FILE, index=False)

# Varsayılan Kullanıcı Veritabanı (Eğer yoksa)
if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["email", "password"]).to_csv(USERS_FILE, index=False)

@st.cache_data
def load_products():
    return pd.read_csv(CSV_FILE)

def load_users():
    return pd.read_csv(USERS_FILE)

df = load_products()

# Oturum Yönetimi (Session State)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "cart" not in st.session_state:
    st.session_state.cart = []

# Mail Bildirim Simülasyonu / Fonksiyonu
def send_email_notification(subject, body):
    try:
        print(f"Mail hedefi: skus42173@gmail.com | Konu: {subject} | İçerik: {body}")
    except Exception as e:
        print(f"Mail hatası: {e}")

# --- ÜST MENÜ & HEADER ---
st.title("🎨 Sanat Atölyesi & E-Ticaret Mağazası")
st.markdown("Eşsiz el yapımı çizimler, orijinal tablolar ve özel koleksiyonlar.")

# --- SIDEBAR: ÜYELİK & SEPET & ADMIN ---
st.sidebar.header("👤 Kullanıcı & Hesap")

if not st.session_state.logged_in:
    auth_mode = st.sidebar.radio("İşlem Seçin", ["Giriş Yap", "Üye Ol"])
    
    email_input = st.sidebar.text_input("E-posta Adresi")
    pass_input = st.sidebar.text_input("Şifre", type="password")
    
    users_df = load_users()
    
    if auth_mode == "Üye Ol":
        if st.sidebar.button("Kayıt Ol"):
            if email_input and pass_input:
                if email_input in users_df["email"].values:
                    st.sidebar.warning("Bu e-posta zaten kayıtlı!")
                else:
                    new_user = pd.DataFrame([[email_input, pass_input]], columns=["email", "password"])
                    updated_users = pd.concat([users_df, new_user], ignore_index=True)
                    updated_users.to_csv(USERS_FILE, index=False)
                    st.sidebar.success("Kayıt başarılı! Şimdi giriş yapabilirsiniz.")
                    send_email_notification("Yeni Üye Kaydı", f"Yeni bir üye katıldı: {email_input}")
            else:
                st.sidebar.warning("Lütfen tüm alanları doldurun.")
    else:
        if st.sidebar.button("Giriş Yap"):
            matched = users_df[(users_df["email"] == email_input) & (users_df["password"] == pass_input)]
            if not matched.empty:
                st.session_state.logged_in = True
                st.session_state.user_email = email_input
                st.sidebar.success("Giriş başarılı!")
                st.rerun()
            else:
                st.sidebar.error("Hatalı e-posta veya şifre!")
else:
    st.sidebar.write(f"Hoş geldin, **{st.session_state.user_email}**")
    if st.sidebar.button("Çıkış Yap"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.rerun()

st.sidebar.divider()

# --- ADMIN PANELİ (Mağaza Yönetimi) ---
st.sidebar.subheader("🛠️ Mağaza Yönetimi (Admin)")
admin_mode = st.sidebar.checkbox("Yönetim Paneli Aç")

if admin_mode:
    st.sidebar.markdown("---")
    st.sidebar.write("**Yeni Ürün Ekle**")
    new_title = st.sidebar.text_input("Eser Adı")
    new_cat = st.sidebar.selectbox("Kategori", ["Kategori X", "Kategori Y", "Kategori Z", "Özel Seri"])
    new_price = st.sidebar.number_input("Fiyat (TL)", min_value=0.0, value=500.0)
    new_stock = st.sidebar.number_input("Stok Adedi", min_value=1, value=1)
    new_desc = st.sidebar.text_area("Açıklama")
    new_img = st.sidebar.text_input("Görsel URL (Unsplash veya Resim Linki)")
    
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
            st.sidebar.success("Ürün başarıyla eklendi! Sayfa yenileniyor...")
            st.rerun()
        else:
            st.sidebar.warning("Eser adı ve görsel URL zorunludur.")

# --- SEPET VE PROFESYONEL ÖDEME ALANI ---
st.sidebar.divider()
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
        st.sidebar.warning("Sipariş vermek için önce üye olmalı ve giriş yapmalısınız!")
    else:
        ship_name = st.sidebar.text_input("Ad Soyad")
        ship_phone = st.sidebar.text_input("Telefon Numarası")
        ship_city = st.sidebar.text_input("Şehir")
        ship_district = st.sidebar.text_input("İlçe")
        ship_neighborhood = st.sidebar.text_input("Mahalle")
        ship_address_detail = st.sidebar.text_area("Cadde, Sokak, Bina ve Kapı No")
        
        if st.sidebar.button("Siparişi Tamamla ve Onayla"):
            if ship_name and ship_phone and ship_city and ship_district and ship_address_detail:
                order_summary = f"""
Yeni Sipariş Alındı!
Müşteri Üye: {st.session_state.user_email}
Ad Soyad: {ship_name}
Telefon: {ship_phone}
Adres: {ship_neighborhood} Mah. {ship_address_detail}, {ship_district} / {ship_city}

Ürünler:
"""
                for item in st.session_state.cart:
                    order_summary += f"- {item['title']} ({item['price']} TL)\n"
                order_summary += f"\nToplam Tutar: {total_price} TL"
                
                # skus42173@gmail.com adresine sipariş bildirimi
                send_email_notification(f"Yeni Sipariş - {ship_name}", order_summary)
                
                st.sidebar.success("Siparişiniz başarıyla alındı! Satıcıya ve size detaylar iletildi.")
                st.balloons()
                st.session_state.cart = []
            else:
                st.sidebar.error("Lütfen tüm adres ve iletişim alanlarını eksiksiz doldurun.")
else:
    st.sidebar.write("Sepetiniz boş.")

# --- KATEGORİ FİLTRELEME & VİTRİN (4'LÜ GRID) ---
st.divider()
selected_cat = st.selectbox("Kategori Filtrele", ["Tümü", "Kategori X", "Kategori Y", "Kategori Z", "Özel Seri"])

if selected_cat != "Tümü":
    display_df = df[df["category"] == selected_cat]
else:
    display_df = df

# 4'lü sütun yapısı (Her satırda 4 ürün)
num_cols = 4
rows = [display_df.iloc[i:i+num_cols] for i in range(0, len(display_df), num_cols)]

for row_chunk in rows:
    cols = st.columns(num_cols)
    for col_idx, (_, row) in enumerate(row_chunk.iterrows()):
        with cols[col_idx]:
            st.image(row["image_url"], use_container_width=True)
            st.subheader(row["title"])
            st.markdown(f"**Kategori:** {row['category']}")
            st.markdown(f"**Fiyat:** {row['price']} TL")
            st.markdown(f"**Stok:** {row['stock']} adet")
            st.write(row["description"])
            
            if st.button("Sepete Ekle", key=f"product_{row['id']}"):
                st.session_state.cart.append({
                    "id": row["id"],
                    "title": row["title"],
                    "price": row["price"]
                })
                st.success("Sepete eklendi!")

# --- İLETİŞİM & SOSYAL MEDYA FOOTER ---
st.markdown("---")
st.markdown("""
### 📞 İletişim & Sosyal Medya
Sanatçının tüm eserlerini yakından incelemek ve doğrudan iletişime geçmek için:
- **Instagram:** [@sanatci_hesabi](https://instagram.com)
- **E-posta Destek:** `skus42173@gmail.com`
- **Atölye Konumu:** İstanbul / Kadıköy
""")
