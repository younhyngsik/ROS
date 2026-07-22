import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class M_sub(Node):
    def __init__(self):        
        super().__init__("message1_sub")
        # subscription 등록
        self.create_subscription(String, "message1", self.sub_callback, 10)
        self.count = 0


    def sub_callback(self, msg: String):
        self.get_logger().info(msg.data)


def main(args=None):
    rclpy.init(args=args) #rmw 활성화
    node = M_sub()
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