#!/usr/bin/env python3

import sys
import pygame
import json
import os
import math
import random
import numpy

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

class Interpolator:

    def __init__(self):
        self.restart(0, 0)

    def restart(self, a, b, duration = 2.0):
        self.a = a
        self.b = b
        self.value = a
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.done = False

    def get_delta(self):
        now = pygame.time.get_ticks()
        return (now - self.start_time) / 1000

    def update(self):
        progress = self.get_delta() / self.duration
        if progress > 1:
            self.value = self.b
            self.done = True
            return
        mul = (1 - math.cos(math.pi * progress)) / 2
        self.value = self.a + mul * (self.b - self.a)



class Grid:

    def __init__(self, game):
        self.game = game
        self.width = 10
        self.height = 1
        self.timer = pygame.time.get_ticks()
        self.rows = []
        self.dy = 0
        self.search_speed = 100
        self.num_rows = 0
        self.backtracking_level = 0
        self.graying_start_time = 0
        self.graying_end_time = 0
        self.interp = Interpolator()
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
        # for tile in self.tile_desc["tiles"]:
        #     img_path = os.path.join(game.tile_dir, tile["image"])
        #     self.atlas.append(pygame.image.load(img_path))
        self.img_hq = pygame.image.load("scarf-hq.png")
        for tile in self.tile_desc["tiles"]:
            rect = (tile["x"] * 10, tile["y"] * 10, 3 * 10, 3 * 10)
            img = self.img_hq.subsurface(rect)
            self.atlas.append(img)

    def new_row(self):
        row = [Cell() for _ in range(self.width)]
        for cell in row:
            cell.domain = set(self.domain)
        return row

    def pad_rect(self, rect):
        return next((x + 20, y + 20, w - 40, h - 40) for x, y, w, h in [rect])

    def blend_images(self, imgs):
        # img = imgs[0].convert()
        # for i in range(1, len(imgs)):
        #     img.blit(imgs[i], (0, 0), special_flags = pygame.BLEND_RGB_MULT)
        # return img
        img = imgs[0].convert()
        alpha = 255 // len(imgs)
        for i in range(1, len(imgs)):
            cp = imgs[i].copy()
            cp.set_alpha(alpha)
            img.blit(cp, (0, 0))
        return img
        # alpha = 255 // len(imgs)
        # blended = None
        # for img in imgs:
        #     cp = img.copy()
        #     cp.set_alpha(alpha)
        #     if not blended:
        #         blended = cp
        #     else:
        #         blended.blit(img, (0, 0))
        # return blended

    def draw_label(self, x, y, bounds):
        # bounds = self.pad_rect(bounds)
        cell = self.rows[y][x]
        font = self.game.font
        dim = math.ceil(math.sqrt(len(cell.domain)))
        if dim == 0:
            return
        # blended image
        images = [self.atlas[i] for i in cell.domain]
        img = self.blend_images(images)
        img = pygame.transform.scale(img, bounds[2:4])
        # # cardinality
        # font_surface = font.render(str(len(cell.domain)), True, (255, 0, 255))
        # img.blit(font_surface, (0, 0))
        # if len(cell.domain) == 1:
        #     value = list(cell.domain)[0]
        #     font_surface = font.render(str(value), True, (255, 0, 255))
        #     img.blit(font_surface, (0, 0))
        self.game.win.blit(img, bounds[:2])
        # lsize = bounds[2] / dim
        # for i, v in enumerate(cell.domain):
        #     lx = bounds[0] + (i % dim) * lsize
        #     ly = bounds[1] + (i // dim) * lsize
        #     # text label
        #     # label = str(v)
        #     # font_surface = font.render(label, True, (230, 230, 230))
        #     # self.game.win.blit(font_surface, (lx, ly))
        #     # img label
        #     img = self.atlas[v]
        #     # img = pygame.transform.scale(img, (lsize - 8, lsize - 8))
        #     # self.game.win.blit(img, (lx + 4, ly + 4))
        #     img = pygame.transform.scale(img, (lsize - 4, lsize - 4))
        #     self.game.win.blit(img, (lx + 2, ly + 2))

    def draw_cell(self, x, y):
        cell = self.rows[y][x]
        win_width, win_height = pygame.display.get_surface().get_size()
        size = win_width / self.width
        abs_x = x * size
        abs_y = win_height - (y + 1) * size + self.dy
        rect = (abs_x, abs_y, size, size)
        # pygame.draw.rect(self.game.win, (200, 0, 0), rect)
        self.draw_label(x, y, rect)

    def draw(self):
        win_width, win_height = pygame.display.get_surface().get_size()
        size = win_width / self.width
        top = win_height - (self.height) * size + self.dy
        if top < 150 and self.interp.done:
            self.interp.restart(self.dy, self.dy + abs(top) + 50)
        first_y = math.floor(self.dy / size)
        # print(f"first y {first_y}")
        for y in range(first_y, self.height):
            for x in range(0, self.width):
                self.draw_cell(x, y)

    def pick_cell(self):
        cells = []
        for y in range(self.height):
            for x in range(self.width):
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
    
    def get_constraint(self, tile_num, name):
        return set(self.tile_desc["tiles"][tile_num]["constraints"][name])

    def propagate_v2(self):
        changed = False
        for y in range(self.height):
            for x in range(self.width):
                cell = self.rows[y][x]
                if cell.is_collapsed() or not cell.is_valid():
                    continue
                old_size = len(cell.domain)
                domain = set(self.domain)
                if x > 0:
                    left_cell = self.rows[y][x - 1]
                    right = set()
                    for v in left_cell.domain:
                        right = right.union(self.get_constraint(v, "right"))
                    domain = domain.intersection(right)
                if x < self.width - 1:
                    right_cell = self.rows[y][x + 1]
                    left = set()
                    for v in right_cell.domain:
                        left = left.union(self.get_constraint(v, "left"))
                    domain = domain.intersection(left)
                if y > 0:
                    down_cell = self.rows[y - 1][x]
                    up = set()
                    for v in down_cell.domain:
                        up = up.union(self.get_constraint(v, "up"))
                    domain = domain.intersection(up)
                if y < self.height - 1:
                    up_cell = self.rows[y + 1][x]
                    down = set()
                    for v in up_cell.domain:
                        down = down.union(self.get_constraint(v, "down"))
                    domain = domain.intersection(down)
                cell.domain = domain
                if old_size != len(domain):
                    changed = True
        if changed:
            self.propagate_v2()

    def propagate(self):
        self.propagate_v2()
        return
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
            last_row = self.rows[-1]
            for cell in last_row:
                if not cell.is_valid():
                    print("retrying last row!")
                    if self.num_rows == len(self.rows) and self.backtracking_level < 3:
                        print("row failed twice, backtracking!")
                        self.rows.pop()
                        self.height -= 1
                        if self.backtracking_level == 0:
                            self.graying_start_time = pygame.time.get_ticks()
                        self.backtracking_level += 1
                    self.num_rows = len(self.rows)
                    self.rows[-1] = self.new_row()
                    return
            if self.backtracking_level == 1:
                self.graying_end_time = pygame.time.get_ticks()
            self.backtracking_level = max(self.backtracking_level - 1, 0)
            self.rows.append(self.new_row())
            self.height += 1
            self.propagate()
            return
        v = random.choice(list(cell.domain))
        # print(f"collapsing {x}, {y}, ({len(cell.domain)}) to {v}")
        cell.domain = set([v])
        self.propagate()

    def update(self, delta):
        self.interp.update()
        self.dy = self.interp.value
        now = pygame.time.get_ticks()
        if now - self.timer > self.search_speed:
            self.collapse()
            # process = psutil.Process()
            # print(f"{process.memory_info().rss / 1000000} MB")
            self.timer = pygame.time.get_ticks()

