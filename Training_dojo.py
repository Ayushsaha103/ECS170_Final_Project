from shapely.geometry import Point
from shapely.geometry.polygon import LineString
from shapely.geometry import Polygon
from math_helpers import distance, fit_exponential_through_points
import numpy as np
import random
import math
import time

import Constants

# Training dojo
# systems to constrain the car's motion and actions


class Training_dojo:
    def __init__(self, rd, wp, car, obs, tim):
        self.rd = rd
        self.wp = wp
        self.car = car
        self.obs = obs
        self.tim = tim
        self.game_num = -1
        self.successful_lap_index = -1

        self.carminv = 0.6
        self.carmaxv = 0.9
        max_curv = 0.8

        self.vset = (self.carmaxv + self.carminv)/2
        self.train_mode = "steer"
        self.m_for_v_ctrl, self.b_for_v_ctrl = fit_exponential_through_points((0.0, self.carmaxv),(max_curv, self.carminv))
        self.cur_rd_curvature = self.rd.max_curvature / 2


    def vary_speed(self):
        self.cur_rd_curvature = abs(self.rd.curvature_normalized[(self.wp.first_target_pt)])
        self.vset = \
            self.m_for_v_ctrl * math.exp(-self.b_for_v_ctrl * self.cur_rd_curvature)
        return self.vset

    def check_car_overlies_wp(self):
        car_box = Polygon(self.car.bounding_box)
        # import pdb; pdb.set_trace()
        target_line = LineString(
            (
                self.rd.left_boundary_points[self.wp.closest_pt],
                self.rd.right_boundary_points[self.wp.closest_pt],
            )
        )

        return target_line.intersects(car_box)

    def reset(self):
        self.game_num += 1
        pass

    def reward(self):
        reward = 0
        car_pos = (self.car.x, self.car.y)
        n = len(self.rd.track_points)
        wpcoor = self.rd.track_points[(self.wp.first_target_pt) % n]
        # reward += (1/600)*self.wp.rd_dist_traversed
        reward += 1 / 60

        # every 12 sec, vary the training reward func.
        t = time.time()
        nsec = 15.0
        method_fracs = [0.,1.0, 0.]
        if t % nsec < nsec * sum(method_fracs[:1]):
            self.train_mode = "optimal_wp_collision"
            # reward += -abs(self.obs.ephi) - (1/20)*self.obs.ey
            reward -= distance(car_pos, wpcoor) * 1 / 90

        elif t % nsec < nsec * sum(method_fracs[:2]):
            self.train_mode = "steer"
            # penalty for how far off the heading angle is from the road
            reward -= abs(self.obs.ephi) * 4 / 5 - (1/20) *  abs(self.obs.ey)
        else:
            self.train_mode = "speed_ctrl"
            reward -= abs(self.car.v-self.vary_speed())

        # check if waypoints updated
        # crossed_wp_coor = self.rd.track_points[self.wp.closest_pt-1]
        if self.wp.just_updated:  # and distance(car_pos, crossed_wp_coor) < 6:
            # print("wp update")
            reward += 9.0

            if self.wp.first_target_pt > len(self.rd.track_points) - 5:
                self.successful_lap_index = self.game_num
                print("Successful lap completion on game# " + str(self.game_num))

        return reward

    def collision_reward(self):
        return -200

    def terminate(self):
        # car is heading in wrong dir.
        # self.obs.s_update < 0
        # import pdb; pdb.set_trace()

        # car is too far from rd center
        if abs(self.obs.ey) > 8 + 2*(self.game_num / Constants.total_timesteps):
            return True

        # car is facing > 15deg from road yaw
        if abs(self.obs.ephi) > (29) * np.pi / 180:
            return True

        # # return True if car insuccessfully collides w/ wp
        # # AKA if car is too far from upcoming middle lane waypoint (when crossing it)
        # wpcoor = self.rd.track_points[self.wp.closest_pt-1]
        # if self.wp.just_updated and distance((self.car.x, self.car.y), wpcoor) > 10:
        #     return True
