import math


class OrientedPoint:
    def __init__(self, x: float, y: float, ori_deg: float) -> None:
        """Create a point with orientation

        point (x,y) with orientation in degrees, ranging [-180, 180)
        """
        self.x = x
        self.y = y
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
        self.ori_rad = math.radians(self.ori_deg)
        # convert to slope of a line
        self.ori_slo = math.tan(self.ori_rad)

    def __repr__(self) -> str:
        the_repr_str = ""
        the_repr_str += f"({self.x:.0f}, {self.y:.0f})"
        the_repr_str += f" # {self.ori_deg:.0f}"
        return the_repr_str


class SplinePoint(OrientedPoint):
    """Spline Point: an OrientedPoint with additional info
    """

    def __init__(self, x: float, y: float, ori_deg: float, spid: int) -> None:
        """Create a point with orientation

        point (x,y) with orientation in degrees, ranging [-180, 180)
        spid: a unique integer identifier for the point
        """
        super().__init__(x, y, ori_deg)
        self.spid = spid

    def __repr__(self) -> str:
        the_repr_str = super().__repr__()
        the_repr_str += f" SPID: {self.spid}"
        return the_repr_str
