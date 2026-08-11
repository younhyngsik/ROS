from pathlib import Path

import cv2
import numpy as np


def main():
    file_path = Path(__file__).parent
    img = cv2.imread(str(file_path / "data/lena.jpg"))

    cv2.namedWindow("img", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("img", img.shape[1], img.shape[0])

    roi = img[100:200, 300:400] # roi가 새로운 메모리 영역을 가지지 않음
                                # 얕은 복사 => 원 이미지에 영향
    
    roi = img[100:200, 300:400].copy()  # 깊은 복사 => 원 이미지에 영향 x
    roi[:, :]= (0, 255, 0)

    cv2.imshow("img", img)
    cv2.imshow("roi", roi)
    cv2.waitKey()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()