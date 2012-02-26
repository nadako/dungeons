import libtcodpy as tcod

from shadowcaster import ShadowCaster
from generator import DungeonGenerator

dungeon = DungeonGenerator(size=(80, 80), max_rooms=100, min_room_size=(5, 5), max_room_size=(10, 10))
dungeon.generate()

fov_radius = 10
dark, lit = tcod.darkest_gray, tcod.yellow
x, y = dungeon.size.x / 2, dungeon.size.y / 2

def is_blocked_cb(x, y):
    return x < 0 or y < 0 or x >= dungeon.size.x or y >= dungeon.size.y or dungeon.grid[y][x] == "#"

def light_cb(x, y, intensity):
    global light
    light[y][x] = intensity

caster = ShadowCaster(is_blocked_cb, light_cb)

def recompute_light():
    global x, y, light
    light = [[0 for i in xrange(dungeon.size.x)] for j in xrange(dungeon.size.y)]
    caster.calculate_light(x, y, fov_radius)

def lerp(a, b, t):
    return a + (b - a) * t

def get_light_color(intensity):
    return tcod.Color(
        int(lerp(dark.r, lit.r, intensity)),
        int(lerp(dark.g, lit.g, intensity)),
        int(lerp(dark.b, lit.b, intensity)))


tcod.console_init_root(dungeon.size.x, dungeon.size.y, 'FOV')

while not tcod.console_is_window_closed():
    global light
    recompute_light()

    tcod.console_clear(0)

    for mx in xrange(dungeon.size.x):
        for my in xrange(dungeon.size.y):
            if mx == x and my == y:
                ch = '@'
                col = lit
            else:
                ch = dungeon.grid[my][mx]
                col = get_light_color(light[my][mx])

            tcod.console_set_default_foreground(0, col)
            tcod.console_put_char(0, mx, my, ch)

    tcod.console_flush()

    key = tcod.console_wait_for_keypress(True)
    if key.vk == tcod.KEY_ESCAPE:
        break
    elif key.vk == tcod.KEY_KP8:
        y -= 1
    elif key.vk == tcod.KEY_KP2:
        y += 1
    elif key.vk == tcod.KEY_KP4:
        x -= 1
    elif key.vk == tcod.KEY_KP6:
        x += 1
