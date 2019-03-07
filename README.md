# Pyxel-raycast

![example](example.gif)

A basic raycast example using the [Pyxel](https://github.com/kitao/pyxel) retro game engine. The project started as an experiement porting the [OneLoneCoder CommandLineFPS](https://github.com/OneLoneCoder/CommandLineFPS) (see [video tutorial here](https://www.youtube.com/watch?v=xW8skO7MFYw)) to Python and Pyxel, but went a bit farther with some dithering and mouse camera control (including "vertical" looking).

A resolution of 240x136 and framerate of a whopping 30fps was achieved using two techniques:
1. Interleave rendering (alternating drawing even and odd columns)
2. Using one of Pyxel's image banks as a display buffer so the scene can be rendered with a single draw command (and incidently overcoming Pyxel's internally imposed draw count limit `DRAW_MAX_COUNT = 10000`)

I learned some additional tips, specifically "vertical" look, from https://permadi.com/1996/05/ray-casting-tutorial-1/

### Requirements

- Python 3.7+
- See _requirements.txt_

### Controls

- `1` >> Reduce FOV
- `2` >> Increase FOV
- `3` >> Reset FOV
- `4` >> Toggle interleave rendering on/off (default on)
- `5` >> Toggle mouse capture on/off (default on)
- `6` >> Increase visible distance
- `7` >> Reduce visible distance
- `8` >> Reset visible distance
- `9` >> Toggle wall boundries on/off (default on)
- `W` >> Move forward
- `A` >> Strafe left (or turn left if mouse capture is off)
- `S` >> Move backward
- `D` >> Strafe right (or turn right if mouse capture is off)
- `Q` >> Look up
- `E` >> Look down
- `x` >> Center look
- `SHIFT` >> Hold to walk instead of run
- `MOUSE` >> Camera control (if mouse capture is on)
