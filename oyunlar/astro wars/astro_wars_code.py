import pygame
import random
import sqlite3
import datetime

# SQL veritabanı bağlantısı
def init_database():
    conn = sqlite3.connect("uzay_savasi.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS skorlar
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      skor INTEGER,
                      tarih TEXT)''')
    conn.commit()
    conn.close()

def skor_kaydet(skor):
    conn = sqlite3.connect("uzay_savasi.db")
    cursor = conn.cursor()
    tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO skorlar (skor, tarih) VALUES (?, ?)", (skor, tarih))
    conn.commit()
    conn.close()

def en_yuksek_skor():
    conn = sqlite3.connect("uzay_savasi.db")
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(skor) FROM skorlar")
    max_skor = cursor.fetchone()[0]
    conn.close()
    return max_skor if max_skor else 0

# Veritabanını başlat
init_database()

# pygame hazırlık
pygame.init()

# EKRAN
GENISLIK, YUKSEKLIK = 1250, 750
ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK))

# FPS
FPS = 60
saat = pygame.time.Clock()

# -------------------------------------------------------
# CLASSLAR

class Player(pygame.sprite.Sprite):
    def __init__(self, player_mermi_grup):
        super().__init__()
        self.image = pygame.image.load("uzay_gemi.png")
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.rect = self.image.get_rect()
        self.player_mermi_grup = player_mermi_grup
        self.rect.centerx = GENISLIK // 2
        self.rect.top = YUKSEKLIK - 70
        self.hiz = 13
        self.can = 5
        self.mermi_sesi = pygame.mixer.Sound("oyuncu_mermi.wav")

    def update(self):
        tus = pygame.key.get_pressed()
        if tus[pygame.K_LEFT] and self.rect.left >= 0:
            self.rect.x -= self.hiz
        if tus[pygame.K_RIGHT] and self.rect.right <= GENISLIK:
            self.rect.x += self.hiz

    def saldiri(self):
        if len(self.player_mermi_grup) < 2:
            self.mermi_sesi.play()
            Player_mermi(self.rect.centerx, self.rect.top, self.player_mermi_grup)

    def reset(self):
        self.rect.centerx = GENISLIK // 2

class Uzayli(pygame.sprite.Sprite):
    def __init__(self, x, y, hiz, mermi_grup):
        super().__init__()
        self.image = pygame.image.load("uzayli.png")
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.basx = x
        self.basy = y
        self.yon = 1
        self.hiz = hiz
        self.mermi_grup = mermi_grup
        self.uzayli_mermi_sesi = pygame.mixer.Sound("uzayli_mermi.wav")

    def update(self):
        self.rect.x += self.yon * self.hiz
        if random.randint(0, 100) > 99 and len(self.mermi_grup) < 3:
            self.uzayli_mermi_sesi.play()
            self.saldiri()

    def saldiri(self):
        Uzayli_mermi(self.rect.centerx, self.rect.bottom, self.mermi_grup)

    def reset(self):
        self.rect.topleft = (self.basx, self.basy)
        self.yon = 1

class Player_mermi(pygame.sprite.Sprite):
    def __init__(self, x, y, player_mermi_grup):
        super().__init__()
        self.image = pygame.image.load("oyuncu_mermi.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.hiz = 13
        player_mermi_grup.add(self)

    def update(self):
        self.rect.y -= self.hiz
        if self.rect.bottom < 0:
            self.kill()

class Uzayli_mermi(pygame.sprite.Sprite):
    def __init__(self, x, y, mermi_grup):
        super().__init__()
        self.image = pygame.image.load("uzayli_mermi.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.hiz = 13
        mermi_grup.add(self)

    def update(self):
        self.rect.y += self.hiz
        if self.rect.top > YUKSEKLIK:
            self.kill()

# -------------------------------------------------------
# OYUN SINIFI

class Oyun():
    def __init__(self, oyuncu, uzayli_grup, player_mermi_grup, uzayli_mermi_grup):
        self.bolum_no = 1
        self.puan = 0
        self.oyuncu = oyuncu
        self.uzayli_grup = uzayli_grup
        self.player_mermi_grup = player_mermi_grup
        self.uzayli_mermi_grup = uzayli_mermi_grup
        self.arka_plan1 = pygame.image.load("arka_plan1.jpg")
        self.arka_plan2 = pygame.image.load("arka_plan2.png")
        self.arka_plan3 = pygame.image.load("arka_plan3.png")
        self.tebrikler = pygame.image.load("tebrikler.png")
        self.uzayli_vurus = pygame.mixer.Sound("uzayli_vurus.wav")
        self.oyuncu_vurus = pygame.mixer.Sound("oyuncu_vurus.wav")
        pygame.mixer.music.load("arka_plan_sarki.wav")
        pygame.mixer.music.play(-1)
        self.oyun_font = pygame.font.Font("oyun_font.ttf", 64)
        self.kucuk_font = pygame.font.Font("oyun_font.ttf", 32)

    def update(self):
        self.uzayli_hareket()
        self.temas()
        self.oyun_tamamlandi()

    def ciz(self):
        puan_yazi = self.oyun_font.render("Skor: " + str(self.puan), True, (255, 255, 255), (0, 0, 0))
        puan_yazi_konum = puan_yazi.get_rect()
        puan_yazi_konum.topleft = (10, 10)
        bolum_no_yazi = self.oyun_font.render("Bölüm:" + str(self.bolum_no), True, (255, 255, 255), (0, 0, 0))
        bolum_no_yazi_konum = bolum_no_yazi.get_rect()
        bolum_no_yazi_konum.topleft = (GENISLIK - 250, 10)

        if self.bolum_no == 1:
            ekran.blit(self.arka_plan1, (0, 0))
        elif self.bolum_no == 2:
            ekran.blit(self.arka_plan2, (0, 0))
        elif self.bolum_no == 3:
            ekran.blit(self.arka_plan3, (0, 0))
        elif self.bolum_no == 4:
            self.oyunu_bitir()

        ekran.blit(puan_yazi, puan_yazi_konum)
        ekran.blit(bolum_no_yazi, bolum_no_yazi_konum)

    def uzayli_hareket(self):
        hareket, carpisma = False, False
        for uzayli in self.uzayli_grup.sprites():
            if uzayli.rect.left <= 0 or uzayli.rect.right >= GENISLIK:
                hareket = True
        if hareket:
            for uzayli in self.uzayli_grup.sprites():
                uzayli.rect.y += 10 * self.bolum_no
                uzayli.yon *= -1
                if uzayli.rect.bottom >= YUKSEKLIK - 70:
                    carpisma = True
        if carpisma:
            self.oyuncu.can -= 1
            self.oyun_durumu()

    def temas(self):
        if pygame.sprite.groupcollide(self.player_mermi_grup, self.uzayli_grup, True, True):
            self.oyuncu_vurus.play()
            self.puan += 100 * self.bolum_no
        if pygame.sprite.spritecollide(self.oyuncu, self.uzayli_mermi_grup, True):
            self.uzayli_vurus.play()
            self.oyuncu.can -= 1
            self.oyun_durumu()

    def bolum(self):
        for i in range(10):
            for j in range(5):
                uzayli = Uzayli(64 + i * 64, 100 + j * 64, self.bolum_no, self.uzayli_mermi_grup)
                self.uzayli_grup.add(uzayli)

    def oyun_durumu(self):
        self.uzayli_mermi_grup.empty()
        self.player_mermi_grup.empty()
        self.oyuncu.reset()
        for uzayli in self.uzayli_grup.sprites():
            uzayli.reset()
        if self.oyuncu.can == 0:
            skor_kaydet(self.puan)
            self.oyun_bitti_ekrani()
        else:
            self.oyunu_durdur()

    def oyun_bitti_ekrani(self):
        oyun_bitti = True
        global status

        karanlik_yuzey = pygame.Surface((GENISLIK, YUKSEKLIK), pygame.SRCALPHA)
        karanlik_yuzey.fill((0, 0, 0, 180))
        ekran.blit(karanlik_yuzey, (0, 0))
        en_yuksek = en_yuksek_skor()

        yazi1 = self.oyun_font.render("OYUN BİTTİ!", True, (255, 0, 0))
        yazi1_konum = yazi1.get_rect(center=(GENISLIK // 2, 150))
        yazi2 = self.oyun_font.render(f"Skorunuz: {self.puan}", True, (255, 255, 255))
        yazi2_konum = yazi2.get_rect(center=(GENISLIK // 2, 250))
        yazi3 = self.oyun_font.render(f"En Yüksek Skor: {en_yuksek}", True, (255, 255, 0))
        yazi3_konum = yazi3.get_rect(center=(GENISLIK // 2, 350))
        yazi4 = self.kucuk_font.render("Tekrar Oynamak İçin 'E' Tuşuna Basınız", True, (0, 255, 0))
        yazi4_konum = yazi4.get_rect(center=(GENISLIK // 2, 450))
        yazi5 = self.kucuk_font.render("Çıkmak İçin 'H' Tuşuna Basınız", True, (255, 100, 100))
        yazi5_konum = yazi5.get_rect(center=(GENISLIK // 2, 500))

        ekran.blit(yazi1, yazi1_konum)
        ekran.blit(yazi2, yazi2_konum)
        ekran.blit(yazi3, yazi3_konum)
        ekran.blit(yazi4, yazi4_konum)
        ekran.blit(yazi5, yazi5_konum)
        pygame.display.update()

        while oyun_bitti:
            for etkinlik in pygame.event.get():
                if etkinlik.type == pygame.QUIT:
                    oyun_bitti = False
                    status = False
                if etkinlik.type == pygame.KEYDOWN:
                    if etkinlik.key == pygame.K_e:
                        self.oyun_reset()
                        oyun_bitti = False
                    elif etkinlik.key == pygame.K_h:
                        oyun_bitti = False
                        status = False

    def oyun_tamamlandi(self):
        if not self.uzayli_grup:
            self.bolum_no += 1
            self.bolum()

    def oyunu_durdur(self):
        durduMu = True
        global status
        yazi1 = self.oyun_font.render("Uzaylılar yüzünden " + str(self.oyuncu.can) + " canınız kaldı!", True,
                                      (0, 110, 0), (255, 0, 0))
        yazi1_konum = yazi1.get_rect()
        yazi1_konum.topleft = (100, 150)
        yazi2 = self.oyun_font.render("Devam etmek için 'ENTER' tuşuna basınız...", True, (0, 110, 0), (255, 0, 0))
        yazi2_konum = yazi2.get_rect()
        yazi2_konum.topleft = (100, 250)
        ekran.blit(yazi1, yazi1_konum)
        ekran.blit(yazi2, yazi2_konum)
        pygame.display.update()

        while durduMu:
            for etkinlik in pygame.event.get():
                if etkinlik.type == pygame.KEYDOWN:
                    if etkinlik.key == pygame.K_RETURN:
                        durduMu = False
                if etkinlik.type == pygame.QUIT:
                    durduMu = False
                    status = False

    def oyun_reset(self):
        self.bolum_no = 1
        self.puan = 0
        self.oyuncu.can = 5
        self.uzayli_grup.empty()
        self.uzayli_mermi_grup.empty()
        self.player_mermi_grup.empty()
        self.bolum()

# -------------------------------------------------------
# NESNELERİN OLUŞTURULMASI

player_mermi = pygame.sprite.Group()
uzayli_mermi = pygame.sprite.Group()
oyuncu_grup = pygame.sprite.Group()
oyuncu = Player(player_mermi)
oyuncu_grup.add(oyuncu)
uzayli_grup = pygame.sprite.Group()
oyun = Oyun(oyuncu, uzayli_grup, player_mermi, uzayli_mermi)
oyun.bolum()

# -------------------------------------------------------
# OYUN DÖNGÜSÜ

status = True
while status:
    for etkinlik in pygame.event.get():
        if etkinlik.type == pygame.QUIT:
            status = False
        if etkinlik.type == pygame.KEYDOWN:
            if etkinlik.key == pygame.K_SPACE:
                oyuncu.saldiri()

    oyun.update()
    oyun.ciz()
    oyuncu_grup.update()
    oyuncu_grup.draw(ekran)
    player_mermi.update()
    player_mermi.draw(ekran)
    uzayli_grup.update()
    uzayli_grup.draw(ekran)
    uzayli_mermi.update()
    uzayli_mermi.draw(ekran)
    pygame.display.update()
    saat.tick(FPS)

pygame.quit()