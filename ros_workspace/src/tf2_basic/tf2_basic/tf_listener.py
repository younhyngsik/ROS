import rclpy
from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from rclpy.time import Time
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener




class M_pub(Node):
    def __init__(self):
        super().__init__("dynamic")  # 노드 이름
        self.target_frame = (
            self.declare_parameter("target_frame", "joint2").get_parameter_value().string_value
            )
        self.source_frame = (
                self.declare_parameter("source_frame", "world").get_parameter_value().string_value
                )
        self.tf_buffer = Buffer()
        self.tf_broadcaster = TransformListener(self.tf_buffer, self)
        self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        try:
            t: TransformStamped = self.tf_buffer.lookup_transform(
                self.target_frame, self.source_frame, Time()
            )
            self.get_logger().info(f"{t}")
        except:
            pass





def main(args=None):
    rclpy.init(args=args)  # rmw 활성화
    node = M_pub()
    try:
        rclpy.spin(node)  # 블럭 (무한 루프)
    except KeyboardInterrupt:
        print("키보드 인터럽트")
    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()