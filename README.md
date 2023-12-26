A WFC implementation in pygame for a university exhibit.  
I'll see if I can clean it up and make it more general purpose.

## Description

It contains 2 scripts: 

- `gen_tiles.py` - generates a tile set from a supplied image
- `wfc.py` - renders the generated tile set

Make sure your source pattern is small and pixelated.

## Usage

```
./gen_tiles.py your_image.png [tile_size]
```

Creates a directory called `your_image` containing the generated tiles as well as a `.json` file describing adjacency constraints. `tile_size` is optional and defaults to 3 (i.e. 3x3 pixel tiles).

```
./wfc.py your_image
```

Pass the directory name generated in the previous step to `./wfc.py` to run your WFC live in a pygame window.

## Demonstration

It's for a school project, hence the specific bottom-up order.

### Source pattern, 69 x 69 pixels:  
![](./scarf.png)

### Live render:

![](./demo.gif)
