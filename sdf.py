#!/usr/bin/env python3

import pygame
import random
import math

class Eye:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.degrees = 0.0
        self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        # self.color = (50, 150, 100)
        self.points = []

    def get_dir(self):
        rads = math.radians(self.degrees)
        return pygame.Vector2(math.cos(rads), math.sin(rads))

    def draw(self, screen, game):
        if game.draw_eyes:
            pygame.draw.circle(screen, (200, 200, 200), self.pos, 2)
            pygame.draw.circle(screen, (200, 200, 200), self.pos, 16, 1)
        dir = self.get_dir()
        start = self.pos
        traveled = 0.0
        while True:
            old_pos = start + dir * traveled
            dist = game.get_nearest(old_pos)
            traveled += dist
            if abs(traveled) > 1000:
                break
            new_pos = start + dir * traveled
            if game.draw_eyes:
                # pygame.draw.circle(screen, (200, 200, 200), old_pos, dist, 1)
                pygame.draw.line(screen, (200, 200, 200), old_pos, new_pos)
            if abs(dist) < 1:
                self.points.append(new_pos)
                if len(self.points) > 100:
                    self.points.pop(0)
                break
        for p in self.points:
            pygame.draw.circle(screen, self.color, p, 2)

    def update(self, delta):
        self.degrees += 360 * delta
        while self.degrees > 360:
            self.degrees -= 360

class Circle:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.radius = random.randint(16, 64)
        self.speed = random.random() * 32
        rads = math.radians(random.random() * 360)
        self.dir = pygame.Vector2(math.cos(rads), math.sin(rads))

    def draw(self, screen):
        pygame.draw.circle(screen, (50, 200, 50), self.pos, 2)
        pygame.draw.circle(screen, (50, 200, 50), self.pos, self.radius, 1)
        pass

    def dist(self, eye_pos):
        v = eye_pos - self.pos
        return v.length() - self.radius
    
    def update(self, delta):
        w, h = pygame.display.get_surface().get_size()
        self.pos += self.dir * self.speed * delta
        if self.pos.x < self.radius or self.pos.x > w - self.radius:
            self.dir.x = -self.dir.x
        if self.pos.y < self.radius or self.pos.y > h- self.radius:
            self.dir.y = -self.dir.y

class MyGame:
    def __init__(self):
        self.eyes = []
        self.circles = []
        self.draw_circles = True
        self.draw_eyes = True

    def spawn_eye(self, pos):
        self.eyes.append(Eye(pos))

    def spawn_circle(self, pos):
        self.circles.append(Circle(pos))

    def draw(self, screen):
        if self.draw_circles:
            for circle in self.circles:
                circle.draw(screen)
        for eye in self.eyes:
            eye.draw(screen, self)

    def update(self, delta):
        for e in self.eyes:
            e.update(delta)
        for c in self.circles:
            c.update(delta)

    def smooth_min(self, a, b, delta):
        adj = max(delta - abs(a - b), 0) / delta
        return min(a, b) - pow(adj, 2) * delta * 0.25

    def get_nearest(self, pos):
        dists = list(map((lambda c: c.dist(pos)), self.circles))
        m = 10000
        for dist in dists:
            m = self.smooth_min(m, dist, 48)
        return m
    
    def populate(self):
        w, h = pygame.display.get_surface().get_size()
        for i in range(32):
            r = random.randint(8, 64)
            x = random.randint(r, w - r)
            y = random.randint(r, h - r)
            c = Circle((x, y))
            c.radius = r
            self.circles.append(c)

    def run(self):
        screen = pygame.display.set_mode((640, 480))
        clock = pygame.time.Clock()
        running = True
        self.populate()
        while running:
            delta = clock.tick(120) / 1000
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.MOUSEBUTTONUP:
                    if e.button == 1:
                        self.spawn_eye(e.pos)
                    elif e.button == 3:
                        self.spawn_circle(e.pos)
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_v:
                        self.draw_circles = not self.draw_circles
                    elif e.key == pygame.K_e:
                        self.draw_eyes = not self.draw_eyes
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                running = False
            self.update(delta)
            screen.fill((20, 20, 20))
            self.draw(screen)
            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    game = MyGame()
    game.run()
