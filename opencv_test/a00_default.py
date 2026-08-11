from pathlib import Path

import cv2
import numpy as np


def main():
    file_path = Path(__file__).parent
    black_img = np.zeros((300, 300, 1), dtype=np.uint8)
    cv2.imshow("balck", black_img)
    cv2.waitKey()
    cv2.destroyAllWindows


if __name__ == "__main__":
    main()