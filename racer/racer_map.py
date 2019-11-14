import logging

from timeit import default_timer as timer

from PIL import Image
from PIL import ImageDraw

from pygame.sprite import Group
from pygame.sprite import Sprite
from pygame.transform import rotate

from utils import load_image
from utils import getMyLogger


class RacerMap(Group):
    """Map for a racer, as collection of rect

    Should be easy to do collision detection
    """

    def __init__(self, template_images, field_wid, field_hei):
        logg = getMyLogger(f"c.{__name__}.__init__", "INFO")
        logg.debug(f"Start init")
        super().__init__()

        self.field_wid = field_wid
        self.field_hei = field_hei
        self.template_images = template_images

        name_road_image = "road.bmp"
        self.out_file_road = self.template_images.format(name_road_image)
        self._create_road_segment()

        #  self.orig_image, self.rect = load_image(self.out_file_road)

        # direction, centerx, centery
        self.seg_info = [
            [0, 200, 100],
            [270, 450, 200],
            [0, 550, 450],
            [270, 800, 550],
            [180, 700, 800],
            [180, 350, 800],
            [90, 100, 700],
            [90, 100, 350],
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
        logg = getMyLogger(f"c.{__name__}._create_road_segment")

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
        logg = getMyLogger(f"c.{__name__}.__init__", "INFO")
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
        logg = getMyLogger(f"c.{__name__}.__init__", "INFO")

        #  self.image = rotate(self.orig_image, 360 - direction)
        self.image = rotate(self.orig_image, direction)
        self.rect = self.image.get_rect(center=(self.cx, self.cy))

        logg.debug(f"lefttop {self.rect.topleft} rightbottom {self.rect.bottomright}")
        logg.debug(f"width {self.rect.width} height {self.rect.height}")
