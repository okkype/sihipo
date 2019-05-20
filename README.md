# SIHIPO
Hidroponik adalah salah satu solusi yang tepat guna untuk mengatasi masalah kurangnya suplay sayuran segar di Kota Gresik, hal ini disebabkan karena kualitas tanah yang kurang mendukung pertumbuhan sayuran. Hidroponik adalah metode penanaman dengan hanya menggunakan air dan nutrisi tanpa menggunakan tanah. Hidroponik juga bisa dibangun di berbagai lokasi seperti di atap, pagar, bahkan di dalam ruangan.

Karena menggunakan air bernutrisi sebagai faktor utama maka sistem hidroponik butuh pengawasan ekstra karena sifat dasar air yang lebih mudah terpengaruh oleh lingkungan daripada tanah. Di sisi lain, masyarakat kota pada umumnya memiliki aktifitas yang padat sehingga tidak memungkinkan untuk melakukan pengawasan yang intensif terhadap tanaman hidroponik mereka.

Oleh karena itu, dibuatlah sebuah sistem informasi pengawasan dan kendali hidroponik yang bertujuan untuk meminimalisir aktifitas manusia dalam mengawasi dan mengatur ekosistem mikro penunjang hidroponik. Serta mempermudah pencatatan konduktifitas, keasaman, suhu larutan, suhu udara, dan kelembapan dan pelaporan ketidak sesuaian kondisi keasaman/konduktifitas/suhu, aktifitas dari sensor, dan aktifitas dari perangkat kontrol dengan nama SIHIPO.

SIHIPO (Sistem Informasi Hidroponik) adalah Sistem Informasi yang menangani templating, pendataan, penanganan, dan automasi sistem tanam hidroponik dan akuaponik.

## Kebutuhan

1. WEMOS SENSOR (https://github.com/okkype/wemos_sensor.git)
2. WEMOS RELAY (https://github.com/okkype/wemos_relay.git)
3. Komputer (Rekomendasi Raspberry Pi 3/Zero, image bisa diunduh di https://github.com/okkype/sihipo/releases/download/v1.1.0/sihipo_v1.1.0.zip)
4. Python 2.7+ (https://www.python.org/downloads/)
5. PIP (https://pip.pypa.io/en/stable/installing/)
6. Git (https://git-scm.com/downloads)

## Installasi

1. Clone Repo

   `git clone https://github.com/okkype/sihipo.git`

2. Install Requirement

   `cd sihipo`
   
   `pip install -r requirement.txt`

3. Migrate dan Tambah Super User

   `python manage.py migrate`
   
   `python manage.py createsuperuser`

4. Load Fixture

   `python manage.py loaddata sihipo_root_data.json`

5. Run

   `python manage.py runserver 0.0.0.0:8000`
   
## Menggunakan Raspberry Pi Image

1. Setelah unduh berkas zip, siapkan MicroSD minimun 2GB, kemudian tulis image menggunakan https://www.balena.io/etcher/ (tidak perlu mengekstrak berkas zip tersebut)
2. Jalankan MicroSD tersebut pada Raspberry Pi, apabila tidak ada masalah akan muncul SSID Wifi dengan nama `SIHIPO` dan kata sandi `sistemhidroponik`
3. Masuk jaringan Wifi kemudian masuk ke SSH dengan alamat `local.sihipo.net` nama pengguna `pi` kata sandi `raspberry` kemudian gunakan perintah `sudo raspi-config` , cari opsi `resize partition` untuk memenuhi partisi yang masih kosong
4. Untuk masuk ke aplikasi SIHIPO, buka peramban web, masukkan alamat https://local.sihipo.net/ , kemudian masuk menggunakan nama pengguna `admin` kata sandi `administrator`
5. Petunjuk penggunaan bisa dilihat di https://www.youtube.com/watch?v=HpNHy1K7S1w
