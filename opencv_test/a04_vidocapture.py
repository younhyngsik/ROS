from pathlib import Path

import cv2
import numpy as np


def main():
    file_path = Path(__file__).parent
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    cap.set(cv2.CAP_PROP_FOURCC, fourcc)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    if not cap.isOpened():
        return
    
    while True:
        ret, frame = cap.read()

        if not ret:
            break
        
        cv2.imshow("black", frame)
        if cv2.waitKey(1) == ord("q"):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()