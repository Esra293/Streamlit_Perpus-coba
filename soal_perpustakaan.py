import pandas as pd
import streamlit as st

# ===== Data =====
KATALOG_AWAL = {
    "B01": {"judul": "Algoritma Dasar",       "stok": 2},
    "B02": {"judul": "Struktur Data Python",  "stok": 1},
    "B03": {"judul": "Basis Data Relasional", "stok": 2},
    "B04": {"judul": "Statistika Dasar",      "stok": 1},
    "B05": {"judul": "Kalkulus 1",            "stok": 3},
}


def buat_katalog():
    return {kode: dict(data) for kode, data in KATALOG_AWAL.items()}


# ===== Logika =====

def pinjam_buku(katalog, pinjaman, nama, kode):
    # cek 1 — nama wajib diisi
    if nama == "":
        return "Nama peminjam wajib diisi!"

    # cek 2 — orang ini sudah pinjam buku yang sama
    for p in pinjaman:
        if p["nama"] == nama and p["kode"] == kode:
            return "Buku ini sudah kamu pinjam!"

    # cek 3 — stok habis
    if katalog[kode]["stok"] == 0:
        return "Stok buku habis!"

    # lolos semua cek → proses peminjaman
    katalog[kode]["stok"] -= 1
    pinjaman.append({"nama": nama, "kode": kode})
    return None


def kembalikan_buku(katalog, pinjaman, nama, kode):
    # cek 1 — nama wajib diisi
    if nama == "":
        return "Nama peminjam wajib diisi!"

    # cek 2 — cari data peminjaman yang cocok
    data_ditemukan = None
    for p in pinjaman:
        if p["nama"] == nama and p["kode"] == kode:
            data_ditemukan = p
            break

    if data_ditemukan is None:
        return "Data peminjaman tidak ditemukan!"

    # proses pengembalian
    pinjaman.remove(data_ditemukan)
    katalog[kode]["stok"] += 1
    return None


def rekap_per_peminjam(pinjaman):
    rekap = {}
    for p in pinjaman:
        nama = p["nama"]
        kode = p["kode"]
        if nama not in rekap:
            rekap[nama] = set()
        rekap[nama].add(kode)
    return rekap


# ===== Tampilan =====

def form_buku():
    nama = st.text_input("Nama peminjam").strip()

    katalog = st.session_state["katalog"]
    pilihan = [f"{kode} - {data['judul']}" for kode, data in katalog.items()]
    pilihan_dipilih = st.selectbox("Buku", pilihan)
    kode = pilihan_dipilih[:3]

    kol1, kol2 = st.columns(2)
    pinjam  = kol1.button("📖 Pinjam")
    kembali = kol2.button("↩️ Kembalikan")

    return nama, kode, pinjam, kembali


def tampilkan_katalog(katalog):
    st.table(pd.DataFrame.from_dict(katalog, orient="index"))


def tampilkan_pinjaman(pinjaman):
    if pinjaman:
        st.table(pd.DataFrame(pinjaman))
    else:
        st.info("Belum ada buku yang sedang dipinjam.")


def tampilkan_rekap(rekap):
    if rekap:
        # versi lama pakai list comprehension (susah dibaca):
        # baris = [(nama, ", ".join(sorted(kode)), len(kode)) for nama, kode in sorted(rekap.items())]

        # versi baru — loop biasa, mudah dibaca:
        baris = []
        for nama, kode_set in sorted(rekap.items()):
            kode_urut  = sorted(kode_set)        # urutkan set jadi list: ["B01", "B05"]
            kode_str   = ", ".join(kode_urut)    # gabung jadi string: "B01, B05"
            jumlah     = len(kode_set)           # hitung jumlah buku: 2
            baris.append((nama, kode_str, jumlah))

        df = pd.DataFrame(baris, columns=["Nama", "Buku", "Jumlah"])
        df = df.set_index("Nama")
        st.table(df)
    else:
        st.info("Belum ada peminjam.")


# ===== Aplikasi =====
st.title("📚 Peminjaman Buku Perpustakaan")

if "katalog" not in st.session_state:
    st.session_state["katalog"] = buat_katalog()
    st.session_state["pinjaman"] = []

katalog  = st.session_state["katalog"]
pinjaman = st.session_state["pinjaman"]

nama, kode, pinjam, kembali = form_buku()

if pinjam:
    pesan = pinjam_buku(katalog, pinjaman, nama, kode)
    if pesan:
        st.error(pesan)
    else:
        judul = katalog[kode]["judul"]
        st.success(f"{nama} berhasil meminjam {judul} ✅")

if kembali:
    pesan = kembalikan_buku(katalog, pinjaman, nama, kode)
    if pesan:
        st.error(pesan)
    else:
        judul = katalog[kode]["judul"]
        st.success(f"{nama} berhasil mengembalikan {judul} ✅")

st.subheader("📦 Stok Buku")
tampilkan_katalog(katalog)

st.subheader("📋 Sedang Dipinjam")
tampilkan_pinjaman(pinjaman)

st.subheader("👤 Rekap Per Peminjam")
tampilkan_rekap(rekap_per_peminjam(pinjaman))