from pathlib import Path

import cv2


def main():
    file_path = Path(__file__).parent
    print("안녕하세요.")
    print(cv2.__version__)
    img = cv2.imread(str(file_path / "data/robot.jpg"), cv2.IMREAD_GRAYSCALE)  # 절대 경로
    print(type(img), img.shape, img.dtype)
    x = img.shape[1]
    y = img.shape[0]
    print(x, y)
    cv2.imshow("robot", img)

    cv2.imwrite(str(file_path / "data" / "robot_gray.jpg"), img)
    imwrite_op = [cv2.IMWRITE_JPEG_QUALITY, 10]
    cv2.imwrite(str(file_path / "data" / "robot_gray_10.jpg"), img, imwrite_op)
    cv2.imwrite(str(file_path / "data" / "robot_gray.bmp"), img)
    cv2.waitKey()  # 블럭 함수


if __name__ == "__main__":
    main()