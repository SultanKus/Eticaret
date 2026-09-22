import streamlit as st
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="Sanat Atölyesi Vitrini", page_icon="🎨", layout="wide")

# Verileri Yükle
@st.cache_data
def load_data():
    return pd.read_csv("products.csv")

df = load_data()

# Başlık ve Karşılama
st.title("🎨 Sanat & İllüstrasyon Vitrini")
st.markdown("Özel çizimler, orijinal tablolar ve sınırlı sayıdaki baskılar.")

# Sidebar (Kenar Çubuğu) - Filtreler ve Sepet
st.sidebar.header("🔍 Filtreler")
selected_category = st.sidebar.selectbox("Kategori Seçin", ["Tümü"] + list(df["category"].unique()))

if selected_category != "Tümü":
    filtered_df = df[df["category"] == selected_category]
else:
    filtered_df = df

# Sepet Yönetimi (Session State)
if "cart" not in st.session_state:
    st.session_state.cart = []

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
        
    shipping_name = st.sidebar.text_input("Ad Soyad")
    shipping_address = st.sidebar.text_area("Teslimat Adresi")
    
    if st.sidebar.button("📲 Siparişi WhatsApp ile Tamamla"):
        if shipping_name and shipping_address:
            order_details = f"Merhaba, yeni bir sipariş vermek istiyorum:\n\n*Müşteri:* {shipping_name}\n*Adres:* {shipping_address}\n\n*Ürünler:*\n"
            for item in st.session_state.cart:
                order_details += f"- {item['title']} ({item['price']} TL)\n"
            order_details += f"\nToplam: {total_price} TL"
            
            import urllib.parse
            encoded_message = urllib.parse.quote(order_details)
            whatsapp_url = f"https://wa.me/905000000000?text={encoded_message}"
            
            st.sidebar.markdown(f"[📲 Siparişi Göndermek İçin Tıklayın]({whatsapp_url})", unsafe_allow_html=True)
        else:
            st.sidebar.warning("Lütfen ad soyad ve adres bilgilerini doldurun.")
else:
    st.sidebar.write("Sepetiniz henüz boş.")

# Ürünleri Kartlar Halinde Listeleme
st.divider()
cols = st.columns(2)

for index, row in filtered_df.iterrows():
    with cols[index % 2]:
        st.image(row["image_url"], use_container_width=True)
        st.subheader(row["title"])
        st.markdown(f"**Kategori:** {row['category']}")
        st.markdown(f"**Fiyat:** {row['price']} TL")
        st.write(row["description"])
        
        if st.button(f"Sepete Ekle", key=f"btn_{row['id']}"):
            st.session_state.cart.append({
                "id": row["id"],
                "title": row["title"],
                "price": row["price"]
            })
            st.success(f"'{row['title']}' sepete eklendi!")
