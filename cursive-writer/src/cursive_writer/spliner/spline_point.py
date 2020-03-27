class SPoint:
    def __init__(self, x, y, ori_deg):
        """Create a spline point

        point (x,y) with orientation yp in degrees, ranging [-180, 180]
        """
        self.x = x
        self.y = y

        # save orientation in [-180, 180) range
        if ori_deg > 180:
            ori_deg -= 360
        if ori_deg <= -180:
            ori_deg += 360
        self.ori_deg = ori_deg
        # convert it to radians
        self.ori_rad = radians(self.ori_deg)
        # convert to slope of a line
        self.ori_slo = tan(self.ori_rad)

    def __add__(self, other):
        """Add two points, sum orientations as well
        """
        r_x = self.x + other.x
        r_y = self.y + other.y
        r_ori = self.ori_deg + other.ori_deg
        result = SPoint(r_x, r_y, r_ori)
        return result

    def __sub__(self, other):
        """Subtract two points, sub orientations as well
        """
        r_x = self.x - other.x
        r_y = self.y - other.y
        r_ori = self.ori_deg - other.ori_deg
        result = SPoint(r_x, r_y, r_ori)
        return result

    def __repr__(self):
        the_repr_str = ""
        the_repr_str += f"({self.x:.4f}, {self.y:.4f})"
        the_repr_str += f" # {self.ori_deg:.4f}"
        return the_repr_str
