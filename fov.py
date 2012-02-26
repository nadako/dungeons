import libtcodpy as tcod

from shadowcaster import ShadowCaster

dungeon = [
    "###########################################################",
    "#...........#.............................................#",
    "#...........#........#....................................#",
    "#.....................#...................................#",
    "#....####..............#..................................#",
    "#.......#.......................#####################.....#",
    "#.......#...........................................#.....#",
    "#.......#...........##..............................#.....#",
    "#####........#......##..........##################..#.....#",
    "#...#...........................#................#..#.....#",
    "#...#............#..............#................#..#.....#",
    "#...............................#..###############..#.....#",
    "#...............................#...................#.....#",
    "#...............................#...................#.....#",
    "#...............................#####################.....#",
    "#.........................................................#",
    "#.........................................................#",
    "###########################################################"
]
width = len(dungeon[0])
height = len(dungeon)
light_flag = 0
light = [[light_flag for x in xrange(width)] for y in xrange(height)]
fov_radius = 10
x, y = 36, 13
dark, lit = tcod.dark_blue, tcod.white

def is_blocked(x, y):
    return x < 0 or y < 0 or x >= width or y >= height or dungeon[y][x] == "#"

def do_light(x, y):
    light[y][x] = light_flag

caster = ShadowCaster(is_blocked, do_light)

tcod.console_init_root(80, 80, 'FOV', renderer=tcod.RENDERER_SDL)

while not tcod.console_is_window_closed():
    light_flag += 1
    caster.calculate_light(x, y, fov_radius)

    tcod.console_clear(0)

    for mx in xrange(width):
        for my in xrange(height):
            if mx == x and my == y:
                ch = '@'
                col = lit
            else:
                ch = dungeon[my][mx]
                col = (light[my][mx] == light_flag) and lit or dark

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
