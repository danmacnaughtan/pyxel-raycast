import math

from ctypes import CFUNCTYPE, POINTER, c_int32, c_uint32, pointer
import pyxel
from pyxel.core import _lib


INTERLEAVE_RENDERING = True

SCREEN_WIDTH = 240
SCREEN_HEIGHT = 136

MAP_WIDTH = 16
MAP_HEIGHT = 16

MOUSE_SPEED = 4


MAP_1 = """
################
#..............#
#..#....######.#
#..............#
#..............#
#......##......#
#......##......#
#..............#
###....#####...#
##.............#
#..............#
#........###.###
#........#.....#
#..............#
#........#.....#
################
"""


# ------------[ Exposing some C functions (SDL2) from Pyxel core ]-------------

# Pyxel doesn't provide a way to track arbitrary mouse movement, but we can
# access the C API to the underlying SDL2 framework and start using some
# relative mouse functions...


def _setup_api(name, restype, argtypes):
    api = globals()[name] = getattr(_lib, name)
    api.argtypes = argtypes
    api.restype = restype


_setup_api("SDL_SetRelativeMouseMode", c_int32, [c_int32])
_setup_api("SDL_GetRelativeMouseState", c_uint32, [POINTER(c_int32), POINTER(c_int32)])

# -----------------------------------------------------------------------------


