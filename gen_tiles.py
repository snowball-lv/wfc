#!/usr/bin/env python3

import sys
import pygame
import os
import shutil

def usage():
    print("./gen_tiles.py sample.png")

def surface_eq(a, b):
    for y in range(0, a.get_height()):
        for x in range(0, a.get_width()):
            if a.get_at((x, y)) != b.get_at((x, y)):
                return False
    return True

def in_list(lst, surface):
    for s in lst:
        if surface_eq(surface, s):
            return True
    return False

class Tile:
    def __init__(self, surface):
        self.surface = surface
    def __eq__(self, other):
        pass

def split_img(dir, img, dim):
    tiles = []
    w, h = img.get_size()
    print(f"{w} x {h}")
    for y in range(0, h, dim):
        for x in range(0, w, dim):
            sub = img.subsurface((x, y, dim, dim))
            # path = os.path.join(dir, f"{x}-{y}.png")
            # pygame.image.save(sub, path)
            if not in_list(tiles, sub):
                tiles.append(sub)
    print(len(tiles))

def main():
    img_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not img_path:
        usage()
        sys.exit("*** expected path to sample image")
    print(f"generating tiles for {img_path}")
    img = pygame.image.load(img_path)
    dir_name, _ = os.path.splitext(os.path.basename(img_path))
    print(dir_name)
    shutil.rmtree(dir_name)
    os.makedirs(dir_name, exist_ok=True)
    split_img(dir_name, img, 3)

if __name__ == "__main__":
    main()