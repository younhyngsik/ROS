import rclpy
from rclpy.node import Node
import cv2
import numpy as np


class M_pub(Node):
    def __init__(self):        
        super().__init__("message_pub")
        self.create_timer(1/30,self.img_gen_callback)
        cv2.namedWindow("camera", self.img_gen_callback)
        self.img = np.zeros((300, 300), dtype=np.uint8)
        self.count = 0


    def img_gen_callback(self):
        self.brightness += 1
        self.img.fill(self.brightness)
        self.img += 1
        cv2.imshow("camera", self.img + self.count)
        if self.img[0, 0] > 255:
            self.count += 1
        



def main(args=None):
    rclpy.init(args=args) #rmw 활성화
    node = M_pub()
    # timer 등록
    try:
        rclpy.spin(node) #블럭 무한루프
    except KeyboardInterrupt:
        node.get_logger().info("키보드 인터럽트")
    finally:
        node.destroy_node()
    print("첫번째 프로그램입니다.")


if __name__ == "__main__":
    main()