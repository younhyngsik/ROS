from pathlib import Path

import cv2
import numpy as np
import color

def main():
    file_path = Path(__file__).parent
    img = np.full((500, 500, 3), 255, dtype=np.uint8)
    x1, x2 = 100, 400
    y1, y2 = 100, 400

    cv2.rectangle(img, (x1, y1), (x2, y2), color.RED, 3)
    pt1 = 120, 50
    pt2_x = 300
    pt2_y = 500
    a = 0
    while True:
        a += 1
        cv2.rectangle(img, (x1, y1), (x2, y2), color.RED, 3)
        imgRect = (x1, y1, x2 - x1, y2 - y1)
        cv2.line(img, pt1, (pt2_x, pt2_y + a), color.BLUE, 3, type=cv2.LINE_AA)
        retval, rpt1, rpt2 = cv2.clipLine(imgRect, pt1, (pt2_x, pt2_y + a))
        if retval:
            cv2.circle(img, rpt1, 7, color.BLACK, -1)
            cv2.circle(img, rpt2, 7, color.BLACK, -1)
        cv2.imshow("canvas", img)
        if cv2.waitKey(30) == ord("q"):
            break


if __name__ == "__main__":
    main()