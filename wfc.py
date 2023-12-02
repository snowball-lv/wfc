#!/usr/bin/env python3

import sys
import pygame
import json
import os
import math
import random

def usage():
    print("Usage: ./wfc.py path_to_tile_dir")
    print(" " * 4, "-h print this message and exit")

class Cell:

    def __init__(self):
        self.domain = set()

    def is_collapsed(self):
        return len(self.domain) <= 1
    
    def is_valid(self):
        return len(self.domain) > 0

class Grid:

    def __init__(self, game):
        self.game = game
        self.width = 4
        self.height = 4
        self.rows = []
        for _ in range(self.height):
            self.rows.append([Cell() for _ in range(self.width)])
        desc_path = os.path.join(game.tile_dir, "tiles.json")
        with open(desc_path) as file:
            self.tile_desc = json.load(file)
        self.domain = set(range(len(self.tile_desc["tiles"])))
        for row in self.rows:
            for cell in row:
                cell.domain = set(self.domain)
        self.atlas = []
        for tile in self.tile_desc["tiles"]:
            img_path = os.path.join(game.tile_dir, tile["image"])
            self.atlas.append(pygame.image.load(img_path))

    def pad_rect(self, rect):
        return next((x + 20, y + 20, w - 40, h - 40) for x, y, w, h in [rect])

    def blend_images(self, imgs):
        alpha = 255 // len(imgs)
        blended = None
        for img in imgs:
            cp = img.copy()
            cp.set_alpha(alpha)
            if not blended:
                blended = cp
            else:
                blended.blit(img, (0, 0))
        return blended

    def draw_label(self, x, y, bounds):
        bounds = self.pad_rect(bounds)
        cell = self.rows[y][x]
        font = self.game.font
        dim = math.ceil(math.sqrt(len(cell.domain)))
        if dim == 0:
            return
        # blended image
        images = [self.atlas[i] for i in cell.domain]
        img = self.blend_images(images)
        img = pygame.transform.scale(img, bounds[2:4])
        self.game.win.blit(img, bounds[:2])
        return
        lsize = bounds[2] / dim
        for i, v in enumerate(cell.domain):
            lx = bounds[0] + (i % dim) * lsize
            ly = bounds[1] + (i // dim) * lsize
            # text label
            # label = str(v)
            # font_surface = font.render(label, True, (230, 230, 230))
            # self.game.win.blit(font_surface, (lx, ly))
            # img label
            img = self.atlas[v]
            # img = pygame.transform.scale(img, (lsize - 8, lsize - 8))
            # self.game.win.blit(img, (lx + 4, ly + 4))
            img = pygame.transform.scale(img, (lsize - 4, lsize - 4))
            self.game.win.blit(img, (lx + 2, ly + 2))

    def draw_cell(self, x, y):
        cell = self.rows[y][x]
        win_width, win_height = pygame.display.get_surface().get_size()
        size = win_width / self.width
        abs_x = x * size
        abs_y = win_height - (y + 1) * size
        rect = (abs_x, abs_y, size, size)
        pygame.draw.rect(self.game.win, (200, 0, 0), rect)
        self.draw_label(x, y, rect)

    def draw(self):
        for y in range(self.height):
            for x in range(self.width):
                self.draw_cell(x, y)

    def pick_cell(self):
        cells = []
        for y in range(self.height):
            for x in range(self.height):
                cell = self.rows[y][x]
                if cell.is_collapsed():
                    continue
                cells.append((x, y, cell))
        if len(cells) == 0:
            return (0, 0, None)
        lowest = min([len(cell.domain) for (x, y, cell) in cells])
        cells = [(x, y, cell) for (x, y, cell) in cells
                 if len(cell.domain) == lowest]
        return random.choice(cells)
    
    def propagate(self):
        todo = []
        for y in range(self.height):
            for x in range(self.width):
                cell = self.rows[y][x]
                if cell.is_collapsed() and cell.is_valid():
                    todo.append((x, y, cell))
        for x, y, cell in todo:
            value = list(cell.domain)[0]
            tile_info = self.tile_desc["tiles"][value]
            constraints = tile_info["constraints"]
            left = set(constraints["left"])
            right = set(constraints["right"])
            up = set(constraints["up"])
            down = set(constraints["down"])
            changed = False
            if x > 0:
                left_cell = self.rows[y][x - 1]
                old_size = len(left_cell.domain)
                left_cell.domain = left_cell.domain.intersection(left)
                if old_size != len(left_cell.domain):
                    self.propagate()
                    return
            if x < self.width - 1:
                right_cell = self.rows[y][x + 1]
                old_size = len(right_cell.domain)
                right_cell.domain = right_cell.domain.intersection(right)
                if old_size != len(right_cell.domain):
                    self.propagate()
                    return
            if y < self.height - 1:
                up_cell = self.rows[y + 1][x]
                old_size = len(up_cell.domain)
                up_cell.domain = up_cell.domain.intersection(up)
                if old_size != len(up_cell.domain):
                    self.propagate()
                    return
            if y > 0:
                down_cell = self.rows[y - 1][x]
                old_size = len(down_cell.domain)
                down_cell.domain = down_cell.domain.intersection(down)
                if old_size != len(down_cell.domain):
                    self.propagate()
                    return
    
    def collapse(self):
        x, y, cell = self.pick_cell()
        if not cell:
            print("nothing to collapse!")
            return
        v = random.choice(list(cell.domain))
        print(f"collapsing {x}, {y}, ({len(cell.domain)}) to {v}")
        cell.domain = set([v])
        self.propagate()

class MyGame:

    def __init__(self, tile_dir):
        self.tile_dir = tile_dir

    def draw(self, delta):
        self.win.fill((20, 20, 20))
        self.grid.draw()

    def collapse(self):
        self.grid.collapse()

    def run(self):
        pygame.init()
        self.win = pygame.display.set_mode((400, 800))
        self.font = pygame.font.Font(None, 24)
        clock = pygame.time.Clock()
        running = True
        self.grid = Grid(self)
        while running:
            delta = clock.tick(60) / 1000
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        running = False
                    elif e.key == pygame.K_SPACE:
                        self.collapse()
            self.draw(delta)
            pygame.display.flip()
        pygame.quit()

def main():
    tile_dir = sys.argv[1] if len(sys.argv) > 1 else None
    if not tile_dir or "-h" in sys.argv:
        usage()
        sys.exit("*** path to tile directory not specified")
    print(f"Tile directory {tile_dir}")
    game = MyGame(tile_dir)
    game.run()

if __name__ == "__main__":
    main()
