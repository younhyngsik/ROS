import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class M_pub(Node):
    def __init__(self):        
        super().__init__("message_pub")
        self.create_timer(1,self.timer_callback)
        self.pub1 = self.create_publisher(String, "message1", 10)
        self.pub2 = self.create_publisher(String, "message2", 10)
        self.count = 0

    def timer_callback(self):
        msg1 = String() #DDS에 보낼 객체
        msg2 = String()
        msg1.data = f"첫번째 메시지입니다. {self.count}"  #data를 입력
        msg2.data = f"두번째 메시지입니다. {self.count}"
        self.get_logger().info(msg1.data)
        self.get_logger().info(msg2.data)
        self.pub1.publish(msg1)
        self.pub2.publish(msg2) #DDS로 보내는 기능 수행
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