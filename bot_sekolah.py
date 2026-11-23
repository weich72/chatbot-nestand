import streamlit as st
from google import genai
from google.genai import types
import base64
import os
import time

# 1. KUNCI API GOOGLE AI STUDIO (AMAN MENGGUNAKAN SECRETS STREAMLIT)
KUNCI_AI = st.secrets["GEMINI_API_KEY"]

# Mengatur tampilan halaman web
st.set_page_config(
    page_title="Asisten Virtual Nestand AKBAR",
    page_icon="🎓",
    layout="wide"
)

# FUNGSI MEMBACA GAMBAR LOKAL (UNTUK WALLPAPER & LOGO)
def gambar_ke_base64(nama_dasar):
    for ext in ["png", "jpg", "jpeg"]:
        nama_file = f"{nama_dasar}.{ext}"
        if os.path.exists(nama_file):
            with open(nama_file, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            tipe = "png" if ext == "png" else "jpeg"
            return f"data:image/{tipe};base64,{data}"
    return None

# FUNGSI MEMBACA BASIS PENGETAHUAN DARI FILE knowledge_base.md
def muat_knowledge_base():
    if os.path.exists("knowledge_base.md"):
        with open("knowledge_base.md", "r", encoding="utf-8") as f:
            return f.read()
    return "Kamu adalah Asisten Virtual Resmi SMP Negeri 1 Tanjungmedar (NESTAND AKBAR)."

# FUNGSI TAMPILAN RAMPING + GLASSMORPHISM + WALLPAPER TERBUKA LEGA
def pasang_tampilan_mewah():
    url_wallpaper = gambar_ke_base64("wallpaper")
    if url_wallpaper:
        bg_css = f"""
            background-image: linear-gradient(rgba(10, 25, 47, 0.05), rgba(15, 23, 42, 0.12)),
                              url("{url_wallpaper}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        """
    else:
        bg_css = "background: linear-gradient(135deg, #0a192f 0%, #112240 45%, #1d4ed8 100%);"

    st.markdown(
        f"""
        <style>
        .stApp {{
            {bg_css}
            color: #f8fafc;
        }}
        header[data-testid="stHeader"] {{
            background: transparent !important;
        }}
        /* MERAMPINGKAN KONTAINER UTAMA AGAR WALLPAPER TERLIHAT LUAS */
        .block-container {{
            max-width: 720px !important;
            padding-top: 2.2rem !important;
            padding-bottom: 5rem !important;
            margin: 0 auto !important;
        }}
        /* MERAMPINGKAN KOTAK KETIK PESAN DI BAWAH */
        div[data-testid="stBottom"] {{
            background: transparent !important;
        }}
        div[data-testid="stBottom"] > div {{
            max-width: 720px !important;
            margin: 0 auto !important;
            background: transparent !important;
        }}
        section[data-testid="stSidebar"] {{
            background: rgba(15, 23, 42, 0.85) !important;
            backdrop-filter: blur(14px);
            border-right: 1px solid rgba(56, 189, 248, 0.35);
        }}
        .hero-box {{
            background: rgba(15, 23, 42, 0.72);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(125, 211, 252, 0.45);
            border-radius: 16px;
            padding: 14px 20px;
            margin-bottom: 14px;
            box-shadow: 0 6px 24px rgba(0, 0, 0, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 16px;
            flex-wrap: wrap;
        }}
        .hero-logo {{
            width: 64px;
            height: 64px;
            object-fit: contain;
            filter: drop-shadow(0 4px 10px rgba(0,0,0,0.4));
        }}
        .hero-text {{
            text-align: center;
        }}
        .hero-title {{
            font-size: 1.55rem;
            font-weight: 800;
            background: linear-gradient(90deg, #38bdf8, #ffffff, #7dd3fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
            line-height: 1.2;
        }}
        .hero-sub {{
            color: #e2e8f0;
            font-size: 0.86rem;
            margin-top: 2px;
        }}
        .hero-badge {{
            display: inline-block;
            margin-top: 6px;
            padding: 3px 12px;
            border-radius: 999px;
            background: rgba(56, 189, 248, 0.25);
            border: 1px solid rgba(125, 211, 252, 0.55);
            color: #e0f2fe;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        /* GELEMBUNG CHAT RAMPING & TRANSPARAN ELEGAN */
        div[data-testid="stChatMessage"] {{
            background: rgba(15, 23, 42, 0.74) !important;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(148, 163, 184, 0.3);
            border-radius: 16px;
            padding: 10px 16px;
            margin-bottom: 8px;
            width: fit-content;
            max-width: 88%;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
        }}
        /* PESAN USER OTOMATIS RATA KANAN SEPERTI WHATSAPP */
        div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {{
            margin-left: auto;
            background: rgba(30, 58, 138, 0.78) !important;
            border-color: rgba(96, 165, 250, 0.45);
        }}
        div[data-testid="stChatInput"] {{
            background: rgba(15, 23, 42, 0.85) !important;
            backdrop-filter: blur(12px);
            border-radius: 14px;
            border: 1px solid rgba(56, 189, 248, 0.5);
        }}
        /* TOMBOL CEPAT LEBIH COMPACT */
        div.stButton > button {{
            background: rgba(15, 23, 42, 0.75) !important;
            backdrop-filter: blur(8px);
            border: 1px solid rgba(125, 211, 252, 0.4) !important;
            color: #f8fafc !important;
            font-size: 0.8rem !important;
            padding: 0.35rem 0.5rem !important;
            border-radius: 10px !important;
        }}
        div.stButton > button:hover {{
            border-color: #38bdf8 !important;
            background: rgba(30, 58, 138, 0.85) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

pasang_tampilan_mewah()
url_logo = gambar_ke_base64("logo")

# PANEL SAMPING (SIDEBAR) DENGAN LOGO & PROFIL SEKOLAH
with st.sidebar:
    if url_logo:
        st.markdown(f'<div style="text-align:center;"><img src="{url_logo}" width="90"></div>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; margin-bottom:0;'>SMPN 1 Tanjungmedar</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#7dd3fc;'><b>NESTAND AKBAR</b> • Kab. Sumedang</p>", unsafe_allow_html=True)
    st.info("🎓 *Aktif • Kreatif • Bersama • Adab • Religius*")
    st.markdown("---")
    st.markdown("**Visi Sekolah: NESTAND AKBAR**")
    st.caption("• **AKBAR:** Aktif, Kreatif, Bersama, Adab, Religius")
    st.markdown("---")
    if st.button("🗑️ Bersihkan Obrolan", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Sampurasun & Assalamu'alaikum! Selamat datang di layanan informasi digital **SMP Negeri 1 Tanjungmedar (NESTAND AKBAR)**. Ada yang bisa saya bantu hari ini? 😊"
            }
        ]
        st.rerun()

# HEADER UTAMA DENGAN LOGO SEKOLAH
logo_html = f'<img src="{url_logo}" class="hero-logo">' if url_logo else '<span style="font-size:2.5rem;">🎓</span>'
st.markdown(
    f"""
    <div class="hero-box">
        {logo_html}
        <div class="hero-text">
            <h1 class="hero-title">Asisten Virtual Nestand AKBAR</h1>
            <div class="hero-sub">Pusat Informasi Digital SMP Negeri 1 Tanjungmedar • Sumedang</div>
            <div class="hero-badge">✨ Aktif • Kreatif • Bersama • Adab • Religius ✨</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Menghubungkan ke otak AI Google
client = genai.Client(api_key=KUNCI_AI)

# 2. MEMUAT BUKU INGATAN RESMI DARI FILE knowledge_base.md
info_sekolah = muat_knowledge_base()

# OTOMATIS MENDETEKSI SEMUA MODEL AI YANG TERSEDIA DI AKUN PA WEI
@st.cache_data(ttl=3600)
def cari_daftar_model_ai():
    daftar = ["gemma-4-26b-a4b-it", "gemini-3.8-flash"]
    try:
        for m in client.models.list():
            nama = m.name.replace("models/", "")
            if ("gemini" in nama or "gemma" in nama) and "embedding" not in nama and "imagen" not in nama and "veo" not in nama:
                if nama not in daftar:
                    daftar.append(nama)
    except Exception:
        pass
    return daftar

# 3. MENYIAPKAN INGATAN OBROLAN
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Sampurasun & Assalamu'alaikum! Selamat datang di layanan informasi digital **SMP Negeri 1 Tanjungmedar (NESTAND AKBAR)**. Ada yang bisa saya bantu hari ini? 😊"
        }
    ]

