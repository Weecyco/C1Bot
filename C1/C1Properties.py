from VecUtilities import Vec2, Vec3
from rlbot.utils.game_state_util import Rotator
from rlbot.agents.base_agent import SimpleControllerState
from pathGuide import PathData

class C1Properties:
    def __init__(self):
        self.pastTarg = Target(0, 0, 0)
        self.pastState = 0
        self.ticks = 0
        self.index = 0

        self.CBVec = Vec3(0, 0, 0)

        self.carLoc = [Vec3(0, 0, 0)]
        self.carVel = [Vec3(0.0000001, 0.0000001, 0.0000001)]
        self.carRot = [Rotator(0, 0, 0)]
        self.carAVel = [Vec3(0, 0, 0)]

        self.carPrevLoc = [Vec3(0, 0, 0)]
        self.carPrevVel = [Vec3(0.0000001, 0.0000001, 0.0000001)]

        self.ballLoc = Vec3(0, 0, 0)
        self.ballVel = Vec3(0.0000001, 0.0000001, 0.0000001)
        self.ballRot = Rotator(0, 0, 0)
        self.ballAVel = Vec3(0, 0, 0)

        self.ballPrevVel = Vec3(0.0000001, 0.0000001, 0.0000001)


        self.prevPath = PathData(0, 0, 0)
        self.prevInput = SimpleControllerState()

class Target:
    def __init__(self, loc = 0, vel = 0, priority = 0.0):
        self.loc = loc
        self.vel = vel
        self.priority = priority

