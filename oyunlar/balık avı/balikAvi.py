import pygame
import random
import sqlite3
import time

# pygame hazırlık
pygame.init()

# pencere ayarları
GENISLIK, YUKSEKLIK = 750, 750
ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK))

# fps ayarları
FPS = 30
saat = pygame.time.Clock()


# Veritabanı bağlantısı
def veritabani_baglanti():
    conn = sqlite3.connect('oyun_skorlari.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS skorlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skor INTEGER,
        sure INTEGER,
        tarih TEXT
    )
    ''')
    conn.commit()
    return conn, cursor


def skor_kaydet(conn, cursor, sure):
    tarih = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO skorlar (skor, sure, tarih) VALUES (?, ?, ?)",
                   (sure, sure, tarih))
    conn.commit()


def en_yuksek_skor(cursor):
    cursor.execute("SELECT MAX(skor) FROM skorlar")
    return cursor.fetchone()[0] or 0


# sınıflar
class Oyun():
    def __init__(self, kopekbaligi, balik_grup):
        # nesneler
        self.kopekbaligi = kopekbaligi
        self.balik_grup = balik_grup
        # oyun degiskenleri
        self.sure = 0
        self.fps_degeri_sayma = 0
        self.bolumNo = 0
        self.oyun_bitti = False

        # Veritabanı bağlantısı
        self.conn, self.cursor = veritabani_baglanti()

        # baliklar
        balik1 = pygame.image.load("balik1.png").convert_alpha()
        balik1 = pygame.transform.scale(balik1, (40, 40))

        balik2 = pygame.image.load("balik2.png").convert_alpha()
        balik2 = pygame.transform.scale(balik2, (40, 40))

        balik3 = pygame.image.load("balik3.png").convert_alpha()
        balik3 = pygame.transform.scale(balik3, (40, 40))

        balik4 = pygame.image.load("balik4.png").convert_alpha()
        balik4 = pygame.transform.scale(balik4, (40, 40))
        self.balik_liste = [balik1, balik2, balik3, balik4]
        self.balik_liste_indexNo = random.randint(0, 3)
        self.hedef_balikGoruntu = self.balik_liste[self.balik_liste_indexNo]
        self.hedef_balikKonum = self.hedef_balikGoruntu.get_rect()
        self.hedef_balikKonum.top = 40
        self.hedef_balikKonum.centerx = GENISLIK // 2
        # font
        self.oyun_font = pygame.font.Font("oyun_font.ttf", 40)
        self.buyuk_font = pygame.font.Font("oyun_font.ttf", 60)
        self.kucuk_font = pygame.font.Font("oyun_font.ttf", 30)
        # oyun sesleri ve sarki
        self.balik_yeme = pygame.mixer.Sound("yeme_efekt.wav")
        self.yenme_sesi = pygame.mixer.Sound("olu.wav")
        pygame.mixer.music.load("sarki.wav")
        pygame.mixer.music.play(-1)
        # arkaplan
        self.oyun_arka_plan = pygame.image.load("arkaplan.jpg")

    def update(self):
        if self.oyun_bitti:
            return

        self.fps_degeri_sayma += 1
        if self.fps_degeri_sayma == FPS:
            self.sure += 1
            print(self.sure)
            self.fps_degeri_sayma = 0
        self.temas()

    def ciz(self):
        ekran.blit(self.oyun_arka_plan, (0, 0))

        metin1 = self.oyun_font.render("Süre: " + str(self.sure), True, (255, 255, 255), (0, 0, 170))
        metin1_konum = metin1.get_rect()
        metin1_konum.top = 30
        metin1_konum.left = 30

        metin2 = self.oyun_font.render("can: " + str(self.kopekbaligi.can), True, (255, 255, 255), (0, 0, 170))
        metin2_konum = metin2.get_rect()
        metin2_konum.top = 30
        metin2_konum.right = GENISLIK - 50

        ekran.blit(metin1, metin1_konum)
        ekran.blit(metin2, metin2_konum)
        ekran.blit(self.hedef_balikGoruntu, self.hedef_balikKonum)

        pygame.draw.rect(ekran, (255, 255, 255), (350, 30, 50, 50), 5)
        pygame.draw.rect(ekran, (255, 0, 255), (0, 100, 750, YUKSEKLIK - 150), 5)

        # Oyun bittiyse oyun bitiş ekranını EN SON çiz (şeffaf olarak)
        if self.oyun_bitti:
            self.oyun_bitis_ekrani()

    def temas(self):
        if self.oyun_bitti:
            return

        temas_olduMu = pygame.sprite.spritecollideany(self.kopekbaligi, self.balik_grup)
        if temas_olduMu:
            if temas_olduMu.tip == self.balik_liste_indexNo:
                temas_olduMu.remove(self.balik_grup)
                self.balik_yeme.play()
                if self.balik_grup:
                    self.hedef_degistir()
                else:
                    self.degistir()
            else:
                self.kopekbaligi.can -= 1
                self.yenme_sesi.play()
                self.guvenliAlan()
                if self.kopekbaligi.can <= 0:
                    self.dur()

    def dur(self):
        self.oyun_bitti = True
        skor_kaydet(self.conn, self.cursor, self.sure)
        self.en_yuksek_skor = en_yuksek_skor(self.cursor)

    def oyun_bitis_ekrani(self):
        # ŞEFFAF arkaplan - balıkların ve diğer öğelerin üstüne çıkacak
        karanlik_yuzey = pygame.Surface((GENISLIK, YUKSEKLIK), pygame.SRCALPHA)
        karanlik_yuzey.fill((0, 0, 0, 150))  # Daha şeffaf (150 alpha)
        ekran.blit(karanlik_yuzey, (0, 0))

        # Oyun bitti metni
        oyun_bitti_metin = self.buyuk_font.render("OYUN BİTTİ", True, (255, 0, 0))
        oyun_bitti_konum = oyun_bitti_metin.get_rect()
        oyun_bitti_konum.center = (GENISLIK // 2, YUKSEKLIK // 2 - 100)
        ekran.blit(oyun_bitti_metin, oyun_bitti_konum)

        # Skor bilgileri
        skor_metin = self.oyun_font.render(f"Skorunuz: {self.sure}", True, (255, 255, 255))
        skor_konum = skor_metin.get_rect()
        skor_konum.center = (GENISLIK // 2, YUKSEKLIK // 2 - 30)
        ekran.blit(skor_metin, skor_konum)

        sure_metin = self.oyun_font.render(f"Süre: {self.sure} saniye", True, (255, 255, 255))
        sure_konum = sure_metin.get_rect()
        sure_konum.center = (GENISLIK // 2, YUKSEKLIK // 2 + 20)
        ekran.blit(sure_metin, sure_konum)

        en_yuksek_metin = self.oyun_font.render(f"En Yüksek Skor: {self.en_yuksek_skor}", True, (255, 255, 0))
        en_yuksek_konum = en_yuksek_metin.get_rect()
        en_yuksek_konum.center = (GENISLIK // 2, YUKSEKLIK // 2 + 70)
        ekran.blit(en_yuksek_metin, en_yuksek_konum)

        # Yeniden başlatma seçenekleri
        yeniden_metin = self.kucuk_font.render("Yeniden Başlatmak için R tuşuna basın", True, (0, 255, 0))
        yeniden_konum = yeniden_metin.get_rect()
        yeniden_konum.center = (GENISLIK // 2, YUKSEKLIK // 2 + 140)
        ekran.blit(yeniden_metin, yeniden_konum)

        cikis_metin = self.kucuk_font.render("Çıkmak için ESC tuşuna basın", True, (255, 100, 100))
        cikis_konum = cikis_metin.get_rect()
        cikis_konum.center = (GENISLIK // 2, YUKSEKLIK // 2 + 180)
        ekran.blit(cikis_metin, cikis_konum)

    def reset(self):
        self.kopekbaligi.can = 3
        self.sure = 0
        self.fps_degeri_sayma = 0
        self.bolumNo = 0
        self.oyun_bitti = False
        self.degistir()
        self.guvenliAlan()

    def guvenliAlan(self):
        self.kopekbaligi.rect.top = YUKSEKLIK - 40

    def hedef_degistir(self):
        hedef_balik = random.choice(self.balik_grup.sprites())
        self.hedef_balikGoruntu = hedef_balik.image
        self.balik_liste_indexNo = hedef_balik.tip

    def degistir(self):
        self.bolumNo += 1
        for balik in self.balik_grup:
            self.balik_grup.remove(balik)
        for x in range(self.bolumNo):
            self.balik_grup.add(
                Balik(random.randint(0, GENISLIK - 32), random.randint(105, YUKSEKLIK - 150), self.balik_liste[0], 0))
            self.balik_grup.add(
                Balik(random.randint(0, GENISLIK - 32), random.randint(105, YUKSEKLIK - 150), self.balik_liste[1], 1))
            self.balik_grup.add(
                Balik(random.randint(0, GENISLIK - 32), random.randint(105, YUKSEKLIK - 150), self.balik_liste[2], 2))
            self.balik_grup.add(
                Balik(random.randint(0, GENISLIK - 32), random.randint(105, YUKSEKLIK - 150), self.balik_liste[3], 3))


class Balik(pygame.sprite.Sprite):
    def __init__(self, x, y, resim, tip):
        super().__init__()
        self.image = resim
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.tip = tip
        self.hiz = random.randint(1, 5)
        self.yonx = random.choice([-1, 1])
        self.yony = random.choice([-1, 1])

    def update(self):
        self.rect.x += self.hiz * self.yonx
        self.rect.y += self.hiz * self.yony
        if self.rect.left <= 0 or self.rect.right >= GENISLIK:
            self.yonx *= -1
        if self.rect.top <= 100 or self.rect.bottom >= YUKSEKLIK - 50:
            self.yony *= -1


class KopekBaligi(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.orjinal_resim = pygame.image.load("kopek_baligi.png").convert_alpha()
        self.image = pygame.transform.scale(self.orjinal_resim, (60, 60))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.can = 3
        self.hiz = 13

    def update(self):
        self.hareket()

    def hareket(self):
        tus = pygame.key.get_pressed()
        if tus[pygame.K_LEFT]:
            self.rect.x -= self.hiz
        elif tus[pygame.K_RIGHT]:
            self.rect.x += self.hiz
        elif tus[pygame.K_UP]:
            self.rect.y -= self.hiz
        elif tus[pygame.K_DOWN]:
            self.rect.y += self.hiz


# köpek balığı grup işlemler
kopek_baligiGrup = pygame.sprite.Group()
kopekbaligi = KopekBaligi(GENISLIK // 2, YUKSEKLIK // 2)
kopek_baligiGrup.add(kopekbaligi)

# balık grup
balik_grup = pygame.sprite.Group()

# oyun sınıfı
oyun = Oyun(kopekbaligi, balik_grup)
oyun.degistir()

# oyun döngüsü
durum = True
while durum:
    for etkinlik in pygame.event.get():
        if etkinlik.type == pygame.QUIT:
            durum = False
        elif etkinlik.type == pygame.KEYDOWN:
            if oyun.oyun_bitti:
                if etkinlik.key == pygame.K_r:  # R tuşu ile yeniden başlat
                    oyun.reset()
                elif etkinlik.key == pygame.K_ESCAPE:  # ESC tuşu ile çıkış
                    durum = False

    ekran.fill((0, 0, 0))
    # oyun mekanigi
    oyun.update()
    oyun.ciz()

    # kopekbaligi cizme ve guncelleme
    if not oyun.oyun_bitti:
        kopek_baligiGrup.update()
    kopek_baligiGrup.draw(ekran)

    # baliktest
    if not oyun.oyun_bitti:
        balik_grup.update()
    balik_grup.draw(ekran)

    pygame.display.update()
    saat.tick(FPS)

# Veritabanı bağlantısını kapat
oyun.conn.close()
pygame.quit()