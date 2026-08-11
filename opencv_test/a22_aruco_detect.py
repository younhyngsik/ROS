
from pathlib import Path

import cv2
import numpy as np

def main():
    file_path = Path(__file__).parent
    pipeline = (
        "v4l2src device=/dev/video0 ! "
        "image/jpeg,width=640,height=480,framerate=30/1 ! "
        "jpegdec ! "
        "videoconvert ! "
        "video/x-raw,format=BGR ! "
        "appsink drop=true sync=false"
    )
    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
    # MJPG 설정

    #dict
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters_create()

    previous_ids = set()

    marker_length = 0.04    # m
    camera_metrix = np.array(
        [[600.0, 0.0, 640.0], 
         [0.0, 600.0, 480.0], 
         [0.0, 0.0, 1.0]], dtype=np.float64)

    dist_coeffs = np.zeros((5, 1), dtype=np.float64)


    if not cap.isOpened():
        return
    while True:
        ret, frame = cap.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = cv2.aruco.detectMarkers(gray, dictionary, parameters=parameters)
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            rvevs, tvecs, object_points = cv2.aruco.estimatePoseSingleMarkers(
                corners, marker_length, camera_metrix, dist_coeffs
            )
            print(rvevs, tvecs)

        # if not ret:
        #     break
        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) == ord("q"):
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()