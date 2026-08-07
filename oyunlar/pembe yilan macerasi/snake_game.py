import pygame
import random
import time
import sqlite3
import os

# Pygame'i başlat
pygame.init()

# Renkleri tanımla
BEYAZ = (255, 255, 255)
SIYAH = (0, 0, 0)
PEMBE = (255, 182, 193)
KOYU_PEMBE = (255, 105, 180)
KIRMIZI = (255, 0, 0)
MOR = (128, 0, 128)
ACIK_PEMBE = (255, 223, 227)  # Çok açık pembe arkaplan
YESIL_1 = (102, 205, 102)  # Daha koyu yeşil tonu 1
YESIL_2 = (96, 180, 96)  # Daha koyu yeşil tonu 2
TRANSPARAN = (0, 0, 0, 128)  # Tam transparan

# Oyun penceresi boyutları
genislik, yukseklik = 800, 600
ekran = pygame.display.set_mode((genislik, yukseklik))
pygame.display.set_caption("Yılan Oyunu")

# Oyun hızını kontrol eden saat nesnesi
saat = pygame.time.Clock()

# Yılan ve yiyecek boyutu
blok_boyutu = 20

# Oyun içi font stili
font_stili = pygame.font.SysFont("arial", 35)
buyuk_font = pygame.font.SysFont("arial", 50)


