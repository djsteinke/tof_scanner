from RpiMotorLib.RpiMotorLib import BYJMotor


class Stepper(object):
    def __init__(self, pins=None):
        if pins is None:
            pins = [14, 15, 18, 23]
        self._pins = pins
        self._motor = BYJMotor()

    def step(self, steps, wait=0.006, ccwise=False):
        self._motor.motor_run(self._pins, steps=steps, ccwise=ccwise, steptype="full", wait=wait)
