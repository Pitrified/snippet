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


class RacerCar(Sprite):
    """Experimental car to understand the agent

    Will be rewritten as proper gym env

    NOTE: this class must be split in two:
        step, get_screen, _compute_reward moved in RacerEnv
        the car specific functions will be in RacerCar

    run_racer_main that does the setup of the field, will be in RacerEnv as well

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
        pos_x_d = cos(radians(360 - self.direction)) * self.speed
        pos_y_d = sin(radians(360 - self.direction)) * self.speed

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

    def _compute_reward(self, hit_directions, hit_sid):
        """Compute the reward of moving, related to the map you are in

        hit_directions is a list of direction of the segments you are hitting
        hit_sid is a list of segment ids
        """
        logg = logging.getLogger(f"c.{__name__}._compute_reward")
        logg.debug(f"Reward for hitting {hit_directions} {hit_sid}")

        # out of the map
        if len(hit_directions) == 0:
            self.done = True
            return
        # too many hits, your road is weird, cap them at 2 segments
        elif len(hit_directions) > 2:
            logg.warn(f"Too many segments hit")
            hit_directions = hit_directions[:2]
            hit_sid = hit_sid[:2]

        # now hit_directions is either 1 or 2 elements long
        if len(hit_directions) == 1:
            mean_direction = hit_directions[0]
        else:
            # 135   90  45    140   95  50    130   85  40
            # 180       0     185       5     175       -5
            # 225   270 315   230   275 320   220   265 310
            # 270, 0 have mean 315 = (270+0+360)/2
            # 270, 180 have mean 225 = (270+180)/2
            # 0, 90 have mean 45 = (0+90)/2
            if abs(hit_directions[0] - hit_directions[1]) > 180:
                mean_direction = (sum(hit_directions) + 360) / 2
                if mean_direction >= 360:
                    mean_direction -= 360
            else:
                mean_direction = sum(hit_directions) / 2

        logg.debug(f"mean_direction {mean_direction}")

        error = self.direction - mean_direction
        logg.debug(f"direction-mean {error}")
        #  error %= 360
        if error < 0:
            error += 360
        logg.debug(f"modulus {error}")
        if error > 180:
            error = 360 - error
        logg.debug(f"current direction {self.direction} has error of {error:.4f}")

        # now error goes from 0 (good) to 180 (very bad)

    def get_screen():
        """
        """

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
