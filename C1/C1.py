import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket


class PythonExample(BaseAgent):

    def initialize_agent(self):
        #This runs once before the bot starts up
        self.controller_state = SimpleControllerState()

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        ball_location = Vector3(packet.game_ball.physics.location.x, packet.game_ball.physics.location.y,
                                packet.game_ball.physics.location.z)
        ball_velocity = Vector3(packet.game_ball.physics.velocity.x, packet.game_ball.physics.velocity.y,
                                packet.game_ball.physics.velocity.z)
        print(ball_location.x)

        print(self.index)
        print(len(packet.game_cars))
        my_car = packet.game_cars[self.index]

        # Setting car kinematic arrays
        car_location = [Vector3(packet.game_cars[0].physics.location.x, packet.game_cars[0].physics.location.y,
                                packet.game_cars[0].physics.location.z)]
        car_velocity = [Vector3(packet.game_cars[0].physics.velocity.x, packet.game_cars[0].physics.velocity.y,
                                packet.game_cars[0].physics.velocity.z)]
        car_direction = [get_car_facing_vector(packet.game_cars[0])]
        for i in range(1, packet.num_cars):
            car_location.append(Vector3(packet.game_cars[i].physics.location.x, packet.game_cars[i].physics.location.y,
                                        packet.game_cars[i].physics.location.z))
            car_velocity.append(Vector3(packet.game_cars[i].physics.velocity.x, packet.game_cars[i].physics.velocity.y,
                                        packet.game_cars[i].physics.velocity.z))
            car_direction.append(get_car_facing_vector(packet.game_cars[i]))
        print(car_location[0].x)

        # AI Start
        ball_prediction = self.get_ball_prediction_struct()

        if ball_prediction is not None:
            for i in range(0, ball_prediction.num_slices):
                prediction_slice = ball_prediction.slices[i]
                location = prediction_slice.physics.location
                # self.logger.info("At time {}, the ball will be at ({}, {}, {})"
                #                  .format(prediction_slice.game_seconds, location.x, location.y, location.z))

        cb_delta_d = ball_location - car_location[self.index]
        cb_delta_v = ball_velocity - car_velocity[self.index]
        if cb_delta_d.mag2() > 10000.0:
            throttle = 1.0
        else:
            throttle = math.fabs(cb_delta_d.mag2() / 10000.0)

        steer_correction_radians = car_direction[self.index].correction_to(cb_delta_d)
        if steer_correction_radians > 0:
            # Positive radians in the unit circle is a turn to the left.
            turn = -1.0  # Negative value for a turn to the left.
            action_display = "turn left"
        else:
            turn = 1.0
            action_display = "turn right"

        self.controller_state.throttle = throttle
        self.controller_state.steer = turn

        draw_debug(self.renderer, my_car, packet.game_ball, action_display)

        return self.controller_state


class Vector2:
    def __init__(self, x=0, y=0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, val):
        return Vector2(self.x + val.x, self.y + val.y)

    def __sub__(self, val):
        return Vector2(self.x - val.x, self.y - val.y)

    def correction_to(self, ideal):
        # The in-game axes are left handed, so use -x
        current_in_radians = math.atan2(self.y, -self.x)
        ideal_in_radians = math.atan2(ideal.y, -ideal.x)

        correction = ideal_in_radians - current_in_radians

        # Make sure we go the 'short way'
        if abs(correction) > math.pi:
            if correction < 0:
                correction += 2 * math.pi
            else:
                correction -= 2 * math.pi

        return correction


class Vector3(Vector2):
    def __init__(self, x=0, y=0, z=0):
        Vector2.__init__(self, x, y)
        print(self.x)
        self.z = float(z)

    def __add__(self, val):
        return Vector3(self.x + val.x, self.y + val.y, self.z + val.z)

    def __sub__(self, val):
        return Vector3(self.x - val.x, self.y - val.y, self.z - val.z)

    def mag3(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def mag2(self):
        return math.sqrt(self.x**2 + self.y**2)

def get_car_facing_vector(car):
    pitch = float(car.physics.rotation.pitch)
    yaw = float(car.physics.rotation.yaw)

    facing_x = math.cos(pitch) * math.cos(yaw)
    facing_y = math.cos(pitch) * math.sin(yaw)

    return Vector2(facing_x, facing_y)

def draw_debug(renderer, car, ball, action_display):
    renderer.begin_rendering()
    # draw a line from the car to the ball
    renderer.draw_line_3d(car.physics.location, ball.physics.location, renderer.white())
    # print the action that the bot is taking
    renderer.draw_string_3d(car.physics.location, 2, 2, action_display, renderer.white())
    renderer.end_rendering()


def cross2(vec2d1, vec2d2):
    return vec2d1.x * vec2d2.y - vec2d2.x * vec2d1.y


def dot2(vec2d1, vec2d2):
    return vec2d1.x * vec2d2.x + vec2d1.y * vec2d2.y


def cross3(vec3d1, vec3d2):
    return Vector3(vec3d1.y * vec3d2.z - vec3d1.z * vec3d2.y, vec3d1.z * vec3d2.x - vec2d1.x * vec2d2.z,
                   vec3d1.x * vec3d2.y - vec2d2.x * vec2d1.y)


def dot3(vec3d1, vec3d2):
    return vec3d1.x * vec3d2.x + vec3d1.y * vec3d2.y + vec3d1.z * vec3d2.z
