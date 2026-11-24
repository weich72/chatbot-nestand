import streamlit as st
from google import genai
from google.genai import types
import base64
import os
import time

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="Asisten Virtual Nestand AKBAR",
    page_icon="🎓",
    layout="wide"
)

# 2. KONEKSI AI DI-CACHE AGAR TIDAK BIKIN KONEKSI ULANG TIAP CHAT
@st.cache_resource
def buat_client_ai():
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

client = buat_client_ai()

# 3. GAMBAR DI-CACHE AGAR TIDAK DIBACA ULANG TIAP KLIK
@st.cache_data
def gambar_ke_base64(nama_dasar):
    for ext in ["png", "jpg", "jpeg", "webp"]:
        nama_file = f"{nama_dasar}.{ext}"
        if os.path.exists(nama_file):
            with open(nama_file, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            tipe = "jpeg" if ext in ["jpg", "jpeg"] else ext
            return f"data:image/{tipe};base64,{data}"
    return None

# 4. BASIS PENGETAHUAN CUKUP BACA DARI knowledge_base.md (TIDAK DOBEL)
@st.cache_data(ttl=600)
def muat_knowledge_base():
    instruksi_kecepatan = (
        "\n\nATURAN GAYA JAWABAN: Jawab dengan ramah, akurat, ringkas, dan langsung ke inti "
        "(maksimal 3-4 paragraf pendek atau poin-poin singkat agar cepat dibaca)."
    )
    if os.path.exists("knowledge_base.md"):
        with open("knowledge_base.md", "r", encoding="utf-8") as f:
            return f.read() + instruksi_kecepatan
    return "Kamu adalah Asisten Virtual Resmi SMP Negeri 1 Tanjungmedar (NESTAND AKBAR)." + instruksi_kecepatan

# 5. TAMPILAN GLASSMORPHISM
def pasang_tampilan_mewah():
    url_wallpaper = gambar_ke_base64("wallpaper")
    if url_wallpaper:
        bg_css = f"""
            background-image: linear-gradient(rgba(10, 25, 47, 0.08), rgba(15, 23, 42, 0.15)),
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
        .block-container {{
            max-width: 720px !important;
            padding-top: 2.2rem !important;
            padding-bottom: 5rem !important;
            margin: 0 auto !important;
        }}
        div[data-testid="stBottom"], div[data-testid="stBottom"] > div {{
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
            padding: 18px 20px;
            margin-bottom: 14px;
            box-shadow: 0 6px 24px rgba(0, 0, 0, 0.3);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            gap: 10px;
        }}
        .hero-logo {{
            width: 68px;
            height: 68px;
            object-fit: contain;
            filter: drop-shadow(0 4px 10px rgba(0,0,0,0.4));
        }}
        .hero-text {{ text-align: center; width: 100%; }}
        .hero-title {{
            font-size: 1.55rem;
            font-weight: 800;
            background: linear-gradient(90deg, #38bdf8, #ffffff, #7dd3fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
            line-height: 1.2;
        }}
        .hero-sub {{ color: #e2e8f0; font-size: 0.86rem; margin-top: 2px; }}
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

# SIDEBAR
with st.sidebar:
    if url_logo:
        st.markdown(f'<div style="text-align:center;"><img src="{url_logo}" width="90"></div>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; margin-bottom:0;'>SMPN 1 Tanjungmedar</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#7dd3fc;'><b>NESTAND AKBAR</b> • Kab. Sumedang</p>", unsafe_allow_html=True)
    st.info("🎓 *Aktif • Kreatif • Bersama • Adab • Religius*")
    st.markdown("---")
    if st.button("🗑️ Bersihkan Obrolan", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Assalamu'alaikum Warahmatullahi Wabarakatuh & Sampurasun! Selamat datang di layanan informasi digital **SMP Negeri 1 Tanjungmedar (NESTAND AKBAR)**. Ada yang bisa saya bantu hari ini? 😊"
            }
        ]
        st.rerun()
    st.markdown("---")
    st.markdown("**Bagikan & Media Sosial**")
    link_app = "https://asisten-nestand.streamlit.app"
    pesan_wa = f"Assalamu'alaikum Wr. Wb. & Sampurasun! Yuk tanya-tanya seputar SMP Negeri 1 Tanjungmedar lewat Asisten Virtual Nestand AKBAR di sini: {link_app}"
    url_wa = f"https://api.whatsapp.com/send?text={pesan_wa.replace(' ', '%20')}"
    url_ig = "https://www.instagram.com/smpn1_tanjungmedar/"
    st.link_button("📲 Bagikan ke WhatsApp", url_wa, use_container_width=True)
    st.link_button("📸 Instagram Sekolah", url_ig, use_container_width=True)

# HEADER UTAMA
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

info_sekolah = muat_knowledge_base()

# DAFTAR MODEL TERCEPAT (TANPA CLIENT.MODELS.LIST YANG BIKIN LAMBAT)
DAFTAR_MODEL_CEPAT = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash"
]

# INGATAN OBROLAN
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Assalamu'alaikum Warahmatullahi Wabarakatuh & Sampurasun! Selamat datang di layanan informasi digital **SMP Negeri 1 Tanjungmedar (NESTAND AKBAR)**. Ada yang bisa saya bantu hari ini? 😊"
        }
    ]

# TOMBOL PERTANYAAN CEPAT
col1, col2, col3, col4 = st.columns(4)
pertanyaan_tombol = None
if col1.button("🏫 Profil & Pimpinan", use_container_width=True):
    pertanyaan_tombol = "Siapa Kepala Sekolah dan Wakasek SMP Negeri 1 Tanjungmedar sekarang, serta di mana alamat lengkapnya?"
if col2.button("🌟 Program Unggulan", use_container_width=True):
    pertanyaan_tombol = "Apa saja program unggulan dan ekstrakurikuler di SMP Negeri 1 Tanjungmedar?"
if col3.button("👩‍🏫 Daftar Guru & Staf", use_container_width=True):
    pertanyaan_tombol = "Siapa saja daftar guru dan tenaga kependidikan di SMP Negeri 1 Tanjungmedar?"
if col4.button("🏢 Fasilitas Sekolah", use_container_width=True):
    pertanyaan_tombol = "Apa saja fasilitas laboratorium, ruang belajar, dan sarana prasarana di SMP Negeri 1 Tanjungmedar?"

# TAMPILKAN RIWAYAT OBROLAN
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# INPUT PERTANYAAN
pertanyaan_ketik = st.chat_input("Tanyakan seputar SMPN 1 Tanjungmedar...")
pertanyaan = pertanyaan_tombol if pertanyaan_tombol else pertanyaan_ketik

if pertanyaan:
    st.session_state.messages.append({"role": "user", "content": pertanyaan})
    with st.chat_message("user"):
        st.markdown(pertanyaan)

    # Kirim maksimal 6 pesan terakhir saja agar tetap ringan & ngebut
    riwayat_chat = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part.from_text(text=m["content"])]
        )
        for m in st.session_state.messages[-6:]
    ]

    with st.chat_message("assistant"):
        status = st.empty()
        status.markdown("⚡ *Mengetik...*")
        jawaban_penuh = ""
        model_terpakai = ""

        for nama_model in DAFTAR_MODEL_CEPAT:
            try:
                if "gemini-2.5" in nama_model:
                    konfigurasi = types.GenerateContentConfig(
                        system_instruction=info_sekolah,
                        temperature=0.3,
                        max_output_tokens=700,
                        thinking_config=types.ThinkingConfig(thinking_budget=0)
                    )
                else:
                    konfigurasi = types.GenerateContentConfig(
                        system_instruction=info_sekolah,
                        temperature=0.3,
                        max_output_tokens=700
                    )

                respon_stream = client.models.generate_content_stream(
                    model=nama_model,
                    contents=riwayat_chat,
                    config=konfigurasi
                )
                iter_stream = iter(respon_stream)
                chunk_pertama = next(iter_stream, None)

                if chunk_pertama is not None:
                    status.empty()

                    def pengalir_teks():
                        if chunk_pertama.text:
                            yield chunk_pertama.text
                        for chunk in iter_stream:
                            if chunk.text:
                                yield chunk.text

                    jawaban_penuh = st.write_stream(pengalir_teks())
                    if jawaban_penuh:
                        model_terpakai = nama_model
                        break
            except Exception:
                time.sleep(0.3)
                continue

        if jawaban_penuh:
            st.caption(f"⚡ `{model_terpakai}`")
            st.session_state.messages.append({"role": "assistant", "content": jawaban_penuh})
        else:
            status.error("Server AI Google sedang sibuk. Silakan coba kirim ulang dalam beberapa detik ya! 🙏")
