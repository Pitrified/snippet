from math import tan
from math import radians
from math import isclose

from typing import List


class OrientedPoint(object):
    def __init__(self, x: float, y: float, ori_deg: float) -> None:
        """Create a point with orientation

        point (x,y) with orientation in degrees, ranging [-180, 180)
        """
        self.x = x
        self.y = y
        self.set_ori_deg(ori_deg)

    def translate(self, dx: float, dy: float) -> None:
        """
        """
        self.x += dx
        self.y += dy

    def rotate(self, dt: float) -> None:
        """Rotate this point of dt degrees and validate the orientation
        """
        ori_deg = self.ori_deg + dt
        self.set_ori_deg(ori_deg)

    def set_ori_deg(self, ori_deg: float) -> None:
        """Set the orientation of the points in degrees

        Updates the orientation in radians and slope as well
        """
        # save orientation in [-180, 180) range
        if ori_deg > 180:
            ori_deg -= 360
        if ori_deg <= -180:
            ori_deg += 360

        self.ori_deg = ori_deg
        # convert it to radians
        self.ori_rad: float = radians(self.ori_deg)
        # convert to slope of a line
        self.ori_slo: float = tan(self.ori_rad)

    def to_ab_line(self) -> List[float]:
        """Return the ax+b coeff of the line passing through this point
        """
        a = self.ori_slo
        b = self.y - a * self.x
        return [a, b]

    def __add__(self, other):
        """Add two points, sum orientations as well
        """
        r_x = self.x + other.x
        r_y = self.y + other.y
        r_ori = self.ori_deg + other.ori_deg
        result = OrientedPoint(r_x, r_y, r_ori)
        return result

    def __sub__(self, other):
        """Subtract two points, sub orientations as well
        """
        r_x = self.x - other.x
        r_y = self.y - other.y
        r_ori = self.ori_deg - other.ori_deg
        result = OrientedPoint(r_x, r_y, r_ori)
        return result

    def __eq__(self, other):
        """Compare two OrientedPoint
        """
        if not isclose(self.x, other.x):
            return False
        if not isclose(self.y, other.y):
            return False
        if not isclose(self.ori_deg, other.ori_deg):
            return False
        return True

    def __repr__(self):
        the_repr_str = ""
        the_repr_str += f"({self.x:.4f}, {self.y:.4f})"
        the_repr_str += f" # {self.ori_deg:.4f}"
        return the_repr_str
