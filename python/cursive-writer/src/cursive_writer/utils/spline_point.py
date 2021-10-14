from cursive_writer.utils.oriented_point import OrientedPoint


class SplinePoint(OrientedPoint):
    """Spline Point: an OrientedPoint with additional info"""

    def __init__(self, x: float, y: float, ori_deg: float, spid: int) -> None:
        """Create a point with orientation

        point (x,y) with orientation in degrees, ranging [-180, 180)
        spid: a unique integer identifier for the point
        """
        super().__init__(x, y, ori_deg)
        self.spid = spid

    def __repr__(self):
        the_repr_str = super().__repr__()
        the_repr_str += f" SPID: {self.spid}"
        return the_repr_str
