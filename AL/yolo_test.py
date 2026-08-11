import cv2
from ultralytics import YOLO

def main():
    model = YOLO("yolo26n.pt")  # load a pretrained YOLO26n model
    results = model("/home/youn/ROS/AL/data/dog.jpg")  # run inference
    annotated = results[0]
    annotated_img = results[0].plot()

    cv2.imshow("img", annotated_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()