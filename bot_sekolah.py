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

# FUNGSI TAMPILAN GLASSMORPHISM + WALLPAPER BENING + LOGO
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
            background: rgba(10, 25, 47, 0.2) !important;
            backdrop-filter: blur(4px);
        }}
        div[data-testid="stBottom"] {{
            background: transparent !important;
        }}
        section[data-testid="stSidebar"] {{
            background: rgba(15, 23, 42, 0.84) !important;
            backdrop-filter: blur(14px);
            border-right: 1px solid rgba(56, 189, 248, 0.35);
        }}
        .hero-box {{
            background: rgba(15, 23, 42, 0.75);
            backdrop-filter: blur(14px);
            border: 1px solid rgba(125, 211, 252, 0.45);
            border-radius: 18px;
            padding: 20px 28px;
            margin-bottom: 18px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }}
        .hero-logo {{
            width: 82px;
            height: 82px;
            object-fit: contain;
            filter: drop-shadow(0 4px 10px rgba(0,0,0,0.4));
        }}
        .hero-text {{
            text-align: left;
        }}
        .hero-title {{
            font-size: 1.95rem;
            font-weight: 800;
            background: linear-gradient(90deg, #38bdf8, #ffffff, #7dd3fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
            line-height: 1.2;
        }}
        .hero-sub {{
            color: #e2e8f0;
            font-size: 0.96rem;
            margin-top: 4px;
        }}
        .hero-badge {{
            display: inline-block;
            margin-top: 8px;
            padding: 4px 14px;
            border-radius: 999px;
            background: rgba(56, 189, 248, 0.25);
            border: 1px solid rgba(125, 211, 252, 0.55);
            color: #e0f2fe;
            font-size: 0.82rem;
            font-weight: 600;
        }}
        div[data-testid="stChatMessage"] {{
            background: rgba(15, 23, 42, 0.78) !important;
            backdrop-filter: blur(12px);
            border: 1px solid rgba(148, 163, 184, 0.3);
            border-radius: 16px;
            padding: 14px 18px;
            margin-bottom: 10px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        }}
        div[data-testid="stChatInput"] {{
            background: rgba(15, 23, 42, 0.9) !important;
            border-radius: 14px;
            border: 1px solid rgba(56, 189, 248, 0.5);
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
        st.markdown(f'<div style="text-align:center;"><img src="{url_logo}" width="95"></div>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; margin-bottom:0;'>SMPN 1 Tanjungmedar</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#7dd3fc;'><b>NESTAND</b> • Kab. Sumedang</p>", unsafe_allow_html=True)
    st.info("🌄 *Dari Bukit Menebar Cahaya — MENCRANG!*")
    st.markdown("---")
    st.markdown("**Visi Sekolah: AKBAR**")
    st.caption("• **AKBAR:** Aktif, Kreatif, Bersama, Adab, Religius")
    st.markdown("---")
    if st.button("🗑️ Bersihkan Obrolan", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Sampurasun & Halo! Selamat datang di layanan informasi digital **SMP Negeri 1 Tanjungmedar (NESTAND)**. *Dari Bukit Menebar Cahaya — MENCRANG!* Ada yang bisa saya bantu hari ini? 😊"
            }
        ]
        st.rerun()

# HEADER UTAMA DENGAN LOGO SEKOLAH
logo_html = f'<img src="{url_logo}" class="hero-logo">' if url_logo else '<span style="font-size:3rem;">🎓</span>'
st.markdown(
    f"""
    <div class="hero-box">
        {logo_html}
        <div class="hero-text">
            <h1 class="hero-title">Asisten Virtual Nestand AKBAR</h1>
            <div class="hero-sub">Pusat Informasi Digital SMP Negeri 1 Tanjungmedar • Sumedang</div>
            <div class="hero-badge">✨ AKBAR dalam Prestasi & Karakter • MENCRANG ✨</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Menghubungkan ke otak AI Google
client = genai.Client(api_key=KUNCI_AI)

# 2. BUKU INGATAN RESMI SMP NEGERI 1 TANJUNGMEDAR (NESTAND)
info_sekolah = """
Kamu adalah Asisten Virtual AI Resmi yang sangat cerdas, ramah, luwes, hangat, dan komunikatif untuk SMP Negeri 1 Tanjungmedar (NESTAND).
Jawablah semua pertanyaan siswa, guru, orang tua, atau tamu sekolah berdasarkan arsip resmi berikut:

1. IDENTITAS SEKOLAH:
- Nama Sekolah: SMP Negeri 1 Tanjungmedar (Nama populer: NESTAND - Negeri 1 Tanjungmedar).
- Alamat: Jalan Sindangsari No. 10, Desa Jingkang, Kecamatan Tanjungmedar, Kabupaten Sumedang, Provinsi Jawa Barat.
- Karakter Wilayah: Pedesaan, perbukitan/lereng gunung, dikelilingi lahan pertanian dan perkebunan (cabai, kencur, singkong).
- Kepala Sekolah: Bapak Dadan Andana.
- Guru Informatika & Pengembang Digitalisasi Sekolah: Bapak Wahyu, S.Pd (Pa Wei).
- Gambaran Data Murid (referensi arsip): Sekitar 291 murid (Kelas VII: 101 murid dengan pembahasan 4 rombel; mencakup kelas VII, VIII, dan IX).

2. VISI, JARGON, DAN SEMBOYAN:
- Visi Utama (AKBAR):
  "Pusat penggerak kepemimpinan literasi dan pemberdayaan insan didik yang Aktif, Kreatif, Bersama, ber-Adab, dan Religius (AKBAR) berbasis sains, teknologi, dan Al-Qur'an."
- Kepanjangan AKBAR: Aktif, Kreatif, Bersama, Adab, Religius.
- Jargon Identitas: "AKBAR dalam prestasi dan karakter."
- Jargon Sekolah: "DARI BUKIT MENEBAR CAHAYA — MENCRANG".
- Semboyan Budaya Kerja: "PROVE WE EXIST BECAUSE OF WORKING".
- Identitas Pertumbuhan: Internal Growth (Nisita Cala Sinudarsana), External Growth (Kebhinekaan Global), nilai Kreatif, Gotong Royong, dan Mandiri.

3. PROGRAM UNGGULAN & KEGIATAN SEKOLAH:
- Program STAR:
  * S (Sport): Olahraga.
  * T (Science / Technology): Sains & Teknologi (komunitas JAQ-IT, Olimpiade Informatika).
  * A (Art): Seni & Budaya (Sundanese Ethnic Music Class).
  * R (Religious): Keagamaan (komunitas IRMALAT).
- Ekstrakurikuler & Komunitas: Pramuka, Paskibra, PMR, OSIS, JONEST, IRMALAT, JAQ-IT, Sundanese Ethnic Music Class, dan Olimpiade.
- Program NISCALA: KIN, K3N, KKBN, NDLC, dan NMB.
- Kurikulum & Metode: Kurikulum Operasional Mandiri Berubah, Pembelajaran Mendalam (Deep Learning), PESAT Method, KUKA, TUMBUH (growth mindset), E-library, Penguatan Literasi & Numerasi, serta pengembangan menuju ISO 9001:2000.
- Projek Pembelajaran & Karakter (P5 & NSR):
  * P5 Gaya Hidup Berkelanjutan: Budidaya tanaman cabai di lahan kosong sekolah.
  * Projek Kewirausahaan Kelas VIII: Pembuatan kipas dari bambu.
  * Program NSR: Kunjungan dunia usaha menjahit ke Penjahit Neng Susi di Cimayang.
- Kemitraan: Puskesmas dan GENRE Sumedang.

4. DIGITALISASI & INOVASI SEKOLAH:
- Pemanfaatan LKPD digital (TTS interaktif), AI, Google Workspace, akun belajar.id, serta pengembangan Aplikasi Digital Nestand dan Absensi Digital Nestand.
"""

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
            "content": "Sampurasun & Halo! Selamat datang di layanan informasi digital **SMP Negeri 1 Tanjungmedar (NESTAND)**. *Dari Bukit Menebar Cahaya — MENCRANG!* Ada yang bisa saya bantu hari ini? 😊"
        }
    ]

# TOMBOL PERTANYAAN CEPAT (QUICK PROMPTS)
col1, col2, col3, col4 = st.columns(4)
pertanyaan_tombol = None
if col1.button("🏫 Profil & Alamat", use_container_width=True):
    pertanyaan_tombol = "Di mana alamat lengkap dan bagaimana profil SMP Negeri 1 Tanjungmedar?"
if col2.button("✨ Visi AKBAR", use_container_width=True):
    pertanyaan_tombol = "Jelaskan visi dan nilai karakter AKBAR di NESTAND!"
if col3.button("⭐ Program STAR", use_container_width=True):
    pertanyaan_tombol = "Apa saja kegiatan dan komunitas dalam program STAR?"
if col4.button("💻 Digitalisasi Sekolah", use_container_width=True):
    pertanyaan_tombol = "Apa saja inovasi digitalisasi dan projek P5 yang ada di NESTAND?"

# Menampilkan riwayat obrolan di layar
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Menangkap input dari ketikan manual ATAU klik tombol cepat
pertanyaan_ketik = st.chat_input("Ngobrol atau tanyakan apa saja seputar SMP Negeri 1 Tanjungmedar...")
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
                            temperature=0.5
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
