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

# DATA RESMI SEKOLAH (SUDAH DISARING DARI DATA PRIBADI & SENSITIF)
DATA_SEKOLAH = """
=== PROFIL RESMI SMP NEGERI 1 TANJUNGMEDAR ===
- Nama Sekolah: SMP NEGERI 1 TANJUNGMEDAR (NESTAND AKBAR)
- NPSN: 20208449
- Jenjang / Status: SMP / Negeri (Kepemilikan: Pemerintah Daerah)
- Alamat: Jl. Sindangsari No. 10, RT 02 / RW 01, Kelurahan Jingkang, Kec. Tanjungmedar, Kab. Sumedang, Prov. Jawa Barat, Kode Pos 45354
- Koordinat Geografis: -6.7135 Lintang, 107.8652 Bujur
- SK Pendirian: 182/Kpts/IMB/SMD/1993 (23 September 1993)
- SK Izin Operasional: 0260/O/1994 (5 Oktober 1994)
- Waktu Penyelenggaraan: Pagi / 6 hari
- Biaya & BOS: Tidak memungut iuran (Rp 0/siswa), menerapkan MBS, dan menerima dana BOS
- Kontak Resmi Sekolah: Telp - | Email: smpntanjungmedar@yahoo.co.id
- Listrik & Internet: PLN (5.698 Watt) | Akses Internet 50 Mb

=== FASILITAS SANITASI & UKS ===
- Sumber Air: Sumur terlindungi
- Tempat Cuci Tangan: 17 unit (semua berfungsi baik, tersedia sabun & air mengalir)
- Jamban / Toilet: 6 jamban laki-laki dan 6 jamban perempuan (tipe leher angsa, seluruhnya dapat digunakan)
- Pengelolaan Sampah: Tempat sampah tersedia di setiap kelas, tempat sampah tertutup di jamban perempuan, memiliki TPS tertutup yang diangkut rutin
- Kemitraan Sanitasi: Pemerintah Daerah, Perusahaan Swasta, Puskesmas, dan Lembaga Non-Pemerintah

=== DAFTAR PENDIDIK DAN TENAGA KEPENDIDIKAN (PTK) ===
Kepala Sekolah:
1. Nana Rahayu, S.Pd (L) — PNS | Kepala Sekolah

Wakil Kepala Sekolah & Pimpinan Unit:
2. Cecep Ridwan, S.Pd (L) — Honor Daerah TK.II | Wakasek Kurikulum | Mengajar: PAI & Budi Pekerti
3. Diarta, S.Pd (L) — PNS | Wakasek Sarpras | Mengajar: Matematika (Umum)
4. Entang Purnama, S.Pd, M.M. (P) — PPPK | Wakasek Humas | Mengajar: Bahasa Indonesia
5. Nunung Nurhayati, S.S. (P) — Honor Daerah TK.II | Kepala Perpustakaan | Mengajar: Bahasa Inggris
6. Tati Apriliani, A.Ma.Pd, S.Pd (P) — PNS | Koordinator P5 | Mengajar: Bahasa Sunda, P5
7. Wahyu, S.Pd (L) — PNS | Kepala Lab. Komputer | Mengajar: Informatika, P5
8. Yana Suryana, A.Ma.Pd (L) — PNS | Kepala Lab. IPA | Mengajar: Ilmu Pengetahuan Alam (IPA)
9. Romy Dwi Agustian, S.Pd (L) — Guru Honor Sekolah | Pembina Ekstrakurikuler | Mengajar: PJOK, Prakarya

Dewan Guru:
10. Amar, A.Ma.Pd, S.Pd (L) — PNS | Mengajar: Bahasa Inggris
11. Ani Rahmawati, S.Sn (P) — PPPK | Mengajar: Seni Musik, Seni dan Budaya
12. Apong Jubaedah, A.Ma.Pd, S.Pd (P) — PNS | Mengajar: Bahasa Indonesia
13. Heni Purnamasari, S.Pd (P) — Guru Honor Sekolah | Mengajar: BK (Bimbingan dan Konseling), IPA
14. Iis Trisnawati, S.Akun (P) — Guru Honor Sekolah | Mengajar: Ilmu Pengetahuan Sosial (IPS)
15. Indi Fitriyani, S.Sos. (P) — Guru Honor Sekolah | Mengajar: BK (Bimbingan dan Konseling)
16. Ratnasih, A.Md, S.Pd.I (P) — PPPK | Mengajar: PAI & Budi Pekerti
17. Yeni Mulyani, S.Sos (P) — PPPK | Mengajar: Pendidikan Pancasila / PPKn

Tenaga Kependidikan:
18. Ai Rohmayati, S.Sos (P) — Honor Daerah TK.II | Tugas: Bendahara BOS/BOP, Pelaksana PBJ
19. Ai Rohaeni, S.AP (P) — Tenaga Honor Sekolah
20. Asep Sopian Bukhori Muslim, S.Kom (L) — Tenaga Honor Sekolah
21. Asep Suparman (L) — Tenaga Honor Sekolah
"""

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

