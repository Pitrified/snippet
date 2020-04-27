import numpy as np  # type: ignore
from typing import List, Tuple, Union

from cursive_writer.utils.oriented_point import OrientedPoint

# anything that is a valid input to np.array()
DArray = Union[List[float], np.ndarray]

Glyph = List[OrientedPoint]
Spline = List[Glyph]

ThickSegment = Tuple[np.ndarray, np.ndarray]
ThickGlyph = List[ThickSegment]
ThickSpline = List[ThickGlyph]
