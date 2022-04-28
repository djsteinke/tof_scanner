from RpiMotorLib.RpiMotorLib import BYJMotor


def wait_from_rpm(rpm):
    return 60.0 / (rpm * 1.0) / 4.0 / 512.0


class Stepper(object):
    def __init__(self, pins=None):
        if pins is None:
            pins = [14, 15, 18, 23]
        self._pins = pins
        self._motor = BYJMotor()

    def step(self, steps, wait=0.005, ccwise=False, rpm=None):
        if rpm is not None:
            wait = wait_from_rpm(rpm)
        wait = wait if wait >= 0.005 else 0.005
        self._motor.motor_run(self._pins, steps=steps, ccwise=ccwise, steptype="full", wait=wait)
