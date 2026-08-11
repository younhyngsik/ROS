import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import TransformStamped, PoseStamped
from tf2_ros import TransformBroadcaster
from cv_bridge import CvBridge
import cv2
import numpy as np
from rclpy.qos import qos_profile_sensor_data
import math

class ArucoPosePublisher(Node):
    def __init__(self):
        super().__init__('aruco_tracker')
        self.br = TransformBroadcaster(self)
        self.bridge = CvBridge()

        # 1. ArUco 설정 (OpenCV 4.6.0 방식)
        self.dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.parameters = cv2.aruco.DetectorParameters_create()
        self.marker_length = 0.04  # 4cm 상자 기준

        # 2. 카메라 매트릭스 (가제보 기본값 기준)
        self.mtx = np.array([[600.0, 0, 320.0], [0, 600.0, 240.0], [0, 0, 1]], dtype=np.float64)
        self.dist = np.zeros((5, 1))

        # 3. 퍼블리셔 추가 (Pose 토픽 발행)
        self.pose_pub = self.create_publisher(PoseStamped, '/aruco_pose', 10)

        # 4. 구독 설정 (Gazebo Sim용 QoS)
        self.subscription = self.create_subscription(
            Image, 
            '/gripper_camera/image_raw', 
            self.image_callback, 
            qos_profile_sensor_data)
            
        self.get_logger().info("ArUco 추적 및 Pose 발행 노드 가동 중")

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 마커 검출
            corners, ids, _ = cv2.aruco.detectMarkers(gray, self.dictionary, parameters=self.parameters)

            if ids is not None:
                # 포즈 추정 (tvec, rvec 추출)
                rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                    corners, self.marker_length, self.mtx, self.dist
                )

                for i in range(len(ids)):
                    rvec, tvec = rvecs[i][0], tvecs[i][0]
                    marker_id = ids[i][0]

                    # 1. 화면 시각화 (축 그리기: 빨강-X, 초록-Y, 파랑-Z)
                    cv2.aruco.drawDetectedMarkers(frame, corners, ids)
                    cv2.drawFrameAxes(frame, self.mtx, self.dist, rvec, tvec, 0.03)

                    # 2. ROS 2 토픽으로 데이터 발행 (PoseStamped)
                    self.publish_pose_topic(marker_id, rvec, tvec)

                    # 3. Dynamic TF 발행 (RViz 확인용)
                    self.publish_dynamic_tf(marker_id, rvec, tvec)

                    # 4. 터미널 출력 (요청사항)
                    print(f"ID: {marker_id} | TVEC: {tvec} | RVEC: {rvec}")
            
            cv2.imshow("Aruco Tracking", frame)
            cv2.waitKey(1)

        except Exception as e:
            self.get_logger().error(f"Error: {e}")

    def publish_pose_topic(self, marker_id, rvec, tvec):
        """tvec, rvec 데이터를 PoseStamped 토픽으로 발행"""
        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'camera_link'
        
        # Position (tvec)
        msg.pose.position.x = tvec[0]
        msg.pose.position.y = tvec[1]
        msg.pose.position.z = tvec[2]

        # Orientation (rvec -> Quaternion)
        qx, qy, qz, qw = self.rvec_to_quaternion(rvec)
        msg.pose.orientation.x = qx
        msg.pose.orientation.y = qy
        msg.pose.orientation.z = qz
        msg.pose.orientation.w = qw

        self.pose_pub.publish(msg)

    def publish_dynamic_tf(self, marker_id, rvec, tvec):
        """TF를 발행하여 RViz에서 좌표축이 보이게 함"""
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'camera_link'
        t.child_frame_id = f'marker_{marker_id}'
        
        t.transform.translation.x = tvec[0]
        t.transform.translation.y = tvec[1]
        t.transform.translation.z = tvec[2]

        qx, qy, qz, qw = self.rvec_to_quaternion(rvec)
        t.transform.rotation.x = qx
        t.transform.rotation.y = qy
        t.transform.rotation.z = qz
        t.transform.rotation.w = qw

        self.br.sendTransform(t)

    def rvec_to_quaternion(self, rvec):
        """Rotation Vector를 Quaternion으로 변환"""
        angle = np.linalg.norm(rvec)
        if angle == 0:
            return 0.0, 0.0, 0.0, 1.0
        axis = rvec / angle
        qx = axis[0] * math.sin(angle/2)
        qy = axis[1] * math.sin(angle/2)
        qz = axis[2] * math.sin(angle/2)
        qw = math.cos(angle/2)
        return qx, qy, qz, qw

def main():
    rclpy.init()
    node = ArucoPosePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()  