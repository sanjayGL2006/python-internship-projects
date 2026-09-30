import pygame
import random
import math

pygame.init()

# ============================================================
#                 SHADOW ESCAPE
#              A MINI 2D ADVENTURE
# ============================================================

WIDTH = 1000
HEIGHT = 650

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SHADOW ESCAPE")

clock = pygame.time.Clock()

# ---------------- COLORS ----------------

BLACK = (10, 10, 18)
DARK = (18, 20, 32)
WALL = (55, 58, 78)
WHITE = (240, 240, 245)
BLUE = (60, 170, 255)
GREEN = (70, 220, 120)
RED = (230, 65, 75)
YELLOW = (255, 210, 60)
PURPLE = (170, 80, 255)
ORANGE = (255, 140, 50)

# ---------------- FONTS ----------------

font = pygame.font.SysFont("arial", 22)
small_font = pygame.font.SysFont("arial", 17)
big_font = pygame.font.SysFont("arial", 52, bold=True)

# ---------------- PLAYER ----------------

player = pygame.Rect(80, 80, 35, 35)

player_speed = 5
health = 100
coins = 0
score = 0

# ---------------- EXIT ----------------

exit_rect = pygame.Rect(900, 540, 55, 70)

# ---------------- WALLS ----------------

walls = [
    pygame.Rect(0, 0, WIDTH, 20),
    pygame.Rect(0, HEIGHT - 20, WIDTH, 20),
    pygame.Rect(0, 0, 20, HEIGHT),
    pygame.Rect(WIDTH - 20, 0, 20, HEIGHT),

    pygame.Rect(150, 80, 30, 400),
    pygame.Rect(300, 0, 30, 300),
    pygame.Rect(450, 180, 30, 400),
    pygame.Rect(600, 0, 30, 300),
    pygame.Rect(750, 180, 30, 400),

    pygame.Rect(180, 500, 250, 30),
    pygame.Rect(520, 100, 180, 30),
]

# ---------------- COINS ----------------

coin_positions = [
    (90, 550),
    (230, 150),
    (380, 80),
    (380, 420),
    (550, 550),
    (700, 150),
    (700, 420),
    (850, 100),
    (850, 350),
    (500, 80),
]

coins_list = []

for x, y in coin_positions:
    coins_list.append(pygame.Rect(x, y, 18, 18))

# ---------------- ENEMIES ----------------

class Enemy:

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.speed = random.choice([2, 2, 3])
        self.direction = random.choice([-1, 1])
        self.timer = 0

    def update(self):

        self.timer += 1

        # Move randomly
        if self.timer > 60:
            self.direction = random.choice([-1, 1])
            self.timer = 0

        self.rect.x += self.direction * self.speed

        # Keep inside screen
        if self.rect.left < 25:
            self.rect.left = 25
            self.direction = 1

        if self.rect.right > WIDTH - 25:
            self.rect.right = WIDTH - 25
            self.direction = -1

        # Wall collision
        for wall in walls:
            if self.rect.colliderect(wall):
                self.rect.x -= self.direction * self.speed
                self.direction *= -1

enemies = [
    Enemy(250, 350),
    Enemy(550, 350),
    Enemy(850, 250),
    Enemy(600, 550),
]

# ---------------- PARTICLES ----------------

particles = []

for i in range(80):
    particles.append([
        random.randint(20, WIDTH - 20),
        random.randint(20, HEIGHT - 20),
        random.randint(1, 3)
    ])

# ---------------- GAME STATE ----------------

game_over = False
game_won = False

# ---------------- FUNCTIONS ----------------

def draw_text(text, x, y, color=WHITE, f=font):
    image = f.render(text, True, color)
    screen.blit(image, (x, y))


def move_player(dx, dy):

    global player

    # Horizontal movement
    player.x += dx

    for wall in walls:
        if player.colliderect(wall):
            if dx > 0:
                player.right = wall.left
            elif dx < 0:
                player.left = wall.right

    # Vertical movement
    player.y += dy

    for wall in walls:
        if player.colliderect(wall):
            if dy > 0:
                player.bottom = wall.top
            elif dy < 0:
                player.top = wall.bottom


def reset_game():

    global player
    global health
    global coins
    global score
    global coins_list
    global enemies
    global game_over
    global game_won

    player = pygame.Rect(80, 80, 35, 35)

    health = 100
    coins = 0
    score = 0

    coins_list = []

    for x, y in coin_positions:
        coins_list.append(pygame.Rect(x, y, 18, 18))

    enemies = [
        Enemy(250, 350),
        Enemy(550, 350),
        Enemy(850, 250),
        Enemy(600, 550),
    ]

    game_over = False
    game_won = False


# ============================================================
#                      MAIN GAME LOOP
# ============================================================

running = True

