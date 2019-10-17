import logging

from timeit import default_timer as timer

from math import cos
from math import sin
from math import radians

from PIL import Image
from PIL import ImageDraw

#  from pygame import display
from pygame.sprite import Sprite
from pygame.transform import rotate

from utils import load_image


class Racer(Sprite):
    """Experimental car to understand the agent

    Will be rewritten as proper gym env
    """

    def __init__(self, out_file_car, pos_x, pos_y, direction=0):
        logg = logging.getLogger(f"c.{__name__}.__init__")
        logg.debug(f"Start init")

        super().__init__()

        self.pos_x = pos_x
        self.pos_y = pos_y
        self.precise_x = pos_x
        self.precise_y = pos_y

        # car heading, degrees
        self.direction = direction
        #  self.dir_step = 3
        self.dir_step = 15

        logg.debug(f"Pos x {self.pos_x} y {self.pos_y} dir {self.direction}")

        self.speed = 0
        self.speed_step = 1
        # viscous drag coefficient
        self.drag_coeff = 0.5

        self.done = False

        self.out_file_car = out_file_car
        # image and rect are used by allsprites.draw
        self._create_car_image()
        self.orig_image, self.rect = load_image(self.out_file_car)
        self._rotate_car_image()
        logg.debug(f"Rect di car {self.rect}")

        #  self.rect.center = self.pos_x, self.pos_y
        self.step("nop")

    def step(self, action):
        """Perform the action

        left-rigth: change steering
        up-down: accelerate/brake
        combination of the above
        do nothing
 
        ----------
        This method steps the game forward one step
        Parameters
        ----------
        action : str
            MAYBE should be int anyway
        Returns
        -------
        ob, reward, episode_over, info : tuple
            ob (object) :
                an environment-specific object representing the
                state of the environment.
            reward (float) :
                amount of reward achieved by the previous action.
            episode_over (bool) :
                whether it's time to reset the environment again.
            info (dict) :
                diagnostic information useful for debugging.
        """
        logg = logging.getLogger(f"c.{__name__}.step")
        logg.debug(f"Doing action {action}")

        if action == "up":
            self._accelerate("up")
        elif action == "down":
            self._accelerate("down")

        elif action == "right":
            self._steer("right")
        elif action == "left":
            self._steer("left")

        elif action == "upright":
            self._accelerate("up")
            self._steer("right")
        elif action == "upleft":
            self._accelerate("up")
            self._steer("left")

        elif action == "downright":
            self._accelerate("down")
            self._steer("right")
        elif action == "downleft":
            self._accelerate("down")
            self._steer("left")

        elif action == "nop":
            pass

        # compute delta
        pos_x_d = cos(radians(360-self.direction)) * self.speed
        pos_y_d = sin(radians(360-self.direction)) * self.speed

        # move the car
        self.precise_x += pos_x_d
        self.precise_y += pos_y_d
        self.pos_x = int(self.precise_x)
        self.pos_y = int(self.precise_y)
        logg.debug(f"x {self.pos_x} y {self.pos_y} dir {self.direction}")

        # pick the rotated image and place it
        self.image = self.rot_car_image[self.direction]
        self.rect = self.rot_car_rect[self.direction]
        self.rect.center = self.pos_x, self.pos_y

    def _compute_reward(self, hit_directions):
        """Compute the reward of moving, related to the map you are in

        hit_directions is a list of direction of the segments you are hitting
        """
        logg = logging.getLogger(f"c.{__name__}._compute_reward")
        logg.debug(f"Reward for hitting {hit_directions}")

        # out of the map
        if len(hit_directions) == 0:
            self.done = True
            return

        mean_direction = sum(hit_directions) / len(hit_directions)
        logg.debug(f"mean_direction {mean_direction}")

        error = self.direction - mean_direction
        logg.debug(f"direction-mean {error}")
        error %= 360
        logg.debug(f"modulus {error}")
        if error > 180:
            error = 360 - error
        logg.debug(f"current direction {self.direction} has error of {error:.4f}")

    def _steer(self, action):
        """Steer the car
        """
        if action == "left":
            self.direction += self.dir_step
            if self.direction >= 360:
                self.direction -= 360
        elif action == "right":
            self.direction -= self.dir_step
            if self.direction < 0:
                self.direction += 360

    def _accelerate(self, action):
        """Control the speed of the car
        """
        if action == "up":
            # TODO some threshold, possibly from the drag
            self.speed += self.speed_step
        elif action == "down":
            self.speed -= self.speed_step
            # MAYBE it can go in reverse?
            if self.speed < 0:
                self.speed = 0

    def _create_car_image(self):
        self.size = 60, 40
        img1 = Image.new("RGBA", self.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img1)
        wheel_len = 7
        wheel_wid = 6
        mid = wheel_wid / 2
        delta = -3
        # top left wheel
        self._draw_oval(draw, 15 + delta + mid, 10 - mid, wheel_wid, wheel_len, "grey")
        # top right wheel
        self._draw_oval(
            draw,
            15 + 30 - (delta + mid + wheel_len),
            10 - mid,
            wheel_wid,
            wheel_len,
            "grey",
        )
        # bottom left
        self._draw_oval(draw, 15 + delta + mid, 30 - mid, wheel_wid, wheel_len, "grey")
        # bottom right wheel
        self._draw_oval(
            draw,
            15 + 30 - (delta + mid + wheel_len),
            30 - mid,
            wheel_wid,
            wheel_len,
            "grey",
        )
        # body
        self._draw_oval(draw, 15, 10, 20, 30, "red")
        # windshield
        #  wind_wid1 = 5
        #  wind_wid2 = 3
        wind_wid1 = 4
        wind_wid2 = 7
        draw.polygon(
            [
                (52, 20),
                (46, 20 - wind_wid2),
                (36, 20 - wind_wid1),
                (36, 20 + wind_wid1),
                (46, 20 + wind_wid2),
            ],
            fill="cyan",
        )

        # MAYBE can the saving be avoided
        img1.save(self.out_file_car, "bmp")

    def _draw_oval(self, draw, top, left, width, length, color):
        """draw an oval, top left is for the rectangle

        circle rect circle
        draw.rectangle(((15, 10), (45, 30)), fill="red")
        draw.ellipse(((5, 10), (25, 30)), fill="red")
        draw.ellipse(((35, 10), (55, 30)), fill="red")
        top 15 left 10 width 20 length 30
        """
        # make width even to simplify things
        if width % 2 != 0:
            width += 1
        mid = width / 2
        draw.rectangle(((top, left), (top + length, left + width)), fill=color)
        draw.ellipse(((top - mid, left), (top + mid, left + width)), fill=color)
        draw.ellipse(
            ((top + length - mid, left), (top + length + mid, left + width)), fill=color
        )

    def _rotate_car_image(self):
        """Create rotated copies of the sprite
        """
        logg = logging.getLogger(f"c.{__name__}._rotate_car_image")
        if 360 % self.dir_step != 0:
            logg.warn(f"A dir_step that is not divisor of 360 is a bad idea")
        self.rot_car_image = {}
        self.rot_car_rect = {}
        for dire in range(0, 360, self.dir_step):
            self.rot_car_image[dire] = rotate(self.orig_image, dire)
            self.rot_car_rect[dire] = self.rot_car_image[dire].get_rect()
            #  logg.debug(f"rect {dire}: {self.rot_car_rect[dire]}")
