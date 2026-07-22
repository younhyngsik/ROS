import rclpy
from rclpy.node import Node
from std_msgs.msg import Header


class Header_pub(Node):
    def __init__(self):        
        super().__init__("time_pub")
        self.create_timer(1, self.timer_callback)
        self.pub = self.create_publisher(Header, "time", 10)
        self.count = 0

    def timer_callback(self):
        msg = Header() #DDS에 보낼 객체
        msg.frame_id = "time"
        msg.stamp = self.get_clock().now().to_msg()
        self.pub.publish(msg) #DDS로 보내는 기능 수행
        self.count += 1


def main(args=None):
    rclpy.init(args=args) #rmw 활성화
    node = Header_pub()
    # timer 등록
    try:
        rclpy.spin(node) #블럭 무한루프
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
    print("첫번째 프로그램입니다.")


if __name__ == "__main__":
    main()