import rclpy
from rclpy.node import Node
from std_msgs.msg import Header
from std_msgs.msg import String


class TimeSub(Node):
    def __init__(self):
        super().__init__("time_sub")
        
        self.create_subscription(String, "message1", self.msg1_callback, 10)
        self.create_subscription(Header, "time", self.time_callback, 10)
    
    def time_callback(self, msg):
        seconds = msg.stamp.sec
        
        self.get_logger().info(f"수신 시간: {seconds}")


    def msg1_callback(self, msg):
        self.get_logger().info(f"[MSG1] 수신: {msg.data}")


def main(args=None):
    rclpy.init(args=args)
    node = TimeSub()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("프로그램 종료")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()