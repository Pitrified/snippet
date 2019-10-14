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
        self.seg_info = [
            [0, 200, 150],
            [90, 300, 250],
            [0, 400, 350],
            [270, 500, 250],
            [0, 600, 150],
            [90, 700, 250],
            [90, 700, 450],
            [90, 700, 650],
            [180, 600, 750],
            [180, 400, 750],
            [180, 200, 750],
            [270, 100, 650],
            [270, 100, 450],
            [270, 100, 250],
        ]
        self.segments = {}
        self.num_segments = len(self.seg_info)

        # create the various segments
        for i in range(self.num_segments):
            #  self.seg_img[i], self.seg_rect[i] = Segment(self.out_file_road)
            direction, cx, cy = self.seg_info[i]
            self.segments[i] = Segment(self.out_file_road, direction, cx, cy, i)
            self.add(self.segments[i])

    def _create_road_segment(self):
        """Create the bmp for a road segment
        """
        logg = logging.getLogger(f"c.{__name__}._create_road_segment")

        self.size = 350, 150
        #  img1 = Image.new("RGBA", self.size, "grey")
        img1 = Image.new("RGBA", self.size, (128, 128, 128, 128))
        draw = ImageDraw.Draw(img1)
        line_wid = 2
        mid_hei = self.size[1] // 2
        draw.rectangle(
            ((0, mid_hei - line_wid), (self.size[0], mid_hei + line_wid)),
            fill="lightgrey",
        )
        draw.rectangle(
            ((self.size[0] - line_wid * 2, 0), (self.size[0], self.size[1])),
            fill="lightgrey",
        )

        img1.save(self.out_file_road, "bmp")


class Segment(Sprite):
    """A single segment of road
    """

    def __init__(self, out_file_road, direction, cx, cy, sid):
        logg = logging.getLogger(f"c.{__name__}.__init__")
        logg.debug(f"Start init")
        super().__init__()

        self.out_file_road = out_file_road
        self.orig_image, self.rect = load_image(self.out_file_road)

        self.direction = direction
        self.cx = cx
        self.cy = cy

        # save a segment id
        self.sid = sid

        self.rotate_image(self.direction)

    def rotate_image(self, direction):
        """Rotate the image segment
        """
        logg = logging.getLogger(f"c.{__name__}.__init__")

        self.image = rotate(self.orig_image, 360 - direction)
        self.rect = self.image.get_rect(center=(self.cx, self.cy))

        logg.debug(f"lefttop {self.rect.topleft} rightbottom {self.rect.bottomright}")
        logg.debug(f"width {self.rect.width} height {self.rect.height}")
