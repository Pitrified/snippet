import logging

from timeit import default_timer as timer

from PIL import Image
from PIL import ImageDraw

from pygame.sprite import Group
from pygame.sprite import Sprite
from pygame.transform import rotate

from utils import load_image


class RacingMap(Group):
    """Map for a racer, as collection of rect

    Should be easy to do collision detection
    """

    def __init__(self, field_wid, field_hei):
        logg = logging.getLogger(f"c.{__name__}.__init__")
        logg.debug(f"Start init")
        super().__init__()

        self.field_wid = field_wid
        self.field_hei = field_hei

        self.out_file_road = "road.bmp"
        self._create_road_segment()

        #  self.orig_image, self.rect = load_image(self.out_file_road)

        # direction, centerx, centery
        self.seg_info = [[0, 100, 100], [45, 200, 200]]
        self.segments = {}
        self.num_segments = len(self.seg_info)

        # create the various segments
        for i in range(self.num_segments):
            #  self.seg_img[i], self.seg_rect[i] = Segment(self.out_file_road)
            direction, cx, cy = self.seg_info[i]
            self.segments[i] = Segment(self.out_file_road, direction, cx, cy)
            self.add(self.segments[i])

    def _create_road_segment(self):
        """Create the bmp for a road segment
        """
        logg = logging.getLogger(f"c.{__name__}._create_road_segment")

        self.size = 6 * 60, 4 * 40
        img1 = Image.new("RGBA", self.size, "grey")
        draw = ImageDraw.Draw(img1)
        line_wid = 2
        mid_hei = self.size[1] // 2
        #  draw.rectangle(
        #  ((0, mid_hei - line_wid), (self.size[0], mid_hei + line_wid)),
        #  fill="lightgrey",
        #  )

        img1.save(self.out_file_road, "bmp")


class Segment(Sprite):
    """A single segment of road
    """

    def __init__(self, out_file_road, direction, cx, cy):
        logg = logging.getLogger(f"c.{__name__}.__init__")
        logg.debug(f"Start init")
        super().__init__()

        self.out_file_road = out_file_road
        self.orig_image, self.rect = load_image(self.out_file_road)

        self.direction = direction
        self.cx = cx
        self.cy = cy

        self.rotate_image(self.direction)

    def rotate_image(self, direction):
        """Rotate the image segment
        """
        self.image = rotate(self.orig_image, 360 - direction)
        self.rect = self.image.get_rect(center=(self.cx, self.cy))
