import tkinter as tk
from tkinter import messagebox
import sqlite3
import random
from PIL import Image, ImageTk
import subprocess
import os

# ------------------ DATABASE ------------------
conn = sqlite3.connect('game_platform.db')
cursor = conn.cursor()

# ------------------ TABLO OLUŞTURMA ------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    game_name TEXT NOT NULL,
    score INTEGER NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()


# ------------------ ANA UYGULAMA ------------------
class GamePlatformApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Wawi & Luna Game's")
        self.root.geometry("1400x900")  # Daha büyük ekran
        self.root.resizable(False, False)
        self.root.configure(bg="#0f0c29")

        # Oyun ikonlarını yükle
        self.load_game_icons()

        # Mevcut kullanıcı
        self.current_user = None
        self.message_label = None

        # Canvas (arka plan)
        self.canvas = tk.Canvas(self.root, width=1400, height=900, highlightthickness=0, bg="#0f0c29")
        self.canvas.pack(fill="both", expand=True)

        # Yıldızlar oluştur
        self.create_stars()

        self.login_screen()

    def load_game_icons(self):
        """Oyun ikonlarını yükle"""
        self.game_icons = {}
        try:
            # Oyun ikonlarını yükle (dosya uzantılarını eklemeyi unutmayın)
            icon_files = {
                "Astro Wars": "astroWars_icon.png",
                "Uzay Kaçışı": "uzayKacisi_icon.png",
                "Balık Avı": "balikAvi.icon.png",
                "Pembe Yılan Macerası": "pembeyilanMacerasi_icon.png"
            }

            for game_name, icon_file in icon_files.items():
                try:
                    image = Image.open(icon_file)
                    image = image.resize((120, 120), Image.LANCZOS)  # İkon boyutunu BÜYÜTTÜM
                    self.game_icons[game_name] = ImageTk.PhotoImage(image)
                except Exception as e:
                    print(f"{icon_file} yüklenirken hata: {e}")
                    # İkon yüklenemezse yerine metin kullan
                    self.game_icons[game_name] = game_name
        except Exception as e:
            print(f"İkon yükleme hatası: {e}")
            # PIL yoksa veya başka hata olursa
            self.game_icons = {
                "Astro Wars": "🚀",
                "Uzay Kaçışı": "👾",
                "Balık Avı": "🐟",
                "Pembe Yılan Macerası": "🐍"
            }

    def create_stars(self):
        """Arka plana yıldız efekti ekle"""
        for _ in range(150):  # Daha fazla yıldız
            x = random.randint(0, 1400)
            y = random.randint(0, 900)
            size = random.randint(1, 4)
            color = random.choice(["white", "#f8f9fa", "#e9ecef", "#dee2e6", "#ffeb3b"])
            self.canvas.create_oval(x, y, x + size, y + size, fill=color, outline="")

    def show_message(self, message, color="#00ff00"):
        """Ekranda büyük mesaj göster"""
        if self.message_label:
            self.message_label.destroy()

        self.message_label = tk.Label(self.canvas, text=message, font=("Arial", 24, "bold"),
                                      bg="#0f0c29", fg=color)
        self.message_label.place(relx=0.5, rely=0.8, anchor="center")

        # 3 saniye sonra mesajı kaldır
        self.root.after(3000, self.clear_message)

    def clear_message(self):
        """Mesajı temizle"""
        if self.message_label:
            self.message_label.destroy()
            self.message_label = None

    # ------------------ PANEL OLUŞTURUCU ------------------
    def create_panel(self, title, width=600, height=500):  # Daha büyük panel
        panel = tk.Frame(self.canvas, bg="#1a1a40", bd=0, highlightthickness=0,
                         relief="ridge", width=width, height=height)
        panel.place(relx=0.5, rely=0.5, anchor="center")

        # Panel başlık çerçevesi
        title_frame = tk.Frame(panel, bg="#8a2be2", height=70)
        title_frame.pack(fill="x", pady=(0, 30))
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text=title, font=("Arial", 24, "bold"),  # Daha büyük font
                 fg="white", bg="#8a2be2").pack(expand=True)

        return panel

    # ------------------ GİRİŞ EKRANI ------------------
    def login_screen(self):
        self.clear_window()
        self.create_stars()

        panel = self.create_panel("🚀 WaLu'ya Hoşgeldiniz", 650, 550)

        # Ana içerik çerçevesi
        content_frame = tk.Frame(panel, bg="#1a1a40")
        content_frame.pack(fill="both", expand=True, padx=40, pady=20)

        # Kullanıcı adı
        user_frame = tk.Frame(content_frame, bg="#1a1a40")
        user_frame.pack(fill="x", pady=15)

        tk.Label(user_frame, text="👤 Kullanıcı Adı", font=("Arial", 14, "bold"),  # Daha büyük
                 bg="#1a1a40", fg="#e9ecef", anchor="w").pack(fill="x")
        self.username_entry = tk.Entry(user_frame, font=("Arial", 14), width=25,  # Daha büyük
                                       bd=2, relief="flat", bg="#2c2c54", fg="white",
                                       insertbackground="white")
        self.username_entry.pack(fill="x", pady=(8, 0), ipady=8)  # Daha büyük

        # Şifre
        pass_frame = tk.Frame(content_frame, bg="#1a1a40")
        pass_frame.pack(fill="x", pady=15)

        tk.Label(pass_frame, text="🔒 Şifre", font=("Arial", 14, "bold"),  # Daha büyük
                 bg="#1a1a40", fg="#e9ecef", anchor="w").pack(fill="x")
        self.password_entry = tk.Entry(pass_frame, show="*", font=("Arial", 14), width=25,  # Daha büyük
                                       bd=2, relief="flat", bg="#2c2c54", fg="white",
                                       insertbackground="white")
        self.password_entry.pack(fill="x", pady=(8, 0), ipady=8)  # Daha büyük

        # Göster/Gizle
        show_frame = tk.Frame(content_frame, bg="#1a1a40")
        show_frame.pack(fill="x", pady=10)
        self.show_password = tk.BooleanVar()
        tk.Checkbutton(show_frame, text="Şifreyi Göster", variable=self.show_password,
                       command=self.toggle_password, bg="#1a1a40", fg="#e9ecef",
                       selectcolor="#2c2c54", activebackground="#1a1a40",
                       activeforeground="#e9ecef", font=("Arial", 12)).pack(anchor="w")  # Daha büyük

        # Butonlar
        btn_frame = tk.Frame(content_frame, bg="#1a1a40")
        btn_frame.pack(fill="x", pady=(25, 15))

        tk.Button(btn_frame, text="🚀 Giriş Yap", command=self.login_user,
                  bg="#6a11cb", fg="white", font=("Arial", 14, "bold"),  # Daha büyük
                  width=20, height=2, bd=0, cursor="hand2",
                  activebackground="#8a2be2").pack(pady=8)

        tk.Button(btn_frame, text="⭐ Kayıt Ol", command=self.register_screen,
                  bg="#2575fc", fg="white", font=("Arial", 14, "bold"),  # Daha büyük
                  width=20, height=2, bd=0, cursor="hand2",
                  activebackground="#6a11cb").pack(pady=8)

        # Giriş bilgileri (test için)
        test_frame = tk.Frame(content_frame, bg="#1a1a40")
        test_frame.pack(fill="x", pady=(15, 0))
        tk.Label(test_frame, text="Test için: admin / admin", font=("Arial", 11),  # Daha büyük
                 bg="#1a1a40", fg="#adb5bd").pack()

    def toggle_password(self):
        if self.show_password.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    def login_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            self.show_message("Lütfen tüm alanları doldurun!", "#ff0000")
            return

        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        if user:
            self.current_user = username
            self.show_message(f"Hoşgeldiniz, {username}! 🎉", "#00ff00")
            self.root.after(2000, self.main_menu)  # 2 saniye sonra ana menüye geç
        else:
            self.show_message("Kullanıcı adı veya şifre yanlış! ❌", "#ff0000")

    # ------------------ KAYIT EKRANI ------------------
    def register_screen(self):
        self.clear_window()
        self.create_stars()

        panel = self.create_panel("🌟 Wawi & Luna'ya Katıl", 650, 550)

        # Geri düğmesi
        back_btn = tk.Button(panel, text="← Geri", command=self.login_screen,
                             bg="#1a1a40", fg="#adb5bd", font=("Arial", 12),
                             bd=0, activebackground="#2c2c54", activeforeground="white")
        back_btn.place(x=15, y=80)

        # Ana içerik çerçevesi
        content_frame = tk.Frame(panel, bg="#1a1a40")
        content_frame.pack(fill="both", expand=True, padx=40, pady=20)

        # Kullanıcı adı
        user_frame = tk.Frame(content_frame, bg="#1a1a40")
        user_frame.pack(fill="x", pady=12)

        tk.Label(user_frame, text="👤 Kullanıcı Adı", font=("Arial", 14, "bold"),
                 bg="#1a1a40", fg="#e9ecef", anchor="w").pack(fill="x")
        self.reg_username = tk.Entry(user_frame, font=("Arial", 14), width=25,
                                     bd=2, relief="flat", bg="#2c2c54", fg="white",
                                     insertbackground="white")
        self.reg_username.pack(fill="x", pady=(8, 0), ipady=8)

        # Şifre
        pass_frame = tk.Frame(content_frame, bg="#1a1a40")
        pass_frame.pack(fill="x", pady=12)

        tk.Label(pass_frame, text="🔒 Şifre", font=("Arial", 14, "bold"),
                 bg="#1a1a40", fg="#e9ecef", anchor="w").pack(fill="x")
        self.reg_password = tk.Entry(pass_frame, show="*", font=("Arial", 14), width=25,
                                     bd=2, relief="flat", bg="#2c2c54", fg="white",
                                     insertbackground="white")
        self.reg_password.pack(fill="x", pady=(8, 0), ipady=8)

        # Şifre tekrar
        confirm_frame = tk.Frame(content_frame, bg="#1a1a40")
        confirm_frame.pack(fill="x", pady=12)

        tk.Label(confirm_frame, text="🔁 Şifre Tekrar", font=("Arial", 14, "bold"),
                 bg="#1a1a40", fg="#e9ecef", anchor="w").pack(fill="x")
        self.reg_confirm = tk.Entry(confirm_frame, show="*", font=("Arial", 14), width=25,
                                    bd=2, relief="flat", bg="#2c2c54", fg="white",
                                    insertbackground="white")
        self.reg_confirm.pack(fill="x", pady=(8, 0), ipady=8)

        # Buton
        btn_frame = tk.Frame(content_frame, bg="#1a1a40")
        btn_frame.pack(fill="x", pady=(25, 15))

        tk.Button(btn_frame, text="🚀 Kayıt Ol", command=self.register_user,
                  bg="#2575fc", fg="white", font=("Arial", 14, "bold"),
                  width=20, height=2, bd=0, cursor="hand2",
                  activebackground="#6a11cb").pack(pady=8)

    def register_user(self):
        username = self.reg_username.get()
        password = self.reg_password.get()
        confirm = self.reg_confirm.get()

        if not username or not password:
            self.show_message("Lütfen tüm alanları doldurun! ❌", "#ff0000")
            return

        if password != confirm:
            self.show_message("Şifreler uyuşmuyor! ❌", "#ff0000")
            return

        # Önce kullanıcı adının var olup olmadığını kontrol et
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            self.show_message("Bu kullanıcı adı zaten alınmış! ❌", "#ff0000")
            return

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            self.show_message("Kayıt başarılı! ✅", "#00ff00")
            self.root.after(2000, self.login_screen)  # 2 saniye sonra giriş ekranına dön
        except sqlite3.IntegrityError:
            self.show_message("Bu kullanıcı adı zaten alınmış! ❌", "#ff0000")

    def main_menu(self):
        self.clear_window()
        self.create_stars()

        # Başlık
        title_label = tk.Label(self.canvas, text="🎮 Wawi & Luna Oyun Koleksiyonu",
                               font=("Arial", 32, "bold"), bg="#0f0c29", fg="white")
        title_label.place(relx=0.5, y=70, anchor="center")

        # Kullanıcı bilgisi
        user_label = tk.Label(self.canvas, text=f"👤 {self.current_user}",
                              font=("Arial", 14), bg="#0f0c29", fg="#adb5bd")
        user_label.place(x=25, y=25)

        # Oyun kartları çerçevesi
        games_frame = tk.Frame(self.canvas, bg="#0f0c29")
        games_frame.place(relx=0.5, rely=0.5, anchor="center", width=1200, height=400)

        # 4 OYUN - Sizin oyunlarınız
        games = [
            {"name": "Astro Wars", "color": "#6a11cb", "desc": "Uzaylılara karşı galaksiyi koru!"},
            {"name": "Uzay Kaçışı", "color": "#ff4b1f", "desc": "Tehlikelerden kaçarak uzayda yol al!"},
            {"name": "Balık Avı", "color": "#1cb5e0", "desc": "En lezzetli balıkları yakala!"},
            {"name": "Pembe Yılan Macerası", "color": "#ff369b", "desc": "Pembe yılanla macera dolu bir yolculuk!"}
        ]

        # Oyun kartlarını oluştur
        for i, game in enumerate(games):
            card = tk.Frame(games_frame, bg=game["color"], width=250, height=320,  # Kart yüksekliğini artırdım
                            relief="raised", bd=3)
            card.place(relx=0.125 + i * 0.25, rely=0.5, anchor="center")

            # Kart içeriği
            content = tk.Frame(card, bg=game["color"], width=230, height=300)  # İçerik yüksekliğini artırdım
            content.place(relx=0.5, rely=0.5, anchor="center")
            content.pack_propagate(False)

            # Oyun ikonu - DAHA BÜYÜK
            if isinstance(self.game_icons[game["name"]], str):
                # Eğer ikon yüklenememişse emoji kullan
                icon_label = tk.Label(content, text=self.game_icons[game["name"]],
                                      font=("Arial", 50), bg=game["color"], fg="white")  # Emoji boyutunu artırdım
            else:
                # İkon yüklenmişse görüntüyü kullan
                icon_label = tk.Label(content, image=self.game_icons[game["name"]],
                                      bg=game["color"])
            icon_label.pack(pady=(20, 10))

            # Oyun adı
            name_label = tk.Label(content, text=game["name"], font=("Arial", 16, "bold"),
                                  bg=game["color"], fg="white")
            name_label.pack(pady=(0, 8))

            # Açıklama
            desc_label = tk.Label(content, text=game["desc"], font=("Arial", 10),
                                  bg=game["color"], fg="white", wraplength=200)
            desc_label.pack(pady=8)

            # Oyna butonu
            play_btn = tk.Button(content, text="OYNA",
                                 font=("Arial", 12, "bold"),
                                 bg="white", fg=game["color"],
                                 bd=0, cursor="hand2",
                                 command=lambda g=game["name"]: self.launch_game(g))
            play_btn.pack(pady=12, ipadx=15, ipady=5)

            # Hover efekti
            def on_enter(e, c=card):
                c.config(relief="sunken")

            def on_leave(e, c=card):
                c.config(relief="raised")

            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)

        # Çıkış butonu
        exit_btn = tk.Button(self.canvas, text="Çıkış Yap", command=self.login_screen,
                             bg="#e52d27", fg="white", font=("Arial", 14, "bold"),
                             width=15, height=1, bd=0, cursor="hand2",
                             activebackground="#b31217")
        exit_btn.place(relx=0.5, y=750, anchor="center")

    def launch_game(self, game_name):
        """Oyunu başlat"""
        self.show_message(f"{game_name} başlatılıyor... 🚀", "#00ff00")

        # Oyun isimlerini klasörlerle eşleştiriyoruz
        oyun_haritasi = {
            "Astro Wars": ("astro wars", "astro_wars_code.py"),
            "Uzay Kaçışı": ("Uzay Kaçışı", "game.py"),
            "Balık Avı": ("balık avı", "balikAvi.py"),
            "Pembe Yılan Macerası": ("pembe yilan macerasi", "snake_game.py")
        }

        # Seçilen oyunun klasör ve dosya adını bul
        oyun_bilgisi = oyun_haritasi.get(game_name)
        if not oyun_bilgisi:
            self.show_message("Bilinmeyen oyun!", "#ff0000")
            return

        klasor_adi, dosya_adi = oyun_bilgisi

        # Oyun dosyasının tam yolu
        oyun_yolu = os.path.join("oyunlar", klasor_adi, dosya_adi)

        # Oyun dosyası varsa subprocess ile başlat
        if os.path.exists(oyun_yolu):
            try:
                subprocess.Popen(["python", oyun_yolu])
                self.show_message(f"{game_name} başlatıldı! 🚀", "#00ff00")
            except Exception as e:
                self.show_message(f"Oyun başlatılamadı: {e}", "#ff0000")
        else:
            self.show_message("Oyun dosyası bulunamadı!", "#ff0000")

    # ------------------ YARDIMCI ------------------
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.canvas = tk.Canvas(self.root, width=1400, height=900,
                                bg="#0f0c29", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.message_label = None


# ------------------ ÇALIŞTIR ------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = GamePlatformApp(root)
    root.mainloop()