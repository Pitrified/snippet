import logging

from timeit import default_timer as timer
from math import cos
from math import sin
from math import radians

# pygame
import pygame
from pygame.sprite import Sprite
from pygame.sprite import spritecollide
from pygame.transform import rotate

# my files
from racer_racer import RacerCar
from racer_map import RacerMap
from utils import getMyLogger


class RacerEnv:
    """
    """

    def __init__(self, field_wid, field_hei, template_images):
        logg = getMyLogger(f"c.{__class__.__name__}.__init__")
        logg.debug(f"Start init")

        self.template_images = template_images

        self.field_wid = field_wid
        self.field_hei = field_hei
        self.field_size = (self.field_wid, self.field_hei)

        self.sidebar_wid = 300
        self.sidebar_hei = self.field_hei
        self.sidebar_size = (self.sidebar_wid, self.sidebar_hei)

        self.total_wid = self.sidebar_wid + self.field_wid
        self.total_hei = self.field_hei
        self.total_size = (self.total_wid, self.total_hei)

        pygame.init()
        self.screen = pygame.display.set_mode(self.total_size)
        pygame.display.set_caption("Racer")

        # Create The playing field
        self.field = pygame.Surface(self.field_size)
        # convert() changes the pixel format
        # https://www.pygame.org/docs/ref/surface.html#pygame.Surface.convert
        self.field = self.field.convert()
        #  self.field.fill((250, 250, 250))
        self.field.fill((0, 0, 0))

        # draw the field on the screen
        self.screen.blit(self.field, (0, 0))

        # Put Text On The field, Centered
        if not pygame.font:
            logg.critical("You need fonts to put text on the screen")

        # create a new Font object (from a file if you want)
        self.main_font = pygame.font.Font(None, 36)

        self.setup_sidebar()

        self.racer_car = RacerCar(self.template_images, 100, 100)

        self.racer_map = RacerMap(self.template_images, self.field_wid, self.field_hei)
        # draw map on the field, it is static, so there is no need to redraw it every time
        self.racer_map.draw(self.field)

        self.allsprites = pygame.sprite.RenderPlain((self.racer_car))

    def setup_sidebar(self):
        """
        """
        # create the sidebar
        self.sidebar = pygame.Surface(self.sidebar_size)
        self.sidebar = self.sidebar.convert()
        self.sidebar.fill((80, 80, 80))

        # render() draws the text on a Surface
        text_title = self.main_font.render("Drive safely", 1, (255, 255, 255))
        # somewhere here there is a nice drawing of rect pos
        # https://dr0id.bitbucket.io/legacy/pygame_tutorial01.html
        # the pos is relative to the surface you blit to
        textpos_title = text_title.get_rect(centerx=self.sidebar_wid / 2)

        # draw the text on the sidebar
        self.sidebar.blit(text_title, textpos_title)

        val_delta = 50
        speed_text_hei = 200
        text_speed = self.main_font.render("Speed:", 1, (255, 255, 255))
        textpos_speed = text_speed.get_rect(
            center=(self.sidebar_wid / 2, speed_text_hei)
        )
        self.sidebar.blit(text_speed, textpos_speed)
        speed_val_hei = speed_text_hei + val_delta

        direction_text_hei = 300
        text_direction = self.main_font.render("Direction:", 1, (255, 255, 255))
        textpos_direction = text_direction.get_rect(
            center=(self.sidebar_wid / 2, direction_text_hei)
        )
        self.sidebar.blit(text_direction, textpos_direction)
        direction_val_hei = direction_text_hei + val_delta

        # draw the sidebar on the screen
        self.screen.blit(self.sidebar, (self.field_wid, 0))

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
        logg = getMyLogger(f"c.{__class__.__name__}.step")
        logg.debug(f"Start step {action}")

        self.racer_car.step(action)

        reward, done = self._compute_reward()

        #  view = self.get_sensors()
        view = self._get_sensor_array()

        self._update_display()

    def _compute_reward(self):
        """
        """
        logg = getMyLogger(f"c.{__class__.__name__}._compute_reward")
        logg.debug(f"Start _compute_reward")

        # compute collision car/road
        hits = spritecollide(self.racer_car, self.racer_map, dokill=False)
        logg.debug(f"hitting {hits}")
        hit_directions = []
        hit_sid = []
        for segment in hits:
            logg.debug(f"hit segment with id {segment.sid}")
            hit_directions.append(self.racer_map.seg_info[segment.sid][0])
            hit_sid.append(segment.sid)

        # out of the map
        if len(hit_directions) == 0:
            return 0, True
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

        error = self.racer_car.direction - mean_direction
        logg.debug(f"direction-mean {error}")
        #  error %= 360
        if error < 0:
            error += 360
        logg.debug(f"modulus {error}")
        if error > 180:
            error = 360 - error
        logg.debug(
            f"current direction {self.racer_car.direction} has error of {error:.4f}"
        )

        reward = 90 - error
        # MAYBE a sigmoid-like shape
        return reward, False

    def get_screen(self):
        """a square with the car in the corner, looking to the diagonal
        """
        logg = getMyLogger(f"c.{__class__.__name__}.get_screen")
        logg.debug(f"Start get_screen")

        self.viewfield_size = 100
        pos_car = self.racer_car.pos_x, self.racer_car.pos_y
        vf_cos = cos(radians(360 - self.racer_car.direction - 45)) * self.viewfield_size
        vf_sin = sin(radians(360 - self.racer_car.direction - 45)) * self.viewfield_size

        # positions of the corners of the viewfield
        pos_left = int(pos_car[0] + vf_cos), int(pos_car[1] + vf_sin)
        pos_right = int(pos_car[0] - vf_sin), int(pos_car[1] + vf_cos)
        pos_front = int(pos_car[0] + vf_cos - vf_sin), int(pos_car[1] + vf_cos + vf_sin)

    def get_sensors(self, trace=False):
        """check if an array of sensors in front of the car is inside the road

        * compute the array for direction 0
        * rotate it for every direction needed
        * get the current one with a simple translation
        * check if the points in the current are inside the road or not:
            precompute a yes/no road map, as big as the field
        """

        self.viewfield_size = 100

        pos_car = self.racer_car.pos_x, self.racer_car.pos_y
        vf_cos = cos(radians(360 - self.racer_car.direction - 45)) * self.viewfield_size
        vf_sin = sin(radians(360 - self.racer_car.direction - 45)) * self.viewfield_size
        pos_left = int(pos_car[0] + vf_cos), int(pos_car[1] + vf_sin)
        pos_right = int(pos_car[0] - vf_sin), int(pos_car[1] + vf_cos)
        pos_front = int(pos_car[0] + vf_cos - vf_sin), int(pos_car[1] + vf_cos + vf_sin)

        the_color = (0, 255, 0, 128)
        the_size = 3
        pygame.draw.circle(self.field, the_color, pos_car, the_size)
        pygame.draw.circle(self.field, the_color, pos_right, the_size)
        pygame.draw.circle(self.field, the_color, pos_left, the_size)
        pygame.draw.circle(self.field, the_color, pos_front, the_size)

    def _get_sensor_array(self):
        """get the sa for the current direction and collide it with the road
        """
        logg = getMyLogger(f"c.{__class__.__name__}._get_sensor_array")
        logg.debug(f"Start _get_sensor_array")

        # get the current sensor_array to use
        self.curr_sa = self.racer_car.get_current_sensor_array()
        logg.debug(f"shape curr_sa {self.curr_sa.shape}")

        obs = []
        for s_pos in self.curr_sa:
            #  logg.debug(f"s_pos {s_pos}")
            if (
                s_pos[0] < 0
                or s_pos[0] >= self.field_wid
                or s_pos[1] < 0
                or s_pos[1] >= self.field_hei
            ):
                obs.append(0)
            else:
                obs.append(self.racer_map.raw_map[s_pos[0], s_pos[1]])
        #  logg.debug(f"obs {obs}")

        # draw the array on the sa_surf
        self._draw_sensor_array(obs)

        return obs

    def _draw_sensor_array(self, obs=None):
        """draw the sensor_array on a Surface
        """
        logg = getMyLogger(f"c.{__class__.__name__}._draw_sensor_array")
        logg.debug(f"Start _draw_sensor_array")

        # create the new surface for the sensor_array
        self.sa_surf = pygame.Surface(self.field_size)
        #  self.sa_surf = self.sa_surf.convert()
        black = (0, 0, 0)
        self.sa_surf.fill(black)
        # black colors will not be blit
        self.sa_surf.set_colorkey(black)

        the_color = (0, 255, 0, 128)
        the_second_color = (0, 0, 255, 128)
        color = the_color
        the_size = 3
        for i, s_pos in enumerate(self.curr_sa):
            if not obs is None:
                if obs[i] == 1:
                    color = the_second_color
                else:
                    color = the_color
            pygame.draw.circle(self.sa_surf, color, s_pos, the_size)

    def _update_display(self):
        """draw everything
        """
        logg = getMyLogger(f"c.{__class__.__name__}._update_display")
        logg.debug(f"Start _update_display")

        # Draw Everything again, every frame
        # the field already has the road drawn
        self.screen.blit(self.field, (0, 0))

        # draw all moving sprites (the car) on the screen
        self.allsprites.draw(self.screen)
        # if you draw on the field you can easily leave a track
        #  allsprites.draw(field)

        # draw the sensor surface
        self.screen.blit(self.sa_surf, (0, 0))

        # update the display
        pygame.display.flip()
