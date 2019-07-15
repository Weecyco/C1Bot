from VecUtilities import Vec2, Vec3
from rlbot.utils.game_state_util import Rotator
from rlbot.agents.base_agent import SimpleControllerState
from pathGuide import PathData, Target

class C1Properties:
    def __init__(self):
        self.debugVisual = 1
        self.debugOut = 0
        self.debugTrack = 9
        self.targetSize = 40
        self.unmathable = 0
        self.testTicks = 0

        self.pastTarg = Target(0, 0, 0, 0)
        self.pastState = 0
        self.ticks = 0
        self.index = 0

        self.CBVec = Vec3(0, 0, 0)

        self.carLoc = [Vec3(0, 0, 0)]
        self.carVel = [Vec3(0.0000001, 0.0000001, 0.0000001)]
        self.carRot = [Rotator(0, 0, 0)]
        self.carAVel = [Vec3(0, 0, 0)]

        self.carPrevVel = [Vec3(0.0000001, 0.0000001, 0.0000001)]

        self.ballLoc = Vec3(0, 0, 0)
        self.ballVel = Vec3(0.0000001, 0.0000001, 0.0000001)
        self.ballRot = Rotator(0, 0, 0)
        self.ballAVel = Vec3(0, 0, 0)

        self.ballPrevVel = Vec3(0.0000001, 0.0000001, 0.0000001)

        self.memoryTicks = 2  # min of 2
        self.prevPath = []
        self.myCarPrevLocs = []
        self.myCarPrevVels = []
        self.myCarPrevRots = []
        self.myCarPrevAVels = []

        self.prevInput = SimpleControllerState()

        self.pastTime = 0
        self.deltaTime = 0.016666666667

