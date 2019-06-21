import math
from C1Properties import C1Properties, Target
from VecUtilities import Vec2, Vec3, cross2, dot2, cross3, dot3
from pathGuide import *

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.game_state_util import Rotator


C1DB = C1Properties()


class C1(BaseAgent):

    def initialize_agent(self):
        #This runs once before the bot starts up
        self.controller_state = SimpleControllerState()

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:

        if C1DB.ticks == 0:
            while len(C1DB.carLoc) != len(packet.game_cars):
                C1DB.carLoc.append(Vec3(0, 0, 0))
                C1DB.carVel.append(Vec3(0, 0, 0))
                C1DB.carRot.append(Rotator(0, 0, 0))
                C1DB.carAVel.append(Vec3(0, 0, 0))
                C1DB.carPrevVel.append(Vec3(0, 0, 0))

        C1DB.ballLoc.covtVecFrom(packet.game_ball.physics.location)
        C1DB.ballVel.covtVecFrom(packet.game_ball.physics.velocity)
        C1DB.ballRot = packet.game_ball.physics.rotation
        C1DB.ballAVel.covtVecFrom(packet.game_ball.physics.angular_velocity)

        C1DB.index = self.index

        for i in range(0, len(packet.game_cars)):
            C1DB.carLoc[i].covtVecFrom(packet.game_cars[i].physics.location)
            C1DB.carVel[i].covtVecFrom(packet.game_cars[i].physics.velocity)
            C1DB.carRot[i] = packet.game_cars[i].physics.rotation
            C1DB.carAVel[i].covtVecFrom(packet.game_cars[i].physics.angular_velocity)

        C1DB.CBVec = C1DB.ballLoc - C1DB.carLoc[C1DB.index]

        # Setting car kinematic arrays
        # car_location = [Vec3(packet.game_cars[0].physics.location.x,
        #                         packet.game_cars[0].physics.location.y,
        #                         packet.game_cars[0].physics.location.z)]
        # car_velocity = [Vec3(packet.game_cars[0].physics.velocity.x,
        #                         packet.game_cars[0].physics.velocity.y,
        #                         packet.game_cars[0].physics.velocity.z)]
        # car_direction = [get_car_facing_vector(packet.game_cars[0])]
        # for i in range(1, packet.num_cars):
        #     car_location.append(Vec3(packet.game_cars[i].physics.location.x, packet.game_cars[i].physics.location.y,
        #                                 packet.game_cars[i].physics.location.z))
        #     car_velocity.append(Vec3(packet.game_cars[i].physics.velocity.x, packet.game_cars[i].physics.velocity.y,
        #                                 packet.game_cars[i].physics.velocity.z))
        #     car_direction.append(get_car_facing_vector(packet.game_cars[i]))

        # C1DB.CBvec = ball_location - car_location[self.index]

        if C1DB.ticks % 60 == 0:
            print("ball location: ")
            print(C1DB.ballLoc.x)
            print("ball speed: ")
            print(C1DB.ballVel.mag3())

            print("self index: ")
            print(self.index)

            print("number of players: ")
            print(len(packet.game_cars))

            print("car 1's pos: ")
            print(C1DB.carLoc[1].x)
            print(C1DB.carLoc[1].y)
            print(C1DB.carLoc[1].z)
            print("end of car 0's xpos")

            print("car 1's Vel")
            print(C1DB.carVel[1].x/60)
            print(C1DB.carVel[1].y/60)
            print(C1DB.carVel[1].z/60)
            print("car 1's Previous Vel")
            print(C1DB.carPrevVel[1].x/60)
            print(C1DB.carPrevVel[1].y/60)
            print(C1DB.carPrevVel[1].z/60)

        # AI Start
        ball_prediction = self.get_ball_prediction_struct()

        if ball_prediction is not None:
            for i in range(ball_prediction.num_slices - 5, ball_prediction.num_slices):
                prediction_slice = ball_prediction.slices[i]
                location = prediction_slice.physics.location
                if C1DB.ticks % 600 == 0:
                    self.logger.info("At time {}, the ball will be at ({}, {}, {})"
                                     .format(prediction_slice.game_seconds, location.x, location.y, location.z))


        # cb_delta_v = ball_velocity - car_velocity[self.index]
        if C1DB.CBVec.mag2() > 500.0:
            self.controller_state.throttle = 1.0
        else:
            self.controller_state.throttle = math.fabs(C1DB.CBVec.mag2() / 1000.0)


        pathFinder(self.controller_state, packet, C1DB, Target(C1DB.ballLoc, C1DB.ballVel, 0))

        action_display = "temp"

        # self.controller_state.throttle = throttle
        # self.controller_state.steer = turn

        draw_debug(self.renderer, packet.game_cars[self.index], packet.game_ball, action_display)

        # updates time
        C1DB.ticks += 1
        if C1DB.ticks == 1000000:
            C1DB.ticks = 0

        # updates data base
        for i in range(0, len(C1DB.carVel)):
            C1DB.carPrevVel[i] = C1DB.carVel[i]
        C1DB.ballPrevVel = C1DB.ballVel
        C1DB.prevInput = self.controller_state

        return self.controller_state


def get_car_facing_vector(car):
    pitch = float(car.physics.rotation.pitch)
    yaw = float(car.physics.rotation.yaw)

    facing_x = math.cos(pitch) * math.cos(yaw)
    facing_y = math.cos(pitch) * math.sin(yaw)

    return Vec2(facing_x, facing_y)


def draw_debug(renderer, car, ball, action_display):
    renderer.begin_rendering()
    # draw a line from the car to the ball
    renderer.draw_line_3d(car.physics.location, ball.physics.location, renderer.white())
    # print the action that the bot is taking
    renderer.draw_string_3d(car.physics.location, 2, 2, action_display, renderer.white())
    renderer.end_rendering()
