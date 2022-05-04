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


def run_scan_new(start_h=0):
    global scanning
    points = []
    steps = int(height / 2 * 512)
    last_mm = 0
    timestamp = strftime('%Y%m%d_%H%M%S')
    for h in range(start_h, steps, 4):
        if h > 0:
            v_stepper.start_step(4, ccwise=True)
            r_stepper.start_step(2, rpm=2)
        rad = center - tof.range
        i = h % 512 * 1.0
        z = h * 1.0 / 512.0 * 2.0
        alpha = math.radians(i / (512.0*2.0) * 360.0)
        points.append([
            rad * math.sin(alpha), rad * math.cos(alpha), z
        ])
        if int(z) > last_mm:
            a_points = ["%0.1f %0.1f %0.1f" % (x, y, z) for x, y, z in points]
            str_points = str.join("\n", a_points)
            out = open(f'{timestamp}.xyz', "a")
            out.write(str_points)
            out.close()
            logger.debug("wrote %d steps to file. alpha [%0.3f]" % (len(points), alpha))
            points = []
            last_mm = int(z)
            print("%d/%d" % (last_mm, height))
            logger.debug("%d/%d" % (last_mm, height))

    Timer(0.1, return_vert).start()

    a_points = ["%0.1f %0.1f %0.1f" % (x, y, z) for x, y, z in points]
    str_points = str.join("\n", a_points)
    out = open(f'{timestamp}.xyz', "a")
    out.write(str_points)
    out.close()

    tof.stop()


def return_vert():
    s = int(height) / 2 * 512
    v_stepper.start_step(s)


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-s", "--scan", action="store", type="string", default="true", dest="scan",
                      help="")
    parser.add_option("-c", "--center", action="store", type="int", default=181, dest="center",
                      help="")
    parser.add_option("-v", "--height", action="store", type="int", default=270, dest="height",
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
        v_stepper.start_step(v_steps, ccwise=True)
        scan = False
    elif move < 0:
        v_stepper = Stepper(v_pins)
        v_steps = int(abs(move) / 2 * 512)
        v_stepper.start_step(v_steps, ccwise=False)
        scan = False
    else:
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
