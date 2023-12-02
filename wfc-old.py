#!/usr/bin/env python3

import pygame
import random

class Cell:

    def __init__(self):
        self.values = ["red", "green", "blue"]
        self.collapsed = False

    def get_color(self):
        final_color = pygame.Vector3()
        for color_name in self.values:
            color = pygame.Color(color_name)
            final_color += (color.r, color.g, color.b)
        if len(self.values) > 0:
            final_color /= len(self.values)
        return final_color

    def draw(self, game, rect):
        color = self.get_color()
        pygame.draw.rect(game.win, color, rect)

    def cardinality(self):
        return len(self.values)

    def collapse(self):
        self.collapsed = True
        self.values = [random.choice(self.values)]

    def remove(self, value):
        if value in self.values:
            self.values.remove(value)

class Grid:

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.cells = [Cell() for _ in range(rows * cols)]
    
    def get_cell(self, x, y):
        return self.cells[y * self.cols + x]
    
    def next_cell(self):
        cells = []
        for y in range(self.rows):
            for x in range(self.cols):
                cell = self.get_cell(x, y)
                if not cell.collapsed and cell.cardinality() > 0:
                    cells.append((x, y, cell))
        if len(cells) > 0:
            return random.choice(cells)
        return (0, 0, None)
    
    def propagate(self, x, y):
        value = self.get_cell(x, y).values[0]
        if x > 0:
            self.get_cell(x - 1, y).remove(value)
        if x < self.cols - 1:
            self.get_cell(x + 1, y).remove(value)
        if y > 0:
            self.get_cell(x, y - 1).remove(value)
        if y < self.rows - 1:
            self.get_cell(x, y + 1).remove(value)

    def collapse(self, x, y):
        x = int(x)
        y = int(y)
        print(f"collapsing {x}, {y}")
        cell = self.get_cell(x, y)
        if cell.collapsed:
            return
        cell.collapse()
        self.propagate(x, y)
    
    def collapse_rand(self):
        x, y, cell = self.next_cell()
        if cell:
            self.collapse(x, y)

    def draw(self, game):
        ww, wh = game.win.get_size()
        cell_width = ww / self.cols
        cell_height = wh / self.rows
        # draw cells
        for row in range(0, self.rows):
            for col in range(0, self.cols):
                x = col * cell_width
                y = row * cell_height
                cell = self.get_cell(col, row)
                cell.draw(game, (x, y, cell_width, cell_height))
        # draw grid
        for row in range(1, self.rows):
            start = (0, row * wh / self.rows)
            end = (ww, row * wh / self.rows)
            pygame.draw.line(game.win, (200, 0, 0), start, end)
        for col in range(1, self.cols):
            start = (col * ww / self.cols, 0)
            end = (col * ww / self.cols, wh)
            pygame.draw.line(game.win, (200, 0, 0), start, end)

class MyGame:

    def __init__(self):
        self.grid = Grid(6, 6)
        self.collapse_timer = 0

    def update(self, delta):
        self.collapse_timer += delta
        if self.collapse_timer > 0.25:
            self.collapse_timer = 0
            self.grid.collapse_rand()

    def draw(self):
        self.win.fill((0, 0, 0))
        self.grid.draw(self)
        pass

    def click(self, pos):
        ww, wh = self.win.get_size()
        cell_width = ww / self.grid.cols
        cell_height = wh / self.grid.rows
        row = pos[1] // cell_height
        col = pos[0] // cell_width
        self.grid.collapse(col, row)

    def run(self):
        pygame.init()
        self.win = pygame.display.set_mode((640, 480))
        clock = pygame.time.Clock()
        running = True
        while running:
            delta = clock.tick(60) / 1000
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        running = False
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    if e.button == 1:
                        self.click(e.pos)
            self.update(delta)
            self.draw()
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    MyGame().run()