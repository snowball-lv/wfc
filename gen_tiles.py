#!/usr/bin/env python3

import sys
import pygame
import os
import shutil
import json

def usage():
    print("Usage: ./gen_tiles.py image.png tile-size")
    print(" " * 4, "-h print this message and exit")

class Tile:

    def __init__(self, img):
        self.img = img
        self.left = set()
        self.right = set()
        self.up = set()
        self.down = set()

    def cmp_img(self, img):
        width, height = self.img.get_size()
        for y in range(height):
            for x in range(width):
                if self.img.get_at((x, y)) != img.get_at((x, y)):
                    return False
        return True

class App:

    def __init__(self, img_path, tile_size = 3):
        self.img_path = img_path
        self.tile_size = tile_size
        self.tiles = []

    def get_dir(self):
        dir, _ = os.path.splitext(os.path.basename(self.img_path))
        return dir
    
    def find_tile(self, img):
        for i, tile in enumerate(self.tiles):
            if tile.cmp_img(img):
                return (i, tile)
        return (0, None)
    
    def get_tile(self, x, y):
        img = self.img.subsurface(x, y, self.tile_size, self.tile_size)
        i, tile = self.find_tile(img)
        if tile:
            return i, tile
        else:
            tile = Tile(img)
            self.tiles.append(tile)
            return len(self.tiles) - 1, tile

    def gen_tiles(self):
        img_width, img_height = self.img.get_size()
        print(f"Size {img_width}x{img_height}")
        for y in range(0, img_height - self.tile_size, self.tile_size):
            for x in range(0, img_width - self.tile_size, self.tile_size):
        # for y in range(0, img_height - self.tile_size):
        #     for x in range(0, img_width - self.tile_size):
                i, tile = self.get_tile(x, y)
                if x >= self.tile_size:
                    li, left = self.get_tile(x - self.tile_size, y)
                    tile.left.add(li)
                    left.right.add(i)
                if x <= img_width - 2 * self.tile_size:
                    ri, right = self.get_tile(x + self.tile_size, y)
                    tile.right.add(ri)
                    right.left.add(i)
                if y >= self.tile_size:
                    ui, up = self.get_tile(x, y - self.tile_size)
                    tile.up.add(ui)
                    up.down.add(i)
                if y <= img_height - 2 * self.tile_size:
                    di, down = self.get_tile(x, y + self.tile_size)
                    tile.down.add(di)
                    down.up.add(i)

        print(f"Made {len(self.tiles)} tiles")
        self.save()

    def save(self):
        tiles = []
        for i, tile in enumerate(self.tiles):
            info = {
                "image": f"{i}.png",
                "constraints": {
                    "left": list(tile.left),
                    "right": list(tile.right),
                    "up": list(tile.up),
                    "down": list(tile.down)
                }
            }
            tiles.append(info)
            img_path = os.path.join(self.get_dir(), info["image"])
            pygame.image.save(tile.img, img_path)
        json_path = os.path.join(self.get_dir(), "tiles.json")
        with open(json_path, "w") as file:
            json.dump({"tiles":tiles}, file, indent = 4)

    def run(self):
        print(f"Image {self.img_path}")
        print(f"Tile size {self.tile_size}x{self.tile_size}")
        self.img = pygame.image.load(self.img_path)
        shutil.rmtree(self.get_dir(), True)
        os.makedirs(self.get_dir(), exist_ok=True)
        self.gen_tiles()

def main():
    pygame.init()
    img_path = sys.argv[1] if len(sys.argv) > 1 else None
    tile_size = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    if not img_path:
        usage()
        sys.exit("*** expected path to image")
    App(img_path, tile_size).run()
    pygame.quit()

if __name__ == "__main__":
    main()