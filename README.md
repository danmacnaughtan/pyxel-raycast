# Pyxel Raycast

![example](example.gif)

A basic raycast example using the [Pyxel](https://github.com/kitao/pyxel) retro game engine. The
project started as an experiment porting the [OneLoneCoder
CommandLineFPS](https://github.com/OneLoneCoder/CommandLineFPS) (see [video tutorial
here](https://www.youtube.com/watch?v=xW8skO7MFYw)) to Python and Pyxel, but went a bit farther
with some dithering and camera control (including "vertical" looking).

A resolution of 240x136 and framerate of a whopping 30fps was achieved using two techniques:
1. Interleave rendering (alternate drawing even and odd columns)
2. Using one of Pyxel's image banks as a display buffer so the scene can be rendered with a single
   draw command

Some additional tips, specifically "vertical" look, can be found in this
[article](https://permadi.com/1996/05/ray-casting-tutorial-1/).

### Requirements

- Python 3.7+
- See [requirements.txt](requirements.txt)

### Controls

| Key | Description |
|:---:|-------------|
| `1` | Reduce FOV |
| `2` | Increase FOV |
| `3` | Reset FOV |
| `4` | Toggle interleave rendering on/off (default on) |
| `5` | Increase visible distance |
| `6` | Reduce visible distance |
| `7` | Reset visible distance |
| `8` | Toggle wall boundaries on/off (default on) |
| `W` | Move forward |
| `A` | Turn left |
| `S` | Move backward |
| `D` | Turn right |
| `Z` | Strafe left |
| `C` | Strafe right |
| `Q` | Look up |
| `E` | Look down |
| `X` | Center look |
| `SHIFT` | Hold to run |