while running:

    clock.tick(60)

    # ---------------- EVENTS ----------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_r and (game_over or game_won):
                reset_game()

    # ========================================================
    #                     GAMEPLAY
    # ========================================================

    if not game_over and not game_won:

        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= player_speed

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += player_speed

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= player_speed

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += player_speed

        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        move_player(int(dx), int(dy))

        # ---------------- COINS ----------------

        for coin in coins_list[:]:

            if player.colliderect(coin):

                coins_list.remove(coin)

                coins += 1
                score += 100

        # ---------------- ENEMIES ----------------

        for enemy in enemies:

            enemy.update()

            if player.colliderect(enemy.rect):

                health -= 1

                # Push player away
                if player.centerx < enemy.rect.centerx:
                    player.x -= 6
                else:
                    player.x += 6

                if player.centery < enemy.rect.centery:
                    player.y -= 6
                else:
                    player.y += 6

        # ---------------- WIN ----------------

        if player.colliderect(exit_rect):

            if coins >= 5:
                game_won = True

        # ---------------- DEATH ----------------

        if health <= 0:
            game_over = True

    # ========================================================
    #                       DRAW
    # ========================================================

    screen.fill(BLACK)

    # ---------------- BACKGROUND ----------------

    for p in particles:

        pygame.draw.circle(
            screen,
            (35, 38, 55),
            (p[0], p[1]),
            p[2]
        )

    # ---------------- FLOOR ----------------

    pygame.draw.rect(
        screen,
        DARK,
        (20, 20, WIDTH - 40, HEIGHT - 40)
    )

    # Floor grid

    for x in range(20, WIDTH, 50):

        pygame.draw.line(
            screen,
            (25, 27, 42),
            (x, 20),
            (x, HEIGHT - 20)
        )

    for y in range(20, HEIGHT, 50):

        pygame.draw.line(
            screen,
            (25, 27, 42),
            (20, y),
            (WIDTH - 20, y)
        )

    # ---------------- WALLS ----------------

    for wall in walls:

        pygame.draw.rect(
            screen,
            WALL,
            wall,
            border_radius=4
        )

        pygame.draw.rect(
            screen,
            (80, 83, 105),
            wall,
            2,
            border_radius=4
        )

    # ---------------- EXIT ----------------

    exit_color = GREEN if coins >= 5 else RED

    pygame.draw.rect(
        screen,
        exit_color,
        exit_rect,
        border_radius=8
    )

    draw_text(
        "EXIT",
        exit_rect.x + 5,
        exit_rect.y + 22,
        BLACK,
        small_font
    )

    # ---------------- COINS ----------------

    for coin in coins_list:

        pygame.draw.circle(
            screen,
            YELLOW,
            coin.center,
            9
        )

        pygame.draw.circle(
            screen,
            ORANGE,
            coin.center,
            9,
            2
        )

    # ---------------- ENEMIES ----------------

    for enemy in enemies:

        pygame.draw.rect(
            screen,
            RED,
            enemy.rect,
            border_radius=8
        )

        # Eyes

        pygame.draw.circle(
            screen,
            WHITE,
            (enemy.rect.x + 9, enemy.rect.y + 10),
            5
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (enemy.rect.x + 23, enemy.rect.y + 10),
            5
        )

        pygame.draw.circle(
            screen,
            BLACK,
            (enemy.rect.x + 9, enemy.rect.y + 10),
            2
        )

        pygame.draw.circle(
            screen,
            BLACK,
            (enemy.rect.x + 23, enemy.rect.y + 10),
            2
        )

    # ---------------- PLAYER ----------------

    pygame.draw.rect(
        screen,
        BLUE,
        player,
        border_radius=8
    )

    # Player glow

    pygame.draw.rect(
        screen,
        (100, 200, 255),
        player,
        2,
        border_radius=8
    )

    # ---------------- HUD ----------------

    pygame.draw.rect(
        screen,
        (12, 13, 22),
        (0, 0, WIDTH, 65)
    )

    draw_text("SHADOW ESCAPE", 25, 18, PURPLE)

    # Health bar

    draw_text("HP", 250, 21, WHITE, small_font)

    pygame.draw.rect(
        screen,
        (60, 20, 25),
        (285, 22, 160, 18)
    )

    pygame.draw.rect(
        screen,
        GREEN if health > 30 else RED,
        (285, 22, int(160 * health / 100), 18)
    )

    draw_text(
        f"{health}/100",
        330,
        21,
        WHITE,
        small_font
    )

    draw_text(
        f"🪙 {coins}/5",
        470,
        20,
        YELLOW,
        small_font
    )

    draw_text(
        f"SCORE: {score}",
        580,
        20,
        WHITE,
        small_font
    )

    draw_text(
        "WASD / ARROWS = MOVE",
        750,
        20,
        WHITE,
        small_font
    )

    # ---------------- MESSAGE ----------------

    if coins < 5:

        draw_text(
            f"Collect {5 - coins} more coin(s) to unlock the EXIT!",
            25,
            HEIGHT - 35,
            YELLOW,
            small_font
        )

    else:

        draw_text(
            "EXIT UNLOCKED! 🚪 GET TO THE GREEN DOOR!",
            25,
            HEIGHT - 35,
            GREEN,
            small_font
        )

    # ========================================================
    #                     WIN SCREEN
    # ========================================================

    if game_won:

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((5, 10, 15))
        screen.blit(overlay, (0, 0))

        text = big_font.render(
            "YOU ESCAPED!",
            True,
            GREEN
        )

        screen.blit(
            text,
            (
                WIDTH // 2 - text.get_width() // 2,
                230
            )
        )

        draw_text(
            f"FINAL SCORE: {score}",
            WIDTH // 2 - 100,
            310,
            WHITE
        )

        draw_text(
            "Press R to play again",
            WIDTH // 2 - 100,
            360,
            YELLOW
        )

    # ========================================================
    #                    GAME OVER SCREEN
    # ========================================================

    if game_over:

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((20, 0, 5))
        screen.blit(overlay, (0, 0))

        text = big_font.render(
            "YOU DIED",
            True,
            RED
        )

        screen.blit(
            text,
            (
                WIDTH // 2 - text.get_width() // 2,
                230
            )
        )

        draw_text(
            f"SCORE: {score}",
            WIDTH // 2 - 55,
            310,
            WHITE
        )

        draw_text(
            "Press R to restart",
            WIDTH // 2 - 90,
            360,
            YELLOW
        )

    pygame.display.flip()


pygame.quit()
