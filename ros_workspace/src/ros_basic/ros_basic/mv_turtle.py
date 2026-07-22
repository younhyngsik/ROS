import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import String
from turtlesim.msg import Pose
from turtlesim.msg import Color


class Move_turtle(Node):
    def __init__(self):        
        super().__init__("move_turtle")
        self.create_timer(0.1,self.timer_callback)
        self.pub = self.create_publisher(Twist, "turtle1/cmd_vel", 10)
        self.create_subscription(Pose, "turtle1/pose", self.pose_callback, 10)
        self.create_subscription(Color, "turtle1/color_sensor", self.color_callback, 10)
        self.state = "FORWARD"  # 현재 상태 (직진/회전)
        self.timer_tick = 0     # 시간 카운트
        self.side_count = 0     # 그린 변의 개수
        self.count = 0.0
        self.pose = Pose()
        self.color = Color()
        

    def timer_callback(self):
        msg = Twist
        self.state = "FORWARD"  # 현재 상태 (직진/회전)
        self.timer_tick = 0     # 시간 카운트
        self.side_count = 0     # 그린 변의 개수
        self.count = 0
        self.pub.publish(msg)


    def pose_callback(self, msg : Pose):
        self.pose = msg

    def color_callback(self, msg :Color):
        self.color = msg


def main(args=None):
    rclpy.init(args=args) #rmw 활성화
    node = Move_turtle()
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