class Game:
    def __init__(self):
        pyxel.init(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            caption="Raycasting in progress...",
            scale=4,
        )

        # Track the initial application setup
        self.has_setup = False
        # Player staring position and angle
        self.player_x = 7
        self.player_y = 12
        self.player_a = 4
        # Field of view
        self.fov = 3.14159 / 4
        # Maximum rendering depth
        self.depth = 16
        # Walking speed
        self.speed = 0.2
        # Load the world map
        self.world_map = MAP_1[1:-1].split("\n")

        self.tp1 = pyxel.frame_count
        self.tp2 = pyxel.frame_count
        self.interleave = INTERLEAVE_RENDERING
        self.render_alt = True
        self.player_run = True
        self.last_mouse_pos = (0, 0)
        self.mouse_vec = [0, 0]
        self.mouse_captured = False
        self.v_look = 0.1
        self.show_map = True
        self.show_boundries = True

    def run(self):
        pyxel.run(self.update, self.draw)

    def setup(self):
        """
        First time additional setup that needs to run after the app has been
        initialized.
        """
        # We will start the game with the mouse captured
        self.capture_mouse()
        # Setup complete
        self.has_setup = True

    def update(self):
        if not self.has_setup:
            self.setup()

        # Compute elapsed time
        self.tp2 = pyxel.frame_count
        ellapsed_time = self.tp2 - self.tp1
        self.tp1 = self.tp2

        # Handle player input
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

        # Determine player speed
        if pyxel.btnp(pyxel.KEY_SHIFT):
            self.player_run = False
        if pyxel.btnr(pyxel.KEY_SHIFT):
            self.player_run = True
        if self.player_run:
            speed = self.speed
        else:
            speed = self.speed / 3

        if pyxel.btn(pyxel.KEY_W):
            self.move_forward(speed, ellapsed_time)
        if pyxel.btn(pyxel.KEY_S):
            self.move_backward(speed, ellapsed_time)
        if pyxel.btn(pyxel.KEY_A):
            if self.mouse_captured:
                self.move_left(speed, ellapsed_time)
            else:
                self.player_a -= 0.05 * ellapsed_time
        if pyxel.btn(pyxel.KEY_D):
            if self.mouse_captured:
                self.move_right(speed, ellapsed_time)
            else:
                self.player_a += 0.05 * ellapsed_time

        if self.mouse_captured:
            if self.mouse_vec[0] != 0:
                self.player_a += self.mouse_vec[0] / 100 * ellapsed_time
                self.mouse_vec[0] = 0
            if self.mouse_vec[1] != 0:
                self.v_look -= self.mouse_vec[1] * ellapsed_time
                self.mouse_vec[1] = 0

        if pyxel.btnp(pyxel.KEY_P):
            print(f"x: {self.player_x}, ", end="")
            print(f"y: {self.player_y}, ", end="")
            print(f"a: {self.player_a}")

        if pyxel.btn(pyxel.KEY_1):
            self.fov += 0.01
        if pyxel.btn(pyxel.KEY_2):
            self.fov -= 0.01
        if pyxel.btn(pyxel.KEY_3):
            self.fov = 3.14159 / 4
        if pyxel.btnp(pyxel.KEY_4):
            self.interleave = not self.interleave
        if pyxel.btnp(pyxel.KEY_5):
            if self.mouse_captured:
                self.release_mouse()
            else:
                self.capture_mouse()
        if pyxel.btn(pyxel.KEY_6):
            self.depth += 1
        if pyxel.btn(pyxel.KEY_7):
            self.depth -= 1
        if pyxel.btn(pyxel.KEY_8):
            self.depth = 16
        if pyxel.btnp(pyxel.KEY_9):
            self.show_boundries = not self.show_boundries

        if pyxel.btn(pyxel.KEY_Q):
            self.v_look += 1
        if pyxel.btn(pyxel.KEY_E):
            self.v_look -= 1
        if pyxel.btn(pyxel.KEY_X):
            self.v_look = 0

        if pyxel.btnp(pyxel.KEY_M):
            self.show_map = not self.show_map

        if self.mouse_captured:
            self.update_mouse_pos()

    def draw(self):
        if self.interleave:
            inc = 2
            start = 0
            if self.render_alt:
                start = 1
            self.render_alt = not self.render_alt
        else:
            pyxel.cls(0)
            start = 0
            inc = 1

        for x in range(start, SCREEN_WIDTH, inc):
            # For each column, calculate the projected ray angle into world space
            ray_angle = (self.player_a - self.fov / 2) + (x / SCREEN_WIDTH) * self.fov

            dist_to_wall = 0
            hit_wall = False
            boundary = False

            eye_x = math.sin(ray_angle)
            eye_y = math.cos(ray_angle)

            while not hit_wall and dist_to_wall < self.depth:
                dist_to_wall += 0.1

                test_x = int(self.player_x + eye_x * dist_to_wall)
                test_y = int(self.player_y + eye_y * dist_to_wall)

                # Test if ray is out of bounds
                if (
                    test_x < 0
                    or test_x >= MAP_WIDTH
                    or test_y < 0
                    or test_y >= MAP_HEIGHT
                ):
                    hit_wall = True
                    dist_to_wall = self.depth
                else:
                    # Ray is inbounds so test to see if the ray cell is a wall
                    # block
                    if self.world_map[test_y][test_x] == "#":
                        hit_wall = True
                        # Cast rays from each corner of the wall to find the
                        # boundaries
                        p = []
                        for tx in range(2):
                            for ty in range(2):
                                vy = test_y + ty - self.player_y
                                vx = test_x + tx - self.player_x
                                d = math.sqrt(vx * vx + vy * vy)
                                dot = (eye_x * vx / d) + (eye_y * vy / d)
                                p.append((d, dot))
                        # Sort the pairs to find the closest
                        p.sort()
                        # Looking for very small angles with closest corners
                        bound = 0.01
                        if math.acos(p[0][1]) < bound:
                            boundary = True
                        if math.acos(p[1][1]) < bound:
                            boundary = True

            # Calculate distance to ceiling and floor
            ceiling = SCREEN_HEIGHT / 2 - SCREEN_HEIGHT / dist_to_wall
            floor = SCREEN_HEIGHT - ceiling
            # Modify the ceiling and floor for the vertical look position
            ceiling += self.v_look
            floor += self.v_look
            # Instead of drawing directly to the screen, I'm using one of the
            # image banks as a display buffer
            shade = 0
            for y in range(SCREEN_HEIGHT):
                if y < ceiling:
                    pyxel.image(1).set(x, y, 0)
                elif y > ceiling and y <= floor:
                    # Compute wall shading
                    if dist_to_wall <= self.depth / 7:
                        shade = 6
                    elif dist_to_wall < self.depth / 6:
                        if x % 2:
                            shade = 6 if y % 2 else 13
                        else:
                            shade = 13 if y % 2 else 6
                    elif dist_to_wall < self.depth / 5:
                        shade = 13
                    elif dist_to_wall < self.depth / 4:
                        if x % 2:
                            shade = 13 if y % 2 else 1
                        else:
                            shade = 1 if y % 2 else 13
                    elif dist_to_wall < self.depth / 3:
                        shade = 1
                    elif dist_to_wall < self.depth / 2:
                        if x % 2:
                            shade = 1 if y % 2 else 0
                        else:
                            shade = 0 if y % 2 else 1
                    elif dist_to_wall < self.depth:
                        shade = 0
                    # Change the shade of a wall block boundary
                    # Can help orient the play, since we have no textures
                    if self.show_boundries and boundary:
                        shade = 0
                    pyxel.image(1).set(x, y, shade)
                else:
                    # Compute floor shading
                    # v_look changes where the floor starts rendering
                    b = 1 - (y - self.v_look - SCREEN_HEIGHT / 2) / (SCREEN_HEIGHT / 2)
                    if b < 0.25:
                        shade = 14
                    elif b < 0.5:
                        if x % 2:
                            shade = 14 if y % 2 else 2
                        else:
                            shade = 2 if y % 2 else 14
                    elif b < 0.75:
                        shade = 2
                    elif b < 0.9:
                        if x % 2:
                            shade = 2 if y % 2 else 0
                        else:
                            shade = 0 if y % 2 else 2
                    else:
                        shade = 0
                    pyxel.image(1).set(x, y, shade)
        # Blt the screen from the image bank being used as the display buffer
        pyxel.blt(0, 0, 1, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        # Draw map
        if self.show_map:
            w = 2
            startx = 0
            starty = SCREEN_HEIGHT - MAP_WIDTH * w
            for nx in range(MAP_HEIGHT):
                for ny in range(MAP_WIDTH):
                    cell = self.world_map[ny][nx]
                    if cell == "#":
                        col = 6
                    else:
                        col = 7
                    pyxel.rect(w * nx + startx, w * ny + starty, w, w, col)
            px = int(self.player_x)
            py = int(self.player_y)
            pyxel.rect(w * px + startx, w * py + starty, w, w, 12)

    def move_forward(self, speed, time_delta):
        new_x = self.player_x + math.sin(self.player_a) * speed * time_delta
        new_y = self.player_y + math.cos(self.player_a) * speed * time_delta
        if not self.check_collision(new_x, new_y):
            self.player_x = new_x
            self.player_y = new_y

    def move_backward(self, speed, time_delta):
        new_x = self.player_x - math.sin(self.player_a) * speed * time_delta
        new_y = self.player_y - math.cos(self.player_a) * speed * time_delta
        if not self.check_collision(new_x, new_y):
            self.player_x = new_x
            self.player_y = new_y

    def move_left(self, speed, time_delta):
        new_x = (
            self.player_x + math.sin(self.player_a - math.pi / 2) * speed * time_delta
        )
        new_y = (
            self.player_y + math.cos(self.player_a - math.pi / 2) * speed * time_delta
        )
        if not self.check_collision(new_x, new_y):
            self.player_x = new_x
            self.player_y = new_y

    def move_right(self, speed, time_delta):
        new_x = (
            self.player_x + math.sin(self.player_a + math.pi / 2) * speed * time_delta
        )
        new_y = (
            self.player_y + math.cos(self.player_a + math.pi / 2) * speed * time_delta
        )
        if not self.check_collision(new_x, new_y):
            self.player_x = new_x
            self.player_y = new_y

    def check_collision(self, x, y):
        return self.world_map[int(y)][int(x)] == "#"

    def capture_mouse(self):
        SDL_SetRelativeMouseMode(1)
        self.mouse_captured = True

    def release_mouse(self):
        SDL_SetRelativeMouseMode(0)
        self.mouse_captured = False

    def update_mouse_pos(self):
        xpos = c_int32(0)
        ypos = c_int32(0)
        SDL_GetRelativeMouseState(pointer(xpos), pointer(ypos))
        delta = (xpos.value, ypos.value)
        self.mouse_vec = [
            self.last_mouse_pos[0] + delta[0] / MOUSE_SPEED,
            self.last_mouse_pos[1] + delta[1] / MOUSE_SPEED,
        ]
        self.last_mouse_pos = self.mouse_vec


if __name__ == "__main__":
    game = Game()
    game.run()
