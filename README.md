A WFC implementation in pygame for a school project. I'll fill the readme out properly when I'm not in a rush to finish this anymore.

## Description

It contains 2 important scripts: `gen_tiles.py` which generates a tile set from a supplied image and `wfc.py` which will render the generated tile set.

## Usage

```
./gen_tiles.py your_image.png [tile_size]
```

Creates a directory called `your_image` containing the generated tiles as well as a `.json` file describing adjacency constraints. `tile_size` is optional and default to 3 (i.e. 3x3 pixel tiles).

```
./wfc.py your_image
```

Pass the directory name generated in the previous step to `./wfc.py` to run your WFC live in a pygame window.

## Demonstration

It's for a school project, hence the specific bottom-up order.

![](./demo.gif)
