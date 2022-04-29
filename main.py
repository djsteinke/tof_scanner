import logging
import math
import optparse
import os
from stepper import Stepper
from tof import TOF
from time import strftime, sleep
from threading import Timer


logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('log.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


v_pins = [14, 15, 18, 23]
r_pins = [24, 25, 8, 7]


def run_scan():
    points = []
    v_steps = 512
    r_step = 2
    r_steps = int(512/360.0*angle)
    for h in range(0, int(height), 2):              # height in mm
        print('V: %d/%d' % (h, int(height)))
        if h > 0:
            v_stepper.step(v_steps, ccwise=True)
        for i in range(0, r_steps, r_step):            # steps / rot
            avg_a = tof.avg
            if len(avg_a) > 0:
                rad = center - (sum(avg_a) / len(avg_a))
                alpha = math.radians(360.0 / 512.0 * (i * 1.0))
                points.append([
                    rad * math.sin(alpha), rad * math.cos(alpha), h
                ])
            r_stepper.step(r_step, rpm=2)
        if angle < 360:
            r_stepper.step(r_steps, rpm=4, ccwise=True)

    # return sensor to bottom
    Timer(0.1, return_vert).start()

    points = ["%0.1f %0.1f %0.1f" % (x, y, z) for x, y, z in points]
    points = str.join("\n", points)

    timestamp = strftime('%Y%m%d_%H%M%S')
    out = open(f'{timestamp}.xyz', "w")
    out.write(points)
    out.close()

    tof.stop()


def run_scan_new():
    global scanning
    points = []
    steps = int(height / 2 * 512)
    for h in range(0, steps, 4):
        if h > 0:
            v_stepper.start_step(4, ccwise=True)
            r_stepper.start_step(4, rpm=2)
        rad = center - tof.range
        i = h % 512 * 1.0
        z = h * 1.0 / 512.0
        alpha = math.radians(i / 512.0 * 360.0)
        points.append([
            rad * math.sin(alpha), rad * math.cos(alpha), z
        ])

    Timer(0.1, return_vert).start()

    points = ["%0.1f %0.1f %0.1f" % (x, y, z) for x, y, z in points]
    points = str.join("\n", points)

    timestamp = strftime('%Y%m%d_%H%M%S')
    out = open(f'{timestamp}.xyz', "w")
    out.write(points)
    out.close()

    tof.stop()


def return_vert():
    s = int(height) / 2 * 512
    v_stepper.start_step(s)


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-s", "--scan", action="store", type="string", default="true", dest="scan",
                      help="")
    parser.add_option("-c", "--center", action="store", type="int", default=100, dest="center",
                      help="")
    parser.add_option("-v", "--height", action="store", type="int", default=100, dest="height",
                      help="")
    parser.add_option("-a", "--angle", action="store", type="int", default=360, dest="angle",
                      help="")
    parser.add_option("-m", "--move", action="store", type="int", default=0, dest="move")
    args, _ = parser.parse_args()

    scan = args.scan == "true"
    center = args.center
    height = args.height
    angle = args.angle
    move = args.move

    if move > 0:
        v_stepper = Stepper(v_pins)
        v_steps = int(move / 2 * 512)
        v_stepper.step(v_steps, ccwise=True)
        scan = False
    elif move < 0:
        v_stepper = Stepper(v_pins)
        v_steps = int(abs(move) / 2 * 512)
        v_stepper.step(v_steps, ccwise=False)
        scan = False

    path = os.path.join(os.getcwd(), "scans")  # create scans dir
    if not os.path.isdir(path):
        os.makedirs(path)

    tof = TOF()
    tof.start()

    scanning = False

    if scan:
        v_stepper = Stepper(v_pins)
        r_stepper = Stepper(r_pins)
        sleep(3.0)
        run_scan_new()
        #run_scan()
