import math
from rlbot.messages.flat.Vector3 import Vector3

class Vec2:
    def __init__(self, x=0, y=0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, val):
        return Vec2(self.x + val.x, self.y + val.y)

    def __sub__(self, val):
        return Vec2(self.x - val.x, self.y - val.y)

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


class Vec3(Vec2):
    def __init__(self, x=0, y=0, z=0):
        Vec2.__init__(self, x, y)
        self.z = float(z)

    def __add__(self, val):
        return Vec3(self.x + val.x, self.y + val.y, self.z + val.z)

    def __sub__(self, val):
        return Vec3(self.x - val.x, self.y - val.y, self.z - val.z)

    def mag3(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def mag2(self):
        return math.sqrt(self.x**2 + self.y**2)

    # -pi to pi
    def angle_xy(self):
        if self.x < 0:
            if self.y > 0:
                return math.atan(self.y / self.x) + math.pi
            else:
                return math.atan(self.y / self.x) - math.pi
        elif self.x > 0:
            return math.atan(self.y / self.x)
        else:
            return math.atan(self.y / 0.0000000001)  # arbitrary small value to avoid division by 0


    def covtVecFrom(self, origVec):
        self.x = origVec.x
        self.y = origVec.y
        self.z = origVec.z

    def __copy__(self):
        return Vec3(self.x, self.y, self.z)


def cross2(vec2d1, vec2d2):
    return vec2d1.x * vec2d2.y - vec2d2.x * vec2d1.y


def dot2(vec2d1, vec2d2):
    return vec2d1.x * vec2d2.x + vec2d1.y * vec2d2.y


def cross3(vec3d1, vec3d2):
    return Vec3(vec3d1.y * vec3d2.z - vec3d1.z * vec3d2.y,
                   vec3d1.z * vec3d2.x - vec3d1.x * vec3d2.z,
                   vec3d1.x * vec3d2.y - vec3d2.x * vec3d1.y)


def dot3(vec3d1, vec3d2):
    return vec3d1.x * vec3d2.x + vec3d1.y * vec3d2.y + vec3d1.z * vec3d2.z