class MyGame:

    def __init__(self, tile_dir):
        self.tile_dir = tile_dir
        self.pause = False

    def draw(self, delta):
        self.win.fill((20, 20, 20))
        self.grid.draw()

    def collapse(self):
        self.grid.collapse()

    def update(self, delta):
        self.grid.update(delta)

    # https://stackoverflow.com/a/65919555
    def convert_to_grayscale(self, surface: pygame.Surface):
        arr = pygame.surfarray.pixels3d(surface)
        mean_arr = numpy.dot(arr[:,:,:], [0.216, 0.587, 0.144])
        mean_arr3d = mean_arr[..., numpy.newaxis]
        new_arr = numpy.repeat(mean_arr3d[:, :, :], 3, axis=2)
        return pygame.surfarray.make_surface(new_arr)

    def run(self):
        pygame.init()
        self.win = pygame.display.set_mode((400, 733))
        self.font = pygame.font.Font(None, 24)
        clock = pygame.time.Clock()
        running = True
        self.grid = Grid(self)
        self.grayscale = False
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
                    elif e.key == pygame.K_p:
                        self.pause = not self.pause
                    elif e.key == pygame.K_r:
                        self.grid = Grid(self)
                    elif e.key == pygame.K_g:
                        self.grayscale = not self.grayscale
            if not self.pause:
                self.update(delta)
                self.draw(delta)
            if self.grid.backtracking_level > 0:
                delta = pygame.time.get_ticks() - self.grid.graying_start_time
                f = min(delta / 3000, 1.0)
                gray = self.convert_to_grayscale(self.win)
                a = pygame.surfarray.array3d(self.win)
                b = pygame.surfarray.array3d(gray)
                fade = a * (1 - f) + b * f
                self.win.blit(pygame.surfarray.make_surface(fade), (0, 0))
            else:
                delta = pygame.time.get_ticks() - self.grid.graying_end_time
                f = min(delta / 1000, 1.0)
                if f < 1.0:
                    gray = self.convert_to_grayscale(self.win)
                    a = pygame.surfarray.array3d(self.win)
                    b = pygame.surfarray.array3d(gray)
                    fade = a * f + b * (1 - f)
                    self.win.blit(pygame.surfarray.make_surface(fade), (0, 0))
            if self.grayscale:
                # img_array = pygame.surfarray.array3d(self.win.convert())
                # gray = numpy.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
                gray = self.convert_to_grayscale(self.win)
                self.win.blit(gray, (0, 0))
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
