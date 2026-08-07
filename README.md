# 🎮 LaWi Game Platform

**4 farklı oyunu tek çatı altında toplayan Python tabanlı oyun platformu**
---

## 📖 Proje Hakkında

**LaWi Game Platform**, kullanıcı giriş/kayıt sistemi ve 4 farklı oyunu tek bir arayüzde toplayan **ölçeklenebilir** bir oyun platformudur.

Tüm oyunlar modüler yapıda tasarlanmış olup, her biri bağımsız olarak çalışabilir.

---

## ✨ Özellikler

| Özellik | Açıklama |
|---------|----------|
| 🔐 **Kullanıcı Yönetimi** | SQLite tabanlı giriş/kayıt sistemi |
| 🎮 **4 Oyun** | Farklı türlerde oyun deneyimi |
| 🗄️ **Veritabanı** | Skorlar ve kullanıcılar SQLite ile saklanır |
| 🎨 **Modern Arayüz** | Tkinter + PIL ile şık tasarım |
| 📊 **Skor Takibi** | Her oyun için ayrı skor tablosu |
| 🔄 **Modüler Yapı** | Yeni oyun eklemek kolay |

---

## 🎯 Oyunlar

| 🚀 Astro Wars | 👾 Uzay Kaçışı |
|:---:|:---:|
| Uzaylılara karşı galaksiyi koru! | Tehlikelerden kaçarak uzayda yol al! |
| [🎮 Oyna]() | [🎮 Oyna]() |

| 🐟 Balık Avı | 🐍 Pembe Yılan Macerası |
|:---:|:---:|
| En lezzetli balıkları yakala! | Pembe yılanla macera dolu yolculuk! |
| [🎮 Oyna]() | [🎮 Oyna]() |

---

## 🛠️ Teknolojiler

| Teknoloji | Açıklama |
|-----------|----------|
| 🐍 **Python 3.9+** | Ana programlama dili |
| 🎮 **Pygame** | Oyun motoru ve grafik |
| 🖥️ **Tkinter** | Grafik arayüz (GUI) |
| 🗄️ **SQLite** | Veritabanı yönetimi |
| 📷 **PIL** | Görsel işleme |

---

## 🚀 Kurulum

### 1️⃣ Projeyi Klonla
```bash
git clone https://github.com/lunaimer/LaWi-Game-Platform.git
cd LaWi-Game-Platform/miami
```

### 2️⃣ Gerekli Kütüphaneleri Yükle
```bash
pip install pygame pillow
```

### 3️⃣ Oyunu Başlat
```bash
python login_page.py
```

> 🔑 **Test Hesabı:** `admin` / `admin`

---

## 📂 Proje Yapısı

```
miami/
├── login_page.py          # Ana giriş ekranı
├── oyunlar/               # Tüm oyunlar
│   ├── astro wars/        # 🚀 Astro Wars
│   ├── balık avı/         # 🐟 Balık Avı
│   ├── pembe yilan macerasi/ # 🐍 Pembe Yılan
│   └── uzay kaçışı/       # 👾 Uzay Kaçışı
├── *.png / *.jpg          # Görsel dosyaları
├── *.wav                  # Ses dosyaları
└── README.md
```

---

## 🤝 Katkıda Bulunma

1. Projeyi forkla 🍴
2. Yeni bir branch oluştur (`git checkout -b feature/ekleme`)
3. Değişikliklerini commit et (`git commit -m "Yeni özellik eklendi"`)
4. Branch'i push et (`git push origin feature/ekleme`)
5. Pull Request aç 🚀

---

## 📄 Lisans

Bu proje **MIT Lisansı** ile lisanslanmıştır.  
Daha fazla bilgi için [LICENSE](LICENSE) dosyasına bakabilirsiniz.

---

⭐ **Beğendiysen yıldız vermeyi unutma!**  
📬 İletişim: [GitHub](https://github.com/lunaimer)