# Veritabanı bağlantısını oluştur
def veritabani_baglantisi():
    conn = sqlite3.connect('snake_scores.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scores
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 score INTEGER NOT NULL,
                 date TEXT NOT NULL)''')
    conn.commit()
    return conn


# Skoru veritabanına kaydet
def skor_kaydet(conn, skor):
    c = conn.cursor()
    tarih = time.strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO scores (score, date) VALUES (?, ?)", (skor, tarih))
    conn.commit()


# En yüksek skoru getir
def en_yuksek_skor(conn):
    c = conn.cursor()
    c.execute("SELECT MAX(score) FROM scores")
    result = c.fetchone()
    return result[0] if result[0] is not None else 0


def skor_goster(skor):
    """Ekranda skor tablosunu gösterir."""
    yazi = font_stili.render("Skor: " + str(skor), True, SIYAH)
    ekran.blit(yazi, [10, 10])


def cicek_ciz(x, y, tur):
    """Belirtilen konuma küçük bir çiçek çizer."""
    if tur == 0:  # Beyaz papatya
        # Çiçek merkezi
        pygame.draw.circle(ekran, (255, 255, 0), (x, y), 3)
        # Çiçek yaprakları
        pygame.draw.circle(ekran, (255, 255, 255), (x - 5, y), 4)
        pygame.draw.circle(ekran, (255, 255, 255), (x + 5, y), 4)
        pygame.draw.circle(ekran, (255, 255, 255), (x, y - 5), 4)
        pygame.draw.circle(ekran, (255, 255, 255), (x, y + 5), 4)
    elif tur == 1:  # Kırmızı gelincik
        pygame.draw.circle(ekran, (255, 0, 0), (x, y), 5)
        pygame.draw.circle(ekran, (0, 0, 0), (x, y), 2)
    elif tur == 2:  # Mor menekşe
        pygame.draw.circle(ekran, (138, 43, 226), (x, y), 4)
        pygame.draw.circle(ekran, (75, 0, 130), (x, y), 2)
    elif tur == 3:  # Pembe karanfil
        pygame.draw.circle(ekran, (255, 182, 193), (x, y), 4)
        pygame.draw.circle(ekran, (219, 112, 147), (x, y), 2)
    elif tur == 4:  # Kırmızı lale
        pygame.draw.rect(ekran, (255, 0, 0), [x - 3, y - 8, 6, 8])
        pygame.draw.ellipse(ekran, (255, 0, 0), [x - 5, y - 10, 10, 6])
    elif tur == 5:  # Beyaz zambak
        pygame.draw.rect(ekran, (0, 150, 0), [x - 2, y - 5, 4, 5])  # Sap
        # Yapraklar
        pygame.draw.ellipse(ekran, (255, 255, 255), [x - 8, y - 8, 6, 10])
        pygame.draw.ellipse(ekran, (255, 255, 255), [x + 2, y - 8, 6, 10])
        pygame.draw.ellipse(ekran, (255, 255, 255), [x - 3, y - 12, 6, 8])
        # Orta kısım
        pygame.draw.circle(ekran, (255, 255, 0), (x, y - 5), 2)


def arkaplan_ciz():
    """Çok açık pembe arkaplan ve iki yakın yeşil tonunda çimler çizer."""
    # Çok açık pembe arkaplan
    ekran.fill(ACIK_PEMBE)

    # İki yakın yeşil tonunda kareler (çim efekti) - çizgiler yok
    kare_boyutu = 20
    for i in range(0, genislik, kare_boyutu):
        for j in range(0, yukseklik, kare_boyutu):
            # İki yakın yeşil tonunu şık şekilde dağıt
            if (i // kare_boyutu + j // kare_boyutu) % 2 == 0:
                pygame.draw.rect(ekran, YESIL_1, [i, j, kare_boyutu, kare_boyutu])
            else:
                pygame.draw.rect(ekran, YESIL_2, [i, j, kare_boyutu, kare_boyutu])

    # Sabit çiçek konumları
    cicek_konumlari = [
        (100, 100, 0), (200, 150, 1), (300, 200, 2), (400, 250, 3),
        (500, 300, 4), (600, 350, 5), (700, 100, 0), (150, 400, 1),
        (250, 450, 2), (350, 500, 3), (450, 550, 4), (550, 200, 5),
        (650, 250, 0), (750, 300, 1), (50, 350, 2), (180, 180, 3),
        (280, 280, 4), (380, 380, 5), (480, 480, 0), (580, 100, 1)
    ]

    for x, y, tur in cicek_konumlari:
        cicek_ciz(x, y, tur)


def yilan_ciz(yilan_listesi, x_degisim, y_degisim):
    """Yılanı ve gözlerini çizer."""
    if not yilan_listesi:
        return

    # Yılanın başını çiz
    pygame.draw.rect(ekran, KOYU_PEMBE, [yilan_listesi[-1][0], yilan_listesi[-1][1], blok_boyutu, blok_boyutu])

    # Göz pozisyonlarını yılanın yönüne göre belirle
    goz_boyutu = 3
    if x_degisim > 0:  # Sağ
        goz_1_konum = (yilan_listesi[-1][0] + blok_boyutu * 0.75, yilan_listesi[-1][1] + blok_boyutu * 0.25)
        goz_2_konum = (yilan_listesi[-1][0] + blok_boyutu * 0.75, yilan_listesi[-1][1] + blok_boyutu * 0.75)
    elif x_degisim < 0:  # Sol
        goz_1_konum = (yilan_listesi[-1][0] + blok_boyutu * 0.25, yilan_listesi[-1][1] + blok_boyutu * 0.25)
        goz_2_konum = (yilan_listesi[-1][0] + blok_boyutu * 0.25, yilan_listesi[-1][1] + blok_boyutu * 0.75)
    elif y_degisim > 0:  # Aşağı
        goz_1_konum = (yilan_listesi[-1][0] + blok_boyutu * 0.25, yilan_listesi[-1][1] + blok_boyutu * 0.75)
        goz_2_konum = (yilan_listesi[-1][0] + blok_boyutu * 0.75, yilan_listesi[-1][1] + blok_boyutu * 0.75)
    else:  # Yukarı (veya başlangıç)
        goz_1_konum = (yilan_listesi[-1][0] + blok_boyutu * 0.25, yilan_listesi[-1][1] + blok_boyutu * 0.25)
        goz_2_konum = (yilan_listesi[-1][0] + blok_boyutu * 0.75, yilan_listesi[-1][1] + blok_boyutu * 0.25)

    pygame.draw.circle(ekran, SIYAH, goz_1_konum, goz_boyutu)
    pygame.draw.circle(ekran, SIYAH, goz_2_konum, goz_boyutu)

    # Yılanın geri kalanını çiz
    for parca in yilan_listesi[:-1]:
        pygame.draw.rect(ekran, PEMBE, [parca[0], parca[1], blok_boyutu, blok_boyutu])


def oyun_sonu_ekrani(skor, en_yuksek_skor):
    """Oyun sonu ekranını gösterir."""
    # Tam transparan bir katman oluştur
    saydam_katman = pygame.Surface((genislik, yukseklik), pygame.SRCALPHA)
    saydam_katman.fill(TRANSPARAN)  # Tam transparan
    ekran.blit(saydam_katman, (0, 0))

    # Oyun bitti mesajı
    oyun_bitti_yazi = buyuk_font.render("OYUN BİTTİ", True, BEYAZ)
    ekran.blit(oyun_bitti_yazi, (genislik / 2 - oyun_bitti_yazi.get_width() / 2, yukseklik / 2 - 80))

    # Skor bilgisi
    skor_yazi = font_stili.render(f"Skorunuz: {skor}", True, BEYAZ)
    ekran.blit(skor_yazi, (genislik / 2 - skor_yazi.get_width() / 2, yukseklik / 2 - 20))

    # En yüksek skor bilgisi
    en_yuksek_yazi = font_stili.render(f"En Yüksek Skor: {en_yuksek_skor}", True, BEYAZ)
    ekran.blit(en_yuksek_yazi, (genislik / 2 - en_yuksek_yazi.get_width() / 2, yukseklik / 2 + 20))

    # Yeniden başlatma mesajı
    yeniden_baslat_yazi = font_stili.render("Yeniden Başlatmak için C, Çıkmak için Q", True, BEYAZ)
    ekran.blit(yeniden_baslat_yazi, (genislik / 2 - yeniden_baslat_yazi.get_width() / 2, yukseklik / 2 + 80))


def oyun_dongusu():
    """Oyunun ana döngüsünü çalıştırır."""
    # Veritabanı bağlantısını oluştur
    conn = veritabani_baglantisi()
    en_yuksek = en_yuksek_skor(conn)

    oyun_devam = True
    oyun_bitti = False

    # Yılanın başlangıç konumu ve uzunluğu
    x_baslangic = genislik / 2
    y_baslangic = yukseklik / 2
    x_degisim = 0
    y_degisim = 0

    yilan_listesi = []
    yilan_uzunlugu = 1

    def rastgele_konum_sec():
        """Yiyeceklerin rastgele konumunu belirler."""
        x = round(random.randrange(0, genislik - blok_boyutu) / blok_boyutu) * blok_boyutu
        y = round(random.randrange(0, yukseklik - blok_boyutu) / blok_boyutu) * blok_boyutu
        return x, y

    kirmizi_elma_konum = rastgele_konum_sec()
    mor_elma_konum = None
    siyah_elma_konum = None
    skor = 0

    while oyun_devam:
        while oyun_bitti:
            oyun_sonu_ekrani(skor, en_yuksek)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    oyun_devam = False
                    oyun_bitti = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        oyun_devam = False
                        oyun_bitti = False
                    if event.key == pygame.K_c:
                        # Mevcut bağlantıyı kapat ve yeni oyun başlat
                        conn.close()
                        oyun_dongusu()
                        return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                oyun_devam = False
            if event.type == pygame.KEYDOWN:
                # Hareket yönünün tersine gidişi engelle
                if event.key == pygame.K_LEFT and x_degisim == 0:
                    x_degisim = -blok_boyutu
                    y_degisim = 0
                elif event.key == pygame.K_RIGHT and x_degisim == 0:
                    x_degisim = blok_boyutu
                    y_degisim = 0
                elif event.key == pygame.K_UP and y_degisim == 0:
                    y_degisim = -blok_boyutu
                    x_degisim = 0
                elif event.key == pygame.K_DOWN and y_degisim == 0:
                    y_degisim = blok_boyutu
                    x_degisim = 0

        # Yılanın konumunu güncelle
        x_baslangic += x_degisim
        y_baslangic += y_degisim

        # Duvarlara çarpma kontrolü
        if x_baslangic >= genislik or x_baslangic < 0 or y_baslangic >= yukseklik or y_baslangic < 0:
            skor_kaydet(conn, skor)
            en_yuksek = en_yuksek_skor(conn)
            oyun_bitti = True

        yeni_yilan_basi = [x_baslangic, y_baslangic]
        yilan_listesi.append(yeni_yilan_basi)

        # Yılanın kendisine çarpma kontrolü, sadece 2 veya daha fazla parçadan oluştuğunda kontrol et
        if yilan_uzunlugu > 1:
            for parca in yilan_listesi[:-1]:
                if parca == yeni_yilan_basi:
                    skor_kaydet(conn, skor)
                    en_yuksek = en_yuksek_skor(conn)
                    oyun_bitti = True

        if len(yilan_listesi) > yilan_uzunlugu:
            del yilan_listesi[0]

        arkaplan_ciz()

        # Elma çizimleri
        pygame.draw.rect(ekran, KIRMIZI, [kirmizi_elma_konum[0], kirmizi_elma_konum[1], blok_boyutu, blok_boyutu])
        if mor_elma_konum:
            pygame.draw.rect(ekran, MOR, [mor_elma_konum[0], mor_elma_konum[1], blok_boyutu, blok_boyutu])
        if siyah_elma_konum:
            pygame.draw.rect(ekran, SIYAH, [siyah_elma_konum[0], siyah_elma_konum[1], blok_boyutu, blok_boyutu])

        yilan_ciz(yilan_listesi, x_degisim, y_degisim)
        skor_goster(skor)

        pygame.display.update()

        # Yiyecekleri yeme kontrolü
        if x_baslangic == kirmizi_elma_konum[0] and y_baslangic == kirmizi_elma_konum[1]:
            kirmizi_elma_konum = rastgele_konum_sec()
            skor += 2
            yilan_uzunlugu += 1

            # Mor elma nadiren ortaya çıksın (örneğin 10'da bir)
            if random.randint(1, 10) == 1:
                mor_elma_konum = rastgele_konum_sec()

            # Siyah elma çok nadiren ortaya çıksın (örneğin 20'de bir)
            if random.randint(1, 20) == 1:
                siyah_elma_konum = rastgele_konum_sec()

        if mor_elma_konum and x_baslangic == mor_elma_konum[0] and y_baslangic == mor_elma_konum[1]:
            skor += 5
            yilan_uzunlugu += 1
            mor_elma_konum = None

        if siyah_elma_konum and x_baslangic == siyah_elma_konum[0] and y_baslangic == siyah_elma_konum[1]:
            skor -= 6
            if yilan_uzunlugu > 1:
                yilan_uzunlugu -= 1
            siyah_elma_konum = None

        saat.tick(15)  # Oyun hızı (saniyede 15 kare)

    conn.close()
    pygame.quit()
    quit()


oyun_dongusu()