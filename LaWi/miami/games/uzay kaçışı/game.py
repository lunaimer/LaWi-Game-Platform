import pygame
import random
import math
import sqlite3
import os
from datetime import datetime

pygame.init()


# Veritabanı bağlantısını oluştur
def init_database():
    conn = sqlite3.connect('space_escape_scores.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scores
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  player_name TEXT,
                  score INTEGER,
                  date TEXT)''')
    conn.commit()
    conn.close()


# Yüksek skorları veritabanına kaydet
def save_score_to_db(score, player_name="Player"):
    conn = sqlite3.connect('space_escape_scores.db')
    c = conn.cursor()
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO scores (player_name, score, date) VALUES (?, ?, ?)",
              (player_name, score, current_date))
    conn.commit()
    conn.close()


# En yüksek skoru veritabanından al
def get_high_score_from_db():
    conn = sqlite3.connect('space_escape_scores.db')
    c = conn.cursor()
    c.execute("SELECT MAX(score) FROM scores")
    result = c.fetchone()
    conn.close()
    return result[0] if result[0] is not None else 0


# İlk 5 yüksek skoru al
def get_top_scores(limit=5):
    conn = sqlite3.connect('space_escape_scores.db')
    c = conn.cursor()
    c.execute("SELECT player_name, score, date FROM scores ORDER BY score DESC LIMIT ?", (limit,))
    results = c.fetchall()
    conn.close()
    return results


# Veritabanını başlat
init_database()

# Ekran boyutunu
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Uzay Kaçışı")

# FPS (Kare/Saniye) ayarı
clock = pygame.time.Clock()
FPS = 120

# Renkleri tanımla
black = (0, 0, 0)
white = (255, 255, 255)
blue = (0, 0, 255)
gray = (100, 100, 100)
dark_gray = (50, 50, 50)
red = (255, 0, 0)
dark_red = (150, 0, 0)
orange = (255, 165, 0)
yellow = (255, 255, 0)
green = (0, 255, 0)

# --- Oyuncu Değişkenleri ---
player_width = 40
player_height = 60
player_x = (screen_width / 2)
player_y = screen_height - player_height - 10
player_speed_x = 7
player_speed_y = 0
gravity = 1
jump_speed = -10
is_jumping = False

# --- Engel Değişkenleri ---
obstacle_width = 50
obstacle_height = 50
obstacle_list = []
base_obstacle_spawn_rate = 40
obstacle_spawn_rate = base_obstacle_spawn_rate
obstacle_timer = 0
base_game_speed = 5
game_speed = base_game_speed

# --- Yıldızlar (Arka plan için) ---
stars = []
for _ in range(200):
    star_x = random.randrange(0, screen_width)
    star_y = random.randrange(0, screen_height)
    stars.append((star_x, star_y))

# --- Puan Değişkeni ---
score = 0
high_score = get_high_score_from_db()
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
game_over = False
player_name = "Player"
name_input_active = False


def create_obstacle():
    """Rastgele bir konumda yeni bir engel oluşturur ve alevli olup olmadığını belirler."""
    obstacle_x = random.randrange(0, screen_width - obstacle_width)
    obstacle_y = -obstacle_height
    is_flaming = random.random() < 0.8  # %80 olasılıkla alevli
    return {'rect': pygame.Rect(obstacle_x, obstacle_y, obstacle_width, obstacle_height), 'is_flaming': is_flaming}


def draw_player(surface, color, center_x, center_y, size):
    """Uzay gemisi şeklinde bir oyuncu çizer."""
    # Uzay gemisinin ana gövdesi için noktalar
    points = [
        (center_x, center_y - size),
        (center_x - size, center_y + size - 10),
        (center_x - size + 10, center_y + size),
        (center_x + size - 10, center_y + size),
        (center_x + size, center_y + size - 10)
    ]
    pygame.draw.polygon(surface, color, points)

    # Motor egzozları için küçük üçgenler
    pygame.draw.polygon(surface, (150, 200, 255), [
        (center_x - size + 10, center_y + size),
        (center_x - size + 5, center_y + size + 10),
        (center_x - 5, center_y + size)
    ])
    pygame.draw.polygon(surface, (150, 200, 255), [
        (center_x + size - 10, center_y + size),
        (center_x + size - 5, center_y + size + 10),
        (center_x + 5, center_y + size)
    ])

    # Çarpışma için ana gövdeyi kapsayan bir dikdörtgen döndürür
    return pygame.Rect(center_x - size, center_y - size, size * 2, size * 2 + 10)


def draw_asteroid(surface, rect, is_flaming):
    """Asteroit şeklinde ve alev efektli bir engel çizer."""
    # Asteroit gövdesi (düzensiz çokgen)
    points = [
        (rect.left + 5, rect.top),
        (rect.right, rect.top + 10),
        (rect.right - 5, rect.bottom),
        (rect.left, rect.bottom - 10)
    ]
    pygame.draw.polygon(surface, dark_gray, points)

    # Alev efekti
    if is_flaming:
        for _ in range(5):
            flame_size = random.randint(5, 15)
            flame_x = rect.left + random.randint(0, rect.width)
            flame_y = rect.top + random.randint(0, rect.height)
            pygame.draw.circle(surface, random.choice([yellow, orange]), (flame_x, flame_y), flame_size)

        for _ in range(3):
            flame_size = random.randint(8, 18)
            flame_x = rect.left + random.randint(0, rect.width)
            flame_y = rect.top + random.randint(0, rect.height)
            pygame.draw.circle(surface, random.choice([red, orange]), (flame_x, flame_y), flame_size)


# Oyun döngüsü
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_over and name_input_active:
                if event.key == pygame.K_RETURN:
                    name_input_active = False
                    save_score_to_db(score, player_name)
                    high_score = get_high_score_from_db()
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    # Sadece harf ve rakamları kabul et, maksimum 15 karakter
                    if len(player_name) < 15 and event.unicode.isalnum():
                        player_name += event.unicode

            elif game_over and not name_input_active:
                if event.key == pygame.K_SPACE:
                    game_over = False
                    score = 0
                    game_speed = base_game_speed
                    obstacle_list.clear()
                    name_input_active = True  # Yeni oyun için isim girişi aktif

            elif not game_over and event.key == pygame.K_h:
                # Yüksek skorları göster
                show_high_scores = True
                while show_high_scores:
                    for e in pygame.event.get():
                        if e.type == pygame.QUIT:
                            show_high_scores = False
                            running = False
                        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                            show_high_scores = False

                    screen.fill(black)
                    title_text = font.render("En Yüksek Skorlar", True, yellow)
                    screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 50))

                    top_scores = get_top_scores()
                    y_pos = 100
                    for i, (name, score_val, date) in enumerate(top_scores):
                        score_text = small_font.render(f"{i + 1}. {name}: {score_val} - {date.split()[0]}", True, white)
                        screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, y_pos))
                        y_pos += 30

                    instruction = small_font.render("Çıkmak için ESC tuşuna basın", True, gray)
                    screen.blit(instruction, (screen_width // 2 - instruction.get_width() // 2, screen_height - 50))

                    pygame.display.flip()
                    clock.tick(FPS)

    if not game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed_x
        if keys[pygame.K_RIGHT] and player_x < screen_width - player_width:
            player_x += player_speed_x
        if keys[pygame.K_SPACE] and not is_jumping:
            is_jumping = True
            player_speed_y = jump_speed

        player_speed_y += gravity
        player_y += player_speed_y
        if player_y >= screen_height - player_height - 10:
            player_y = screen_height - player_height - 10
            is_jumping = False
            player_speed_y = 0

        obstacle_timer += 1
        if obstacle_timer >= obstacle_spawn_rate:
            obstacle_list.append(create_obstacle())
            obstacle_timer = 0

        for obstacle in obstacle_list:
            obstacle['rect'].y += game_speed

        obstacle_list = [obs for obs in obstacle_list if obs['rect'].y < screen_height]

        score += 1
        game_speed = base_game_speed + (score // 500)
        obstacle_spawn_rate = base_obstacle_spawn_rate - (score // 500) * 2
        if obstacle_spawn_rate < 30:
            obstacle_spawn_rate = 30

        screen.fill(black)

        for star in stars:
            pygame.draw.circle(screen, white, star, 1)

        player_rect = draw_player(screen, blue, player_x + player_width // 2, player_y + player_height // 2,
                                  player_width // 2)

        for obstacle in obstacle_list:
            draw_asteroid(screen, obstacle['rect'], obstacle['is_flaming'])
            if player_rect.colliderect(obstacle['rect']):
                game_over = True
                if score > high_score:
                    high_score = score
                save_score_to_db(score, player_name)

        text = font.render(f"Puan: {score}", True, white)
        screen.blit(text, (10, 10))

        high_score_text = font.render(f"En Yüksek: {high_score}", True, white)
        screen.blit(high_score_text, (screen_width - high_score_text.get_width() - 10, 10))

        # Yüksek skorları görüntüleme kısayolu
        help_text = small_font.render("Yüksek skorlar için 'H' tuşuna basın", True, gray)
        screen.blit(help_text, (screen_width - help_text.get_width() - 10, screen_height - 30))

    else:
        if name_input_active:
            # İsim giriş ekranı
            screen.fill(black)
            game_over_text = font.render("Oyun Bitti!", True, red)
            score_text = font.render(f"Puanınız: {score}", True, white)

            if score > high_score:
                new_high_text = font.render("Yeni Rekor!", True, yellow)
                screen.blit(new_high_text,
                            (screen_width // 2 - new_high_text.get_width() // 2, screen_height // 2 - 80))

            name_prompt = font.render("İsminizi girin:", True, white)
            name_input = font.render(player_name + "|", True, green)  # İmleç efekti

            instruction = font.render("Tamamlamak için ENTER tuşuna basın", True, gray)

            screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 2 - 150))
            screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, screen_height // 2 - 100))
            screen.blit(name_prompt, (screen_width // 2 - name_prompt.get_width() // 2, screen_height // 2 - 30))
            screen.blit(name_input, (screen_width // 2 - name_input.get_width() // 2, screen_height // 2 + 10))
            screen.blit(instruction, (screen_width // 2 - instruction.get_width() // 2, screen_height // 2 + 70))
        else:
            # Oyun bitti ekranı
            game_over_text = font.render("Oyun Bitti!", True, red)
            score_text = font.render(f"Puanınız: {score}", True, white)
            high_score_text = font.render(f"En Yüksek Skor: {high_score}", True, yellow)
            restart_text = font.render("Yeniden Başlamak İçin Boşluk Tuşuna Basın", True, white)

            text_rect = game_over_text.get_rect(center=(screen_width / 2, screen_height / 2 - 80))
            score_rect = score_text.get_rect(center=(screen_width / 2, screen_height / 2 - 30))
            high_score_rect = high_score_text.get_rect(center=(screen_width / 2, screen_height / 2 + 10))
            restart_rect = restart_text.get_rect(center=(screen_width / 2, screen_height / 2 + 60))

            screen.fill(black)
            screen.blit(game_over_text, text_rect)
            screen.blit(score_text, score_rect)
            screen.blit(high_score_text, high_score_rect)
            screen.blit(restart_text, restart_rect)

    pygame.display.flip()

pygame.quit()