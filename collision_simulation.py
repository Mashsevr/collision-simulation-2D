
import pygame
import random
import math
import matplotlib.pyplot as plt
import time

# Настройки экрана
WIDTH, HEIGHT = 800, 600
FPS = 60

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Столкновения: энергия и импульс")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
BUTTON_COLOR = (100, 100, 255)
BUTTON_HOVER = (150, 150, 255)

elastic_collisions = True  # Переключатель типа столкновений
show_vectors = False
show_trails = True
simulation_paused = False
simulation_speed = 1.0

energy_history = []
momentum_history = []
time_history = []
start_time = time.time()

class Ball:
    def __init__(self, x, y, vx, vy, mass, radius):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.mass = mass
        self.radius = radius
        self.path = []

    def get_color(self):
        speed = math.hypot(self.vx, self.vy)
        energy = 0.5 * self.mass * speed**2
        r = min(255, int(energy * 5))
        g = 50
        b = 255 - r if r < 255 else 0
        return (r, g, b)

    def move(self):
        self.x += self.vx * simulation_speed
        self.y += self.vy * simulation_speed
        if show_trails:
            self.path.append((self.x, self.y))
            if len(self.path) > 50:
                self.path.pop(0)

        if self.x - self.radius < 0 or self.x + self.radius > WIDTH:
            self.vx *= -1
        if self.y - self.radius < 0 or self.y + self.radius > HEIGHT:
            self.vy *= -1

    def draw(self, surface):
        if show_trails:
            for point in self.path:
                pygame.draw.circle(surface, GRAY, (int(point[0]), int(point[1])), 1)
        pygame.draw.circle(surface, self.get_color(), (int(self.x), int(self.y)), self.radius)
        if show_vectors:
            end_x = self.x + self.vx * 10
            end_y = self.y + self.vy * 10
            pygame.draw.line(surface, WHITE, (self.x, self.y), (end_x, end_y), 2)

    def collide(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        dist = math.hypot(dx, dy)
        if dist < self.radius + other.radius:
            angle = math.atan2(dy, dx)
            v1 = self.vx * math.cos(angle) + self.vy * math.sin(angle)
            v2 = other.vx * math.cos(angle) + other.vy * math.sin(angle)

            if elastic_collisions:
                u1 = (v1 * (self.mass - other.mass) + 2 * other.mass * v2) / (self.mass + other.mass)
                u2 = (v2 * (other.mass - self.mass) + 2 * self.mass * v1) / (self.mass + other.mass)
            else:
                u1 = u2 = (self.mass * v1 + other.mass * v2) / (self.mass + other.mass)

            self.vx += (u1 - v1) * math.cos(angle)
            self.vy += (u1 - v1) * math.sin(angle)
            other.vx += (u2 - v2) * math.cos(angle)
            other.vy += (u2 - v2) * math.sin(angle)

            overlap = 0.5 * (self.radius + other.radius - dist + 1)
            self.x -= overlap * math.cos(angle)
            self.y -= overlap * math.sin(angle)
            other.x += overlap * math.cos(angle)
            other.y += overlap * math.sin(angle)

def draw_button(x, y, w, h, text):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    hovered = x < mouse[0] < x + w and y < mouse[1] < y + h
    color = BUTTON_HOVER if hovered else BUTTON_COLOR
    pygame.draw.rect(screen, color, (x, y, w, h))
    txt = font.render(text, True, WHITE)
    screen.blit(txt, (x + 5, y + 5))
    return hovered and click[0]

def draw_ui():
    mode_text = "Упругие" if elastic_collisions else "Неупругие"
    txt = font.render(f"Тип столкновений: {mode_text} (E)", True, WHITE)
    screen.blit(txt, (10, 10))

def total_energy():
    return sum(0.5 * b.mass * (b.vx**2 + b.vy**2) for b in balls)

def total_momentum():
    px = sum(b.mass * b.vx for b in balls)
    py = sum(b.mass * b.vy for b in balls)
    return math.hypot(px, py)

def average_energy():
    return total_energy() / len(balls) if balls else 0

def average_momentum():
    return total_momentum() / len(balls) if balls else 0

def plot_graphs():
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.plot(time_history, energy_history, label="Энергия")
    plt.title("Энергия во времени")
    plt.xlabel("время (с)")
    plt.ylabel("энергия")

    plt.subplot(1, 2, 2)
    plt.plot(time_history, momentum_history, label="Импульс", color="orange")
    plt.title("Импульс во времени")
    plt.xlabel("время (с)")
    plt.ylabel("импульс")

    plt.tight_layout()
    plt.show()

balls = []
for _ in range(5):
    r = random.randint(15, 25)
    m = r / 5
    x = random.randint(r, WIDTH - r)
    y = random.randint(r, HEIGHT - r)
    vx = random.uniform(-2, 2)
    vy = random.uniform(-2, 2)
    balls.append(Ball(x, y, vx, vy, m, r))

running = True
while running:
    clock.tick(FPS)
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                elastic_collisions = not elastic_collisions
            elif event.key == pygame.K_v:
                show_vectors = not show_vectors
            elif event.key == pygame.K_SPACE:
                simulation_paused = not simulation_paused
            elif event.key == pygame.K_t:
                show_trails = not show_trails
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                simulation_speed = min(simulation_speed + 0.1, 5.0)
            elif event.key == pygame.K_MINUS:
                simulation_speed = max(simulation_speed - 0.1, 0.1)
            elif event.key == pygame.K_g:
                plot_graphs()

    if draw_button(10, 40, 180, 30, "Добавить шар"):
        r = random.randint(15, 25)
        m = r / 5
        x = random.randint(r, WIDTH - r)
        y = random.randint(r, HEIGHT - r)
        vx = random.uniform(-2, 2)
        vy = random.uniform(-2, 2)
        balls.append(Ball(x, y, vx, vy, m, r))

    if draw_button(10, 80, 180, 30, "Удалить последний") and balls:
        balls.pop()

    if draw_button(10, 120, 180, 30, "Сбросить всё"):
        balls.clear()

    if not simulation_paused:
        for ball in balls:
            ball.move()
        for i in range(len(balls)):
            for j in range(i + 1, len(balls)):
                balls[i].collide(balls[j])

    for ball in balls:
        ball.draw(screen)

    draw_ui()

    # Отображение энергии и импульса
    e = total_energy()
    p = total_momentum()
    t = time.time() - start_time
    energy_history.append(e)
    momentum_history.append(p)
    time_history.append(t)

    energy_text = font.render(f"Энергия: {e:.2f}", True, WHITE)
    momentum_text = font.render(f"Импульс: {p:.2f}", True, WHITE)
    avg_energy_text = font.render(f"СКЭ на шар: {average_energy():.2f}", True, WHITE)
    avg_momentum_text = font.render(f"Имп. на шар: {average_momentum():.2f}", True, WHITE)
    screen.blit(energy_text, (WIDTH - 180, 10))
    screen.blit(momentum_text, (WIDTH - 180, 30))
    screen.blit(avg_energy_text, (WIDTH - 180, 50))
    screen.blit(avg_momentum_text, (WIDTH - 180, 70))

    pygame.display.flip()

pygame.quit()
