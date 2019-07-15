import math
import copy
import time

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
        for i in range(0, C1DB.memoryTicks):
            C1DB.myCarPrevLocs.append(Vec3(0, 0, 0))
            C1DB.myCarPrevVels.append(Vec3(0, 0, 0))
            C1DB.myCarPrevRots.append(Rotator(0, 0, 0))
            C1DB.myCarPrevAVels.append(Vec3(0, 0, 0))
            C1DB.prevPath.append(PathData(0.0000001, 0.0000001, 0.0000001))

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:

        #Setting up data...

        if C1DB.ticks == 0:
            while len(C1DB.carLoc) != len(packet.game_cars):
                C1DB.carLoc.append(Vec3(0, 0, 0))
                C1DB.carVel.append(Vec3(0, 0, 0))
                C1DB.carRot.append(Rotator(0, 0, 0))
                C1DB.carAVel.append(Vec3(0, 0, 0))
                C1DB.carPrevVel.append(Vec3(0, 0, 0))
        else:
            C1DB.deltaTime = time.perf_counter() - C1DB.pastTime
            if C1DB.deltaTime < 0:
                C1DB.deltaTime += 1
        C1DB.pastTime = time.perf_counter()
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

        #updating past values
        C1DB.myCarPrevLocs[C1DB.ticks%C1DB.memoryTicks] = copy.copy(C1DB.carLoc[C1DB.index])
        C1DB.myCarPrevVels[C1DB.ticks%C1DB.memoryTicks] = copy.copy(C1DB.carVel[C1DB.index])
        C1DB.myCarPrevRots[C1DB.ticks%C1DB.memoryTicks] = Rotator(C1DB.carRot[C1DB.index].pitch, C1DB.carRot[C1DB.index].yaw, C1DB.carRot[C1DB.index].roll)
        C1DB.myCarPrevAVels[C1DB.ticks%C1DB.memoryTicks] = copy.copy(C1DB.carAVel[C1DB.index])

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


        #State outputs
        if C1DB.debugOut and C1DB.ticks % 40 == 0:  # int(1/C1DB.deltaTime)
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

            print("car 1's Vel")
            print(C1DB.carVel[1].x/60)
            print(C1DB.carVel[1].y/60)
            print(C1DB.carVel[1].z/60)

            print("car 1's Previous Vel")
            print(C1DB.carPrevVel[1].x/60)
            print(C1DB.carPrevVel[1].y/60)
            print(C1DB.carPrevVel[1].z/60)
            print()

            print("car 0's pos: ")
            print(C1DB.carLoc[0].x)
            print(C1DB.carLoc[0].y)
            print(C1DB.carLoc[0].z)
            print("car 0's rot: ")
            print(C1DB.carRot[0].pitch)
            print(C1DB.carRot[0].yaw)
            print(C1DB.carRot[0].roll)
            print()

            print("delta Time:")
            print(C1DB.deltaTime)
            print()



        # --- AI Start ---
        ball_prediction = self.get_ball_prediction_struct()

        if ball_prediction is not None:
            for i in range(ball_prediction.num_slices - 5, ball_prediction.num_slices):
                prediction_slice = ball_prediction.slices[i]
                location = prediction_slice.physics.location
                # if C1DB.debugOut and C1DB.ticks % int(10*1/C1DB.deltaTime) == 0:
                #     self.logger.info("At time {}, the ball will be at ({}, {}, {})"
                #                      .format(prediction_slice.game_seconds, location.x, location.y, location.z))


        #debugTracks:
        if C1DB.debugTrack == 0:
            pathFinder(self.controller_state, packet, C1DB, Target(C1DB.ballLoc, 2400, Rotator(0, -math.pi/2, 0), 0))
        elif C1DB.debugTrack == 1:
            pathFinder(self.controller_state, packet, C1DB, Target(Vec3(2180, 3090, 17), 0, Rotator(0, -0.8, 0), 0))
            if (C1DB.carLoc[C1DB.index] - Vec3(2180, 3090, 17)).mag3() < C1DB.targetSize:
                C1DB.debugTrack = 2
        elif C1DB.debugTrack == 2:
            pathFinder(self.controller_state, packet, C1DB, Target(Vec3(0, 0, 17), 1400, Rotator(0, -2.356, 0), 0))
            if (C1DB.carLoc[C1DB.index] - Vec3(0, 0, 17)).mag3() < C1DB.targetSize:
                C1DB.debugTrack = 3
        elif C1DB.debugTrack == 3:
            pathFinder(self.controller_state, packet, C1DB, Target(Vec3(-2180, -3090, 17), 700, Rotator(0, -0.8, 0), 0))
            if (C1DB.carLoc[C1DB.index] - Vec3(-2180, -3090, 17)).mag3() < C1DB.targetSize:
                C1DB.debugTrack = 4
        elif C1DB.debugTrack == 4:
            pathFinder(self.controller_state, packet, C1DB, Target(Vec3(2180, -3090, 17), 1000, Rotator(0, 0.8, 0), 0))
            if (C1DB.carLoc[C1DB.index] - Vec3(2180, -3090, 17)).mag3() < C1DB.targetSize:
                C1DB.debugTrack = 5
        elif C1DB.debugTrack == 5:
            pathFinder(self.controller_state, packet, C1DB, Target(Vec3(0, 0, 17), 2000, Rotator(0, 2.356, 0), 0))
            if (C1DB.carLoc[C1DB.index] - Vec3(0, 0, 17)).mag3() < C1DB.targetSize:
                C1DB.debugTrack = 6
        elif C1DB.debugTrack == 6:
            pathFinder(self.controller_state, packet, C1DB, Target(Vec3(-2180, 3090, 17), 1400, Rotator(0, 0.8, 0), 0))
            if (C1DB.carLoc[C1DB.index] - Vec3(-2180, 3090, 17)).mag3() < C1DB.targetSize:
                C1DB.debugTrack = 1
        if C1DB.ticks%6000 < 3000:
            targetVel = C1DB.ticks%3000
        else:
            targetVel = 0
        if C1DB.debugTrack == 7:
            if packet.game_cars[0].double_jumped == 1:
                C1DB.debugTrack = 8
            else:
                #controller:
                self.controller_state.steer = 0.8

                self.controller_state.throttle = 1
                if C1DB.carVel[C1DB.index].mag2() > targetVel:
                    self.controller_state.throttle = 0
                    self.controller_state.boost = 0
                elif C1DB.carVel[C1DB.index].mag2() > 1220:
                    self.controller_state.boost = 1

                #analysis:
                if packet.game_cars[self.index].physics.location.z < 25:
                    out = str(C1DB.carVel[C1DB.index].mag2())
                    denominator = (C1DB.carVel[self.index].x*(C1DB.myCarPrevVels[C1DB.ticks%C1DB.memoryTicks].y - C1DB.myCarPrevVels[(C1DB.ticks-1)%C1DB.memoryTicks].y)/C1DB.deltaTime - C1DB.carVel[self.index].y*(C1DB.myCarPrevVels[C1DB.ticks%C1DB.memoryTicks].x - C1DB.myCarPrevVels[(C1DB.ticks-1)%C1DB.memoryTicks].x)/C1DB.deltaTime)
                    if(denominator != 0):
                        out = out + "    " + str((C1DB.carVel[self.index].x**2 + C1DB.carVel[self.index].y**2)**(3/2)/ denominator)
                    else:
                        out = out + "    inf"
                    # print("car to car: " + str((C1DB.carLoc[0] - C1DB.carLoc[1]).mag2()))
                    out = out + "    " + str(targetVel) + "    " + str(C1DB.deltaTime) + "\n"
                    print(out)
                    debugOut = open("debug.txt", "a+")
                    debugOut.write(out)
                    debugOut.close()
                else:
                    print("too high")
        elif C1DB.debugTrack == 8:
            if packet.game_cars[0].double_jumped == 0:
                C1DB.debugTrack = 9
        elif C1DB.debugTrack == 9:
            pathFinder(self.controller_state, packet, C1DB, Target(Vec3(0, 0, 0), targetVel, Rotator(0, 0, 0), 1))
            if (C1DB.carLoc[C1DB.index] - Vec3(0, 0, 0)).mag3() < C1DB.targetSize:
                C1DB.testTicks = 0
                C1DB.debugTrack = 7



        action_display = "temp"
        #draws ground path if available
        if C1DB.debugVisual == 1:
            drawPolarPath(self.renderer, C1DB)
        elif C1DB.debugVisual == 2:
            drawCirclePath(self.renderer, C1DB)

        # draw_debug(self.renderer, packet.game_cars[self.index], packet.game_ball, action_display)

        # --- Tick end data management ---
        # updates time
        C1DB.ticks += 1
        if C1DB.ticks == 1000000:
            C1DB.ticks = 0

        #update path tester
        if C1DB.ticks%100 == 99:
            C1DB.testTicks += 1


        # updates data base
        for i in range(0, len(C1DB.carVel)):
            C1DB.carPrevVel[i] = copy.copy(C1DB.carVel[i])
        C1DB.ballPrevVel = copy.copy(C1DB.ballVel)
        C1DB.prevInput = SimpleControllerState(self.controller_state.steer,
                                               self.controller_state.throttle,
                                               self.controller_state.pitch,
                                               self.controller_state.yaw,
                                               self.controller_state.roll,
                                               self.controller_state.jump,
                                               self.controller_state.boost,
                                               self.controller_state.handbrake)
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
    # renderer.draw_line_3d(car.physics.location, ball.physics.location, renderer.white())
    # print the action that the bot is taking
    renderer.draw_string_3d(car.physics.location, 2, 2, action_display, renderer.white())
    renderer.end_rendering()


