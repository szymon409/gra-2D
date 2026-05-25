import pygame
import sys
import random
import time

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wyprawa 2D")

clock = pygame.time.Clock()
FPS = 60

font = pygame.font.SysFont("Arial", 22)
font_big = pygame.font.SysFont("Arial", 38)

MAP_W, MAP_H = 120, 120
TILE = 32

BLUE = (50, 100, 255)
RED = (255, 50, 50)

GRASS = (100, 220, 100)
FOREST = (20, 140, 20)
DESERT = (230, 210, 120)
MOUNTAIN = (120, 120, 120)

def generate_map():
    world = []

    for y in range(MAP_H):
        row = []
        for x in range(MAP_W):
            r = random.randint(1, 100)

            if r < 25:
                row.append("forest")
            elif r < 45:
                row.append("desert")
            elif r < 60:
                row.append("mountain")
            else:
                row.append("grass")

        world.append(row)

    return world


def color(tile):
    if tile == "forest":
        return FOREST
    if tile == "desert":
        return DESERT
    if tile == "mountain":
        return MOUNTAIN
    return GRASS


def new_level(level):
    world = generate_map()
    px = MAP_W // 2
    py = MAP_H // 2

    gx = random.randint(0, MAP_W - 1)
    gy = random.randint(0, MAP_H - 1)

    print(f"\n=== LEVEL {level} ===")

    return world, px, py, gx, gy


def compass(px, py, gx, gy):
    dx = gx - px
    dy = gy - py

    if abs(dx) > abs(dy):
        return "→ Wschód" if dx > 0 else "← Zachód"
    else:
        return "↓ Południe" if dy > 0 else "↑ Północ"


level = 1
world, player_x, player_y, goal_x, goal_y = new_level(level)

camera_x = 0
camera_y = 0

energy = 100
max_energy = 100

last_move = 0

game_over = False
victory = False

level_start_time = time.time()

stunned = False
stun_end_time = 0

bear_bonus_text = ""
bear_bonus_timer = 0

print("=== zgubiłeś dziecko w lesie (czerwony kwadrat) ===")

running = True

while running:
    clock.tick(FPS)
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    sprint_key = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
    can_sprint = sprint_key and energy > 10

    move_delay = 80 if can_sprint else 180

    if can_sprint:
        energy -= 1.5
    else:
        if not sprint_key:
            energy += 0.2

    energy = max(0, min(max_energy, energy))

    elapsed = time.time() - level_start_time

    if elapsed >= 15 and not victory:
        game_over = True

    if stunned and time.time() >= stun_end_time:
        stunned = False
        print("=== WSTAJESZ I BIEGNIESZ DALEJ ===")

    if not game_over and not stunned:

        dx = 0
        dy = 0

        if now - last_move > move_delay:

            if keys[pygame.K_w]:
                dy = -1
            elif keys[pygame.K_s]:
                dy = 1
            elif keys[pygame.K_a]:
                dx = -1
            elif keys[pygame.K_d]:
                dx = 1

            if dx != 0 or dy != 0:

                new_x = player_x + dx
                new_y = player_y + dy

                if 0 <= new_x < MAP_W and 0 <= new_y < MAP_H:

                    player_x = new_x
                    player_y = new_y

                    if random.randint(1, 100) <= 6:
                        stunned = True
                        stun_end_time = time.time() + 1.5
                        print("!!! PRZEWROCILES SIE !!!")

                    bear_event = random.randint(1, 100)

                    if bear_event <= 4:
                        level_start_time += 1.5
                        bear_bonus_text = "NIEDZWIEDZ SIE PRZEWROCIL +1.5s"
                        bear_bonus_timer = time.time() + 2

                        print(
                            f"[{time.strftime('%H:%M:%S')}] "
                            f"NIEDZWIEDZ SIE PRZEWROCIL -> +1.5s (Level {level})"
                        )

                    direction = ""
                    if dx == 1:
                        direction = "PRAWO"
                    elif dx == -1:
                        direction = "LEWO"
                    elif dy == 1:
                        direction = "DOL"
                    elif dy == -1:
                        direction = "GORA"

                    tile = world[player_y][player_x]

                    print(f"[{direction}] X:{player_x} Y:{player_y} | Teren:{tile} | Level:{level}")

                last_move = now

    if not game_over and player_x == goal_x and player_y == goal_y:

        print(f"=== ZNALEZIONO DZIECKO | LEVEL {level} UKONCZONY ===")

        if level >= 3:
            game_over = True
            victory = True
            print("=== znalazłeś dziecko ===")
        else:
            level += 1
            world, player_x, player_y, goal_x, goal_y = new_level(level)
            energy = max_energy
            level_start_time = time.time()

    camera_x = player_x * TILE - WIDTH // 2
    camera_y = player_y * TILE - HEIGHT // 2

    camera_x = max(0, min(camera_x, MAP_W * TILE - WIDTH))
    camera_y = max(0, min(camera_y, MAP_H * TILE - HEIGHT))

    screen.fill((30, 30, 30))

    start_x = camera_x // TILE
    start_y = camera_y // TILE
    end_x = min(MAP_W, start_x + WIDTH // TILE + 2)
    end_y = min(MAP_H, start_y + HEIGHT // TILE + 2)

    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            pygame.draw.rect(
                screen,
                color(world[y][x]),
                (x * TILE - camera_x, y * TILE - camera_y, TILE, TILE)
            )

    pygame.draw.rect(
        screen,
        RED,
        (goal_x * TILE - camera_x, goal_y * TILE - camera_y, TILE, TILE)
    )

    pygame.draw.rect(
        screen,
        BLUE,
        (player_x * TILE - camera_x, player_y * TILE - camera_y, TILE, TILE)
    )

    hud = [
        f"Level: {level}",
        "WASD | SHIFT sprint",
        compass(player_x, player_y, goal_x, goal_y),
        f"Energia: {int(energy)}",
        f"Czas: {max(0, 15 - int(elapsed))}"
    ]

    if stunned:
        hud.append("PRZEWROCILES SIE!")

    if time.time() < bear_bonus_timer:
        hud.append(bear_bonus_text)

    for i, line in enumerate(hud):
        screen.blit(font.render(line, True, (255, 255, 255)), (10, 10 + i * 25))

    pygame.draw.rect(screen, (80, 80, 80), (10, 170, 200, 15))
    pygame.draw.rect(screen, (0, 200, 255), (10, 170, 200 * (energy / max_energy), 15))

    if game_over:

        text = font_big.render(
            "UKONCZYLES GRE!" if victory else "dziecko zostalo zjedzone przez niedzwiedzia",
            True,
            (255, 255, 0) if victory else (255, 50, 50)
        )

        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, rect)

    pygame.display.flip()

pygame.quit()
sys.exit()