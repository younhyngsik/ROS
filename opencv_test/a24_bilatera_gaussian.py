from pathlib import Path

import cv2
import numpy as np


def main():
    file_path = Path(__file__).parent
    file_path = str(file_path / "data/lena.jpg")
    img: np.ndarray = cv2.imread(file_path)

    # Gaussian filter
    dst1 = cv2.GaussianBlur(img, (11, 11), 3)
    dst2 = cv2.GaussianBlur(img, (11, 11), 10)
    dst3 = cv2.bilateralFilter(img, -1, 10, 10)
    
    cv2.imshow("img", img)
    cv2.imshow("Gaussian 3", dst1)
    cv2.imshow("Gaussian 10", dst2)
    cv2.imshow("bilateral", dst3)
    cv2.waitKey()
    cv2.destroyAllWindows


if __name__ == "__main__":
    main()