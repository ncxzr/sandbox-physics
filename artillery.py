import pygame
import math
import random

# --- setup ---
pygame.init()
W, H = 800, 500
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Artillery Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont("monospace", 18)
small = pygame.font.SysFont("monospace", 14)

# --- constants ---
g = 300        # gravity (pixels/s^2)
dt = 1/60

# --- game state ---
angle = 45.0       # degrees
velocity = 300.0   # pixels/s
score = 0
misses = 0
max_misses = 3

# cannon position
cx, cy = 60, H - 60

# --- target ---
def new_target():
    x = random.randint(500, 720)
    y = random.randint(H - 150, H - 40)
    speed = random.choice([-60, 60])
    return {"x": x, "y": y, "w": 30, "h": 30, "speed": speed}

target = new_target()

# --- ball ---
ball = None  # None means not fired yet
trajectory = []  # preview dots

def preview_trajectory():
    pts = []
    rad = math.radians(angle)
    vx = velocity * math.cos(rad)
    vy = -velocity * math.sin(rad)
    x, y = cx, cy
    for _ in range(180):
        x += vx * dt
        y += vy * dt
        vy += g * dt
        pts.append((int(x), int(y)))
        if y > H:
            break
    return pts

def fire():
    global ball, trajectory
    rad = math.radians(angle)
    ball = {
        "x": cx, "y": cy,
        "vx": velocity * math.cos(rad),
        "vy": -velocity * math.sin(rad)
    }
    trajectory = []  # hide preview while ball is flying

def draw_cannon():
    # base
    pygame.draw.rect(screen, (80, 80, 80), (cx - 20, cy, 40, 20))
    # barrel
    rad = math.radians(angle)
    ex = cx + math.cos(rad) * 45
    ey = cy - math.sin(rad) * 45
    pygame.draw.line(screen, (60, 60, 60), (cx, cy), (int(ex), int(ey)), 8)

running = True
game_over = False

while running:
    clock.tick(60)
    screen.fill((30, 30, 40))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if not game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and ball is None:
                    fire()
                if event.key == pygame.K_r:
                    # restart
                    score = 0; misses = 0; game_over = False
                    ball = None; target = new_target()

        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                score = 0; misses = 0; game_over = False
                ball = None; target = new_target()

    if not game_over:
        # --- input ---
        keys = pygame.key.get_pressed()
        if ball is None:
            if keys[pygame.K_UP]:    angle = min(angle + 1, 89)
            if keys[pygame.K_DOWN]:  angle = max(angle - 1, 1)
            if keys[pygame.K_RIGHT]: velocity = min(velocity + 2, 600)
            if keys[pygame.K_LEFT]:  velocity = max(velocity - 2, 50)

        # --- update target ---
        target["x"] += target["speed"] * dt
        if target["x"] > 740 or target["x"] < 460:
            target["speed"] *= -1

        # --- update ball ---
        if ball:
            ball["x"] += ball["vx"] * dt
            ball["y"] += ball["vy"] * dt
            ball["vy"] += g * dt

            # hit target?
            tx, ty, tw, th = target["x"], target["y"], target["w"], target["h"]
            if tx < ball["x"] < tx + tw and ty < ball["y"] < ty + th:
                score += 1
                ball = None
                target = new_target()

            # miss (off screen)
            if ball["y"] > H or ball["x"] > W:
                misses += 1
                ball = None
                if misses >= max_misses:
                    game_over = True

        # --- preview ---
        if ball is None:
            trajectory = preview_trajectory()

        # --- draw ground ---
        pygame.draw.rect(screen, (60, 100, 60), (0, H - 20, W, 20))

        # --- draw trajectory preview ---
        for i, pt in enumerate(trajectory):
            if i % 5 == 0:
                pygame.draw.circle(screen, (100, 100, 180), pt, 2)

        # --- draw target ---
        pygame.draw.rect(screen, (220, 60, 60),
                         (int(target["x"]), int(target["y"]), target["w"], target["h"]))
        label = small.render("TARGET", True, (255, 200, 200))
        screen.blit(label, (int(target["x"]) - 4, int(target["y"]) - 16))

        # --- draw ball ---
        if ball:
            pygame.draw.circle(screen, (255, 220, 50),
                               (int(ball["x"]), int(ball["y"])), 7)

        # --- draw cannon ---
        draw_cannon()

        # --- HUD ---
        screen.blit(font.render(f"Angle:    {angle:.0f} deg  [UP/DOWN]",   True, (200,200,200)), (10, 10))
        screen.blit(font.render(f"Velocity: {velocity:.0f} px/s [LEFT/RIGHT]", True, (200,200,200)), (10, 32))
        screen.blit(font.render(f"Score: {score}   Misses: {misses}/{max_misses}", True, (255,255,100)), (10, 60))
        screen.blit(font.render("SPACE = fire", True, (150,150,150)), (10, 85))

        # --- physics label ---
        rad = math.radians(angle)
        vx = velocity * math.cos(rad)
        vy = velocity * math.sin(rad)
        screen.blit(small.render(f"vx={vx:.0f}  vy={vy:.0f}  g={g}", True, (120,120,160)), (10, H - 40))
        screen.blit(small.render("x=v0*cos(θ)*t   y=v0*sin(θ)*t - ½g*t²", True, (100,100,140)), (10, H - 22))

    else:
        # game over screen
        msg1 = font.render("GAME OVER", True, (255, 80, 80))
        msg2 = font.render(f"Final Score: {score}", True, (255, 220, 100))
        msg3 = font.render("Press R to restart", True, (200, 200, 200))
        screen.blit(msg1, (W//2 - msg1.get_width()//2, H//2 - 60))
        screen.blit(msg2, (W//2 - msg2.get_width()//2, H//2 - 20))
        screen.blit(msg3, (W//2 - msg3.get_width()//2, H//2 + 20))

    pygame.display.flip()

pygame.quit()
