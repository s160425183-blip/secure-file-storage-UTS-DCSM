# Secure Distributed File Storage System

**Proyek UTS — Network Security / Secure Systems**

## Identitas Mahasiswa

* **Nama:** Maulana Ikromullah
* **NRP:** 160425183
* **Platform:** Ubuntu Server
* **Bahasa:** Python
* **Deployment:** Docker Compose

## 1. Deskripsi Proyek

Secure Distributed File Storage System adalah aplikasi penyimpanan file berbasis gRPC yang menerapkan mekanisme autentikasi, otorisasi, enkripsi komunikasi, pemeriksaan integritas file, dan pencatatan aktivitas.

Aplikasi menyediakan layanan upload dan download file. Setiap file yang diunggah dihitung nilai SHA-256-nya untuk mendeteksi perubahan data. Akses pengguna dikendalikan menggunakan JSON Web Token (JWT), Role-Based Access Control (RBAC), dan security label.

Server dijalankan menggunakan Docker Compose, sedangkan file dan log disimpan melalui persistent storage agar tetap tersedia ketika container dibuat ulang.

## 2. Fitur Keamanan

* **gRPC:** komunikasi antara client dan server.
* **JWT Authentication:** memvalidasi token pengguna.
* **RBAC:** membatasi akses berdasarkan role.
* **Security Label:** membedakan file berlabel `PUBLIC` dan `SECRET`.
* **TLS/mTLS:** mengenkripsi komunikasi dan memverifikasi sertifikat client.
* **SHA-256:** memeriksa integritas file.
* **Audit Logging:** mencatat aktivitas upload dan download, termasuk hasil akses.
* **Persistent Storage:** menyimpan file dan log di folder host melalui Docker bind mount.

## 3. Teknologi

* Python 3.12
* gRPC dan Protocol Buffers
* PyJWT
* OpenSSL
* Docker
* Docker Compose

## 4. Struktur Direktori

```text
secure-file-storage/
├── client/          # Program client
├── server/          # Server dan modul keamanan
├── proto/           # Definisi layanan gRPC
├── certs/           # Sertifikat dan key lokal
├── storage/         # File tersimpan
├── logs/            # Audit log dan checksum
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
└── README.md
```

Private key, token, dan file pengujian tidak boleh diunggah ke repository publik.

## 5. Persyaratan

Sebelum menjalankan aplikasi, siapkan:

* Ubuntu Server atau lingkungan Linux yang sesuai.
* Python 3 dan `venv`.
* Docker Engine dan Docker Compose.
* Sertifikat CA, sertifikat server, serta private key server.
* Sertifikat client dan private key client untuk koneksi mTLS.

Private key harus dibuat atau disediakan secara lokal dan tidak disimpan dalam repository publik.

## 6. Instalasi dan Konfigurasi

Clone repository:

```bash
git clone <URL_REPOSITORY>
cd secure-file-storage
```

Buat virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Instal dependensi:

```bash
pip install -r requirements.txt
```

Pastikan file sertifikat yang diperlukan tersedia pada direktori `certs/`. Client memerlukan `ca.crt`, `client.crt`, dan `client.key`. Server memerlukan `ca.crt`, `server.crt`, dan `server.key`.

## 7. Menjalankan dengan Docker Compose

Bangun image dan jalankan server:

```bash
docker compose up -d --build
```

Periksa status container:

```bash
docker compose ps
```

Lihat log server:

```bash
docker compose logs --tail=50
```

Menghentikan layanan:

```bash
docker compose down
```

Folder `storage/` dan `logs/` dipasang sebagai persistent storage melalui Docker Compose.

## 8. Pengujian Upload dan Download

Aktifkan virtual environment dan pastikan server sudah berjalan.

Upload file:

```bash
echo "Contoh file pengujian" > test.txt
PYTHONPATH=. python client/client.py upload test.txt
```

Download file:

```bash
PYTHONPATH=. python client/client.py download test.txt
```

Verifikasi checksum file hasil download:

```bash
sha256sum downloaded_test.txt
```

Nilai SHA-256 hasil download harus sama dengan checksum file yang diverifikasi server.

## 9. Pengujian Keamanan

Pengujian yang telah dilakukan selama implementasi meliputi:

1. Upload dan download melalui gRPC.
2. Validasi autentikasi JWT.
3. Pengujian izin akses berdasarkan role dan security label.
4. Verifikasi integritas file menggunakan SHA-256.
5. Pencatatan aktivitas melalui audit log.
6. Pengujian komunikasi menggunakan TLS/mTLS.
7. Pengujian deteksi perubahan file (*tampering detection*).
8. Pengujian deployment menggunakan Docker Compose dan persistent storage.

Pada pengujian tampering, perubahan isi file menyebabkan checksum tidak cocok dan server menghasilkan pesan `INTEGRITY FAILED: Checksum file tidak sesuai`.

## 10. Lokasi Data dan Log

* `storage/`: file yang diunggah.
* `logs/audit.log`: catatan aktivitas.
* `logs/checksums.json`: checksum file yang disimpan.

Data tersebut berada pada folder host yang dipasang ke container sehingga tidak bergantung pada umur container.

## 11. Catatan Keamanan

* Jangan mengunggah private key, password, atau JWT yang masih berlaku.
* Jangan memasukkan `ca.key`, `client.key`, atau `server.key` ke image Docker.
* Gunakan `.gitignore` untuk mengecualikan private key, file runtime, dan file pengujian.
* Konfigurasi dan sertifikat harus disesuaikan sebelum server digunakan dari komputer client lain.

## 12. Kesimpulan

Proyek ini mengimplementasikan penyimpanan file dengan autentikasi, kontrol akses, enkripsi komunikasi, pemeriksaan integritas, audit log, dan deployment menggunakan Docker Compose. Pengujian upload, download, verifikasi SHA-256, serta deteksi perubahan file digunakan untuk mengevaluasi fungsi utama sistem.

---

**Mahasiswa:** Maulana Ikromullah
**NRP:** 160425183
