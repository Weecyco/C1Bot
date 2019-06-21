import math
# from C1Properties import C1Properties, Target
from VecUtilities import Vec2, Vec3, cross2, dot2, cross3, dot3




def pathFinder(controlState, packet, C1DB, targ):
    #defaults:
    controlState.handbrake = 0

    dR = targ.loc - C1DB.carLoc[C1DB.index]
    ro = dR.mag2()
    if dR.x == 0:
        dR.x = 0.0000001
    if C1DB.carVel[C1DB.index].x == 0:
        C1DB.carVel[C1DB.index].x = 0.0000001
    if C1DB.carPrevVel[C1DB.index].x == 0:
        C1DB.carPrevVel[C1DB.index].x = 0.0000001
    phio = math.tan(dR.y/dR.x) - math.tan(C1DB.carVel[C1DB.index].y/C1DB.carVel[C1DB.index].x)
    exp = 5
    phi = phio * math.log(C1DB.carVel[C1DB.index].mag2()/60/ro, exp)

    phiOld = 0.0000001
    # controls steering based on angle required
    if C1DB.prevInput is not None and C1DB.prevInput.steer != 0:

        phiOld = math.tan(C1DB.carVel[C1DB.index].y / C1DB.carVel[C1DB.index].x) - math.tan(C1DB.carPrevVel[C1DB.index].y / C1DB.carPrevVel[C1DB.index].x)
        if phiOld == 0:
            phiOld = 0.0000001
        steerNew = C1DB.prevInput.steer / phiOld * phi

        # conrols boost and hand brake for turning
        if controlState.boost == 0:
            if steerNew > 1:
                controlState.handbrake = 1
                steerNew = 1
            if steerNew < -1:
                controlState.handbrake = 1
                steerNew = -1
        else:
            if steerNew > 1:
                controlState.boost = 0
                steerNew = 1
            if steerNew < -1:
                controlState.boost = 0
                steerNew = -1
        controlState.steer = steerNew
    else:
        if phi >= 0:
            controlState.steer = 1
        else:
            controlState.steer = -1

    # outputs
    if C1DB.ticks%60 == 0:
        out = "Ro = " + str(ro) + " PHIo = " + str(phio)
        print(out)
        out = "phi = " + str(phi) + " From r = " + str(C1DB.carVel[C1DB.index].mag2())
        print(out)
        if C1DB.prevInput is not None:
            out = "raw steer: " + str(C1DB.prevInput.steer / phiOld * phi)
            print(out)

        out = "Phiold: " + str(phiOld)
        print(out)
        out = "R angle: " + str(math.tan(dR.y/dR.x)) + " car angle: " + str(math.tan(C1DB.carVel[C1DB.index].y/C1DB.carVel[C1DB.index].x)) + " past car angle: " + str(math.tan(C1DB.carPrevVel[C1DB.index].y / C1DB.carPrevVel[C1DB.index].x))
        print(out)


    C1DB.prevPath = PathData(ro, phio, exp)


class PathData:
    def __init__(self, ro, phio, exp):
        self.ro = ro
        self.phio = phio
        self.exp = exp