def drawPolarPath(renderer, C1DB):
    freq = 2
    inVec = []
    renderer.begin_rendering()

    if C1DB.unmathable == 1:
        renderer.draw_string_3d([C1DB.carLoc[C1DB.index].x, C1DB.carLoc[C1DB.index].y, C1DB.carLoc[C1DB.index].z], 2, 2, "unmathable", renderer.white())
    elif C1DB.unmathable == 2:
        renderer.draw_string_3d([C1DB.carLoc[C1DB.index].x, C1DB.carLoc[C1DB.index].y, C1DB.carLoc[C1DB.index].z], 2, 2, "Very unmathable", renderer.white())

    for i in range(0, int(C1DB.memoryTicks/freq)):
        index = (C1DB.ticks - i*freq)%C1DB.memoryTicks
        for r in range(0, 50):
            R = C1DB.prevPath[index].ro/50 * r
            phi = C1DB.prevPath[index].phio * (R/C1DB.prevPath[index].ro)**C1DB.prevPath[index].exp + C1DB.myCarPrevRots[index].yaw
            inVec.append([R*math.cos(phi) + C1DB.myCarPrevLocs[index].x, R*math.sin(phi) + C1DB.myCarPrevLocs[index].y, 17.2])  # C1DB.carLoc[C1DB.index].z

        if i == 0:
            renderer.draw_polyline_3d(inVec, renderer.white())
        else:
            renderer.draw_polyline_3d(inVec, renderer.cyan())

    renderer.end_rendering()


def drawCirclePath(renderer, C1DB):
    renderer
    C1DB