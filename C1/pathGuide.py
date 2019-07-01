import math
# from C1Properties import C1Properties, Target
from VecUtilities import Vec2, Vec3, cross2, dot2, cross3, dot3




def pathFinder(controlState, packet, C1DB, targ):
    #defaults:
    controlState.handbrake = 0
    if C1DB.prevInput is not None:
        controlState.throttle = C1DB.prevInput.throttle

    #calculates optimal angle change for next frame
    dR = targ.loc - C1DB.carLoc[C1DB.index]
    ro = dR.mag2()
    if dR.x == 0:
        dR.x = 0.0000001
    if C1DB.carVel[C1DB.index].x == 0:
        C1DB.carVel[C1DB.index].x = 0.0000001
    if C1DB.carPrevVel[C1DB.index].x == 0:
        C1DB.carPrevVel[C1DB.index].x = 0.0000001
    phio = dR.angle_xy() - C1DB.carRot[C1DB.index].yaw
    if phio > math.pi:
        phio -= 2*math.pi
    elif phio < -math.pi:
        phio += 2*math.pi

    phiv = targ.rot.yaw - C1DB.carRot[C1DB.index].yaw
    if phiv > math.pi:
        phiv -= 2*math.pi
    elif phiv < -math.pi:
        phiv += 2*math.pi

    xRef = ro * math.cos(phio)
    yRef = ro * math.sin(phio)
    dyOvdx = math.tan(phiv)
    exp = (xRef*dyOvdx - yRef) / (phio * xRef + yRef*dyOvdx)
    if exp < 0.2:
        exp = 0.2
    phi = phio * (C1DB.carVel[C1DB.index].mag2()*C1DB.deltaTime/ro)**exp


    phiOld = 0.0000001
    # controls steering based on angle required
    if C1DB.prevInput is not None and C1DB.prevInput.steer != 0:

        phiOld = C1DB.myCarPrevRots[C1DB.ticks%C1DB.memoryTicks].yaw - C1DB.myCarPrevRots[(C1DB.ticks - 1)%C1DB.memoryTicks].yaw
        if phiOld > math.pi:
            phiOld -= 2 * math.pi
        elif phiOld < -math.pi:
            phiOld += 2 * math.pi
        elif phiOld == 0:
            phiOld = 0.0000001
        steerNew = abs(C1DB.prevInput.steer) / abs(phiOld) * phi

        # controls boost and hand brake for turning
        throttleChange = 0.1
        if controlState.boost == 0:
            if steerNew > 1:
                # controlState.handbrake = 1
                if controlState.throttle >= -1 + throttleChange:
                    controlState.throttle -= throttleChange/2
                # else:
                #     controlState.handbrake = 1
                steerNew = 1

            elif steerNew < -1:
                # controlState.handbrake = 1
                if controlState.throttle >= -1 + throttleChange:
                    controlState.throttle -= throttleChange/2
                # else:
                #     controlState.handbrake = 1
                steerNew = -1
            else:
                if controlState.throttle <= 1-throttleChange:
                    controlState.throttle += throttleChange
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
    if C1DB.carVel[C1DB.index].mag3() > 1 and abs(C1DB.carRot[C1DB.index].yaw - C1DB.carVel[C1DB.index].angle_xy()) > 2:
         controlState.steer *= -1

    # outputs
    if C1DB.debugOut and C1DB.ticks % 40 == 0:  # int(1/C1DB.deltaTime)
        out = "Ro = " + str(ro) + " PHIo = " + str(phio) + " Exp = " + str(exp)
        print(out)
        out = "phi = " + str(phi) + " From r = " + str(C1DB.carVel[C1DB.index].mag2()*C1DB.pastTime)
        print(out)
        if C1DB.prevInput is not None:
            out = "raw steer: " + str(abs(C1DB.prevInput.steer / phiOld) * phi)
            print(out)
            out = "previous steer: " + str(C1DB.prevInput.steer)
            print(out)

        out = "Phiold: " + str(phiOld)
        print(out)
        out = "car vel x: " + str(C1DB.carVel[C1DB.index].x) + " y: " + str(C1DB.carVel[C1DB.index].y) + "prev car vel x: " + str(C1DB.carPrevVel[C1DB.index].x) + " y: " + str(C1DB.carPrevVel[C1DB.index].y)
        print(out)
        out = "R angle: " + str(dR.angle_xy()) + " car angle: " + str(C1DB.myCarPrevRots[C1DB.ticks%C1DB.memoryTicks].yaw) + " past car angle: " + str(C1DB.myCarPrevRots[(C1DB.ticks - 1)%C1DB.memoryTicks].yaw)
        print(out)

        print()
        # out = "yaw: " + str(C1DB.carRot[0].yaw) + " my angle: " + str(C1DB.carVel[0].angle_xy())
        # print(out)


    C1DB.prevPath[C1DB.ticks%C1DB.memoryTicks] = PathData(ro, phio, exp)


class PathData:
    def __init__(self, ro, phio, exp):
        self.ro = ro
        self.phio = phio
        self.exp = exp