# FUNGSI MEMBACA BASIS PENGETAHUAN DARI knowledge_base.md + DATA_SEKOLAH
@st.cache_data(ttl=600)
def muat_knowledge_base():
    dasar = "Kamu adalah Asisten Virtual Resmi SMP Negeri 1 Tanjungmedar (NESTAND AKBAR)."
    if os.path.exists("knowledge_base.md"):
        with open("knowledge_base.md", "r", encoding="utf-8") as f:
            dasar = f.read()
    return f"{dasar}\n\n{DATA_SEKOLAH}"

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
        .hero-text {{
            text-align: center;
            width: 100%;
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

# 2. MEMUAT BUKU INGATAN RESMI (knowledge_base.md + DATA_SEKOLAH)
info_sekolah = muat_knowledge_base()

# DAFTAR MODEL AI TERCEPAT + DETEKSI OTOMATIS AKUN PAK WEI
@st.cache_data(ttl=3600)
def cari_daftar_model_ai():
    # Urutan prioritas utama yang terbukti paling cepat & aktif
    daftar = [
        "gemma-4-26b-a4b-it",
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash"
    ]
    # Otomatis menambahkan model resmi lain yang benar-benar tersedia di API Key Pak Wei
    try:
        for m in client.models.list():
            nama = m.name.replace("models/", "")
            if ("gemma" in nama or "flash" in nama) and not any(
                x in nama for x in ["embedding", "imagen", "veo", "tts", "audio", "robotics", "computer"]
            ):
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
            "content": "Assalamu'alaikum Warahmatullahi Wabarakatuh & Sampurasun! Selamat datang di layanan informasi digital **SMP Negeri 1 Tanjungmedar (NESTAND AKBAR)**. Ada yang bisa saya bantu hari ini? 😊"
        }
    ]

# TOMBOL PERTANYAAN CEPAT (QUICK PROMPTS)
col1, col2, col3, col4 = st.columns(4)
pertanyaan_tombol = None
if col1.button("🏫 Profil & Pimpinan", use_container_width=True):
    pertanyaan_tombol = "Siapa Kepala Sekolah dan Wakasek SMP Negeri 1 Tanjungmedar sekarang, serta di mana alamat lengkapnya?"
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
        placeholder_jawaban = st.empty()
        jawaban_penuh = ""
        model_terpakai = ""
        error_terakhir = ""

        # Maksimal 2 putaran jika semua jalur sempat sibuk sesaat
        for putaran in range(2):
            for nama_model in semua_model:
                placeholder_jawaban.markdown(f"⚡ *Menyiapkan jawaban ({nama_model})...*")
                try:
                    if "gemini-2.5" in nama_model:
                        konfigurasi = types.GenerateContentConfig(
                            system_instruction=info_sekolah,
                            temperature=0.4,
                            thinking_config=types.ThinkingConfig(thinking_budget=0)
                        )
                    else:
                        konfigurasi = types.GenerateContentConfig(
                            system_instruction=info_sekolah,
                            temperature=0.4
                        )

                    respon_stream = client.models.generate_content_stream(
                        model=nama_model,
                        contents=riwayat_chat,
                        config=konfigurasi
                    )
                    for chunk in respon_stream:
                        if chunk.text:
                            jawaban_penuh += chunk.text
                            placeholder_jawaban.markdown(jawaban_penuh + "▌")

                    if jawaban_penuh:
                        placeholder_jawaban.markdown(jawaban_penuh)
                        model_terpakai = nama_model
                        break
                except Exception as e:
                    error_terakhir = str(e)
                    jawaban_penuh = ""
                    # Kalau error 404 (model tidak didukung), langsung lompat tanpa nunggu
                    if "404" not in error_terakhir:
                        time.sleep(1.5)
                    continue
            if jawaban_penuh:
                break

        if jawaban_penuh:
            st.caption(f"⚡ Dijawab oleh AI: `{model_terpakai}`")
            st.session_state.messages.append({"role": "assistant", "content": jawaban_penuh})
        else:
            placeholder_jawaban.error("Server AI Google sedang sangat padat di jam sibuk ini. Tunggu 5 detik lalu klik tombol atau kirim ulang pertanyaan ya, Pak Wei! 🙏")