# TOMBOL PERTANYAAN CEPAT (QUICK PROMPTS)
col1, col2, col3, col4 = st.columns(4)
pertanyaan_tombol = None
if col1.button("🏫 Profil & Pimpinan", use_container_width=True):
    pertanyaan_tombol = "Siapa Kepala Sekolah dan Wakasek Kurikulum SMP Negeri 1 Tanjungmedar sekarang, serta di mana alamat lengkapnya?"
if col2.button("📅 Jadwal & Wali Kelas", use_container_width=True):
    pertanyaan_tombol = "Bagaimana jadwal kegiatan harian sekolah dan daftar wali kelas tahun ajaran 2026/2027?"
if col3.button("💻 Lab & eksKomp", use_container_width=True):
    pertanyaan_tombol = "Apa saja fasilitas Laboratorium Komputer dan program ekstrakurikuler eksKomp Nestand?"
if col4.button("📚 Materi Informatika", use_container_width=True):
    pertanyaan_tombol = "Apa saja peta materi pelajaran Informatika untuk Kelas VII, VIII, dan IX?"

# Menampilkan riwayat obrolan di layar
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Menangkap input dari ketikan manual ATAU klik tombol cepat
pertanyaan_ketik = st.chat_input("Tanyakan seputar SMPN 1 Tanjungmedar...")
pertanyaan = pertanyaan_tombol if pertanyaan_tombol else pertanyaan_ketik

if pertanyaan:
    st.session_state.messages.append({"role": "user", "content": pertanyaan})
    with st.chat_message("user"):
        st.markdown(pertanyaan)

    riwayat_chat = []
    for m in st.session_state.messages:
        peran = "user" if m["role"] == "user" else "model"
        riwayat_chat.append(
            types.Content(
                role=peran,
                parts=[types.Part.from_text(text=m["content"])]
            )
        )

    semua_model = cari_daftar_model_ai()

    with st.chat_message("assistant"):
        with st.spinner("Sedang berpikir menggunakan otak AI..."):
            jawaban = None
            model_terpakai = ""
            error_terakhir = ""

            for nama_model in semua_model:
                try:
                    respon = client.models.generate_content(
                        model=nama_model,
                        contents=riwayat_chat,
                        config=types.GenerateContentConfig(
                            system_instruction=info_sekolah,
                            temperature=0.4
                        )
                    )
                    jawaban = respon.text
                    model_terpakai = nama_model
                    break
                except Exception as e:
                    error_terakhir = str(e)
                    continue

            if jawaban:
                st.markdown(jawaban)
                st.caption(f"⚡ Dijawab oleh AI: `{model_terpakai}`")
                st.session_state.messages.append({"role": "assistant", "content": jawaban})
            else:
                st.error(f"Jalur AI sedang padat sementara. Coba klik/kirim ulang sebentar lagi ya! ({error_terakhir})")

