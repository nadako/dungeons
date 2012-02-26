class ShadowCaster(object):
    """
    Recursive shadow casting algorithm implementation

    This class is made as pluggable as possible, so it
    doesn't handle any data management itself. To use it,
    you need to pass two callbacks in its constructor:

    is_blocking_cb(x, y) - function that returns whether
    the cell is blocking view.

    light_cb(x, y, intensity) - function that is called when cell
    is lit. intensity is a float value within range 0..1, where
    1 means fully lit cell and 0 is no light. Keep in mind though
    that this callback won't be called for any cells not in sight.

    Then, just call the calculate_light(x, y, radius).
    It will invoke callback functions you passed in
    constructor.

    You can also override the calculate_intensity method to
    change the light intensity calculation formula. The default
    method is very fast, but not so good-looking linear attenuation.
    See http://doryen.eptalys.net/articles/lights-in-full-color-roguelikes/
    for more examples. Hint: if you don't want intensity to be
    calculated at all, replace this method with "return 1" to get
    always full-lit cells.
    """

    # coordinate multipliers for different octants
    mult = [
        [1,  0,  0, -1, -1,  0,  0,  1],
        [0,  1, -1,  0,  0, -1,  1,  0],
        [0,  1,  1,  0,  0, -1, -1,  0],
        [1,  0,  0,  1, -1,  0,  0, -1]
    ]

    def __init__(self, is_blocking_cb, light_cb):
        self.is_blocking_cb = is_blocking_cb
        self.light_cb = light_cb

    def calculate_light(self, x, y, radius):
        # call recursive checking for each octant
        for oct in xrange(8):
            self._cast_light(x, y, 1, 1.0, 0.0, radius, radius * radius,
                self.mult[0][oct], self.mult[1][oct],
                self.mult[2][oct], self.mult[3][oct])

    def _cast_light(self, cx, cy, row, start_slope, end_slope, radius, radius_squared, xx, xy, yx, yy):
        if start_slope < end_slope:
            return

        # for each row in radius...
        for j in xrange(row, radius + 1):
            # starting scan coords
            dx = -j - 1 # -1 here, because we increase dx before doing anything else
            dy = -j

            # blocked flag (setting to true when got blocking cell)
            blocked = False

            while dx <= 0:
                dx += 1

                l_slope = (dx - 0.5) / (dy + 0.5) # slope to bottom-right of the cell
                r_slope = (dx + 0.5) / (dy - 0.5) # slope to top-left of the cell

                # we're not interested in cells on the other sides of slope
                if start_slope < r_slope:
                    continue
                elif end_slope > l_slope:
                    break

                # translate the dx, dy coordinates into map coordinates
                map_x = cx + dx * xx + dy * xy
                map_y = cy + dx * yx + dy * yy

                # calculate squared distantion from light position
                dist_squared = dx * dx + dy * dy

                # our light beam is touching this square, so light it
                if dist_squared < radius_squared:
                    intensity = self.calculate_intensity(dist_squared, radius_squared)
                    self.light_cb(map_x, map_y, intensity)

                # if previous cell was blocking, we're scanning a section of blocking cells
                if blocked:
                    # if it's still blocking, store the new slope and skip cycle
                    if self.is_blocking_cb(map_x, map_y):
                        new_start_slope = r_slope
                        continue
                    # if it's not blocking, set the start slope to last blocking one
                    else:
                        blocked = False
                        start_slope = new_start_slope

                # if previous cell was not blocking, check current
                else:
                    if j < radius and self.is_blocking_cb(map_x, map_y):
                        # this is a blocking square, start a child scan
                        blocked = True
                        self._cast_light(cx, cy, j + 1, start_slope, l_slope,
                            radius, radius_squared, xx, xy, yx, yy)
                        new_start_slope = r_slope

            # if final cell was blocking, we don't need to scan next row,
            # because we created recursive scanners for further work
            if blocked:
                break

    def calculate_intensity(self, dist_squared, radius_squared):
        return 1.0 - float(dist_squared) / float(radius_squared)
