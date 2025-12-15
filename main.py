import pygame
import random
import math
import sys

pygame.init()

W, H = 900, 600
TELA = pygame.display.set_mode((W, H))
pygame.display.set_caption("Dash or Die")

FPS = 60
CLOCK = pygame.time.Clock()

PRETO = (15, 15, 15)
BRANCO = (230, 230, 230)
AZUL = (80, 140, 255)
VERMELHO = (220, 60, 60)
AMARELO = (240, 200, 80)

FONTE = pygame.font.SysFont("arial", 24)

class Jogador:
    def __init__(self):
        self.x = W//2
        self.y = H//2
        self.r = 15
        self.vel = 4
        self.dash = 0
        self.inv = 0

    def mover(self, t):
        dx = dy = 0
        if t[pygame.K_w]: dy -= 1
        if t[pygame.K_s]: dy += 1
        if t[pygame.K_a]: dx -= 1
        if t[pygame.K_d]: dx += 1

        mag = math.hypot(dx, dy)
        if mag != 0:
            dx /= mag
            dy /= mag

        speed = 10 if self.dash > 0 else self.vel
        self.x += dx * speed
        self.y += dy * speed

        self.x = max(self.r, min(W - self.r, self.x))
        self.y = max(self.r, min(H - self.r, self.y))

    def usar_dash(self):
        if self.dash == 0:
            self.dash = 12
            self.inv = 15

    def update(self):
        if self.dash > 0:
            self.dash -= 1
        if self.inv > 0:
            self.inv -= 1

    def draw(self):
        cor = AMARELO if self.inv > 0 else AZUL
        pygame.draw.circle(TELA, cor, (int(self.x), int(self.y)), self.r)

class Inimigo:
    def __init__(self):
        lado = random.choice(["t","b","l","r"])
        if lado == "t": self.x, self.y = random.randint(0,W), -20
        if lado == "b": self.x, self.y = random.randint(0,W), H+20
        if lado == "l": self.x, self.y = -20, random.randint(0,H)
        if lado == "r": self.x, self.y = W+20, random.randint(0,H)
        self.r = random.randint(12,18)
        self.vel = random.uniform(1.5, 3)

    def update(self, j):
        ang = math.atan2(j.y - self.y, j.x - self.x)
        self.x += math.cos(ang) * self.vel
        self.y += math.sin(ang) * self.vel

    def draw(self):
        pygame.draw.circle(TELA, VERMELHO, (int(self.x), int(self.y)), self.r)

def main():
    j = Jogador()
    inimigos = []
    spawn = 0
    score = 0

    while True:
        CLOCK.tick(FPS)
        TELA.fill(PRETO)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LSHIFT:
                    j.usar_dash()

        t = pygame.key.get_pressed()
        j.mover(t)
        j.update()

        spawn += 1
        if spawn > max(20, 90 - score//10):
            inimigos.append(Inimigo())
            spawn = 0

        for i in inimigos[:]:
            i.update(j)
            i.draw()
            if math.hypot(i.x - j.x, i.y - j.y) < i.r + j.r:
                if j.inv == 0:
                    pygame.quit()
                    sys.exit()
                else:
                    inimigos.remove(i)
                    score += 1

        j.draw()

        txt = FONTE.render(f"Score: {score}", True, BRANCO)
        TELA.blit(txt, (20, 20))

        pygame.display.flip()

main()
