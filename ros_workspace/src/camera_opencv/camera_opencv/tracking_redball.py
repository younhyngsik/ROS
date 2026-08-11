import cv2
import numpy as np
import rclpy
from action_msgs.msg import GoalStatus
from control_msgs.action import (
    FollowJointTrajectory,
    FollowJointTrajectory_GetResult_Response,
    GripperCommand,
    GripperCommand_GetResult_Response,
)
from cv_bridge import CvBridge
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.task import Future
from sensor_msgs.msg import Image, JointState
from trajectory_msgs.msg import JointTrajectoryPoint
from builtin_interfaces.msg import Duration

class Manipulator_pub(Node):
    def __init__(self):
        super().__init__("manipulator_pub")
        self.joint_client = ActionClient(
            self, FollowJointTrajectory, "/arm_controller/follow_joint_trajectory"
        )
        self.gripper_client = ActionClient(self, GripperCommand, "/gripper_controller/gripper_cmd")
        self.joint_state_subscription = self.create_subscription(
            JointState, "joint_states", self.joint_callback, 10
        )
        
        # 상태 변수
        self.current_joint_position = [0.0, 0.0, 0.0, 0.0]
        self.joint_names = ["joint1", "joint2", "joint3", "joint4"]
        self.is_moving = False  # 액션 실행 중 플래그
        
        self.brige = CvBridge()
        self.create_subscription(Image, "/gripper_camera/image_raw", self.image_callback, 10)

    def image_callback(self, msg: Image):
        # 1. 이미지 변환 및 전처리
        img_sub = self.brige.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        h, w, _ = img_sub.shape
        center_screen_x = w // 2
        center_screen_y = h // 2

        hsv = cv2.cvtColor(img_sub, cv2.COLOR_BGR2HSV)
        # 빨간색 공 감지 (범위 조정 필요시 수정)
        lower = np.array([0, 100, 100], dtype=np.uint8)
        upper = np.array([10, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower, upper)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours and not self.is_moving:
            contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(contour)
            
            if area > 100:  # 노이즈 방지를 위해 최소 면적 설정
                x, y, w_box, h_box = cv2.boundingRect(contour)
                center_x = x + w_box // 2
                center_y = y + h_box // 2
                
                # 거리 추측 로그 (Area 기반)
                # 면적이 클수록 가깝고 작을수록 멀음
                self.get_logger().info(f"공 감지! 면적(거리 지표): {area:.2f}")

                # 시각화
                cv2.rectangle(img_sub, (x, y), (x + w_box, y + h_box), (0, 255, 0), 2)
                cv2.circle(img_sub, (center_x, center_y), 5, (255, 0, 0), -1)

                # 2. 추적 로직 (P 제어 방식)
                # 에러 계산 (화면 중심과의 거리)
                dx = center_screen_x - center_x
                dy = center_screen_y - center_y
                
                # 게인값 (환경에 따라 0.001 ~ 0.005 사이 조정)
                kp = 0.002 
                
                # 새로운 목표 각도 계산
                new_pos = list(self.current_joint_position)
                
                # X 좌표 기반 좌우 이동 -> joint1
                new_pos[0] += dx * kp 
                
                # Y 좌표 기반 상하 이동 -> joint2~4 (간단한 매핑)
                # 공이 아래(y 증가)에 있으면 로봇도 숙여야 함(joint2 증가 등)
                new_pos[1] -= dy * kp 
                new_pos[2] += dy * (kp * 0.5) # joint3은 보조
                
                # 목표 생성 및 전송
                point = JointTrajectoryPoint()
                point.positions = new_pos
                point.time_from_start = Duration(sec=0, nanosec=200000000) # 0.2초 동안 부드럽게 이동
                
                self.move_joint(point)
                
                # 그리퍼 동작 테스트 (Marked: 움직임 x)
                # 실제 동작을 원치 않으시면 주석처리 하세요.
                # self.move_gripper(-0.01) 

        cv2.imshow("Tracking Frame", img_sub)
        cv2.waitKey(1)

    def joint_callback(self, msg: JointState):
        """joint_states 토픽에서 joint1~4의 순서를 찾아 현재 각도 업데이트"""
        temp_pos = [0.0, 0.0, 0.0, 0.0]
        found_count = 0
        for i, name in enumerate(msg.name):
            if name in self.joint_names:
                idx = self.joint_names.index(name)
                temp_pos[idx] = msg.position[i]
                found_count += 1
        
        if found_count == 4:
            self.current_joint_position = temp_pos
            self.joint_state_received = True

    def move_joint(self, point: JointTrajectoryPoint):
        if not self.joint_client.wait_for_server(timeout_sec=1.0):
            return
        
        self.is_moving = True
        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = self.joint_names
        goal.trajectory.points.append(point)

        send_goal_future = self.joint_client.send_goal_async(goal)
        send_goal_future.add_done_callback(self.goal_joint_callback)

    def goal_joint_callback(self, future: Future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.is_moving = False
            return
        
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_joint_result_callback)

    def get_joint_result_callback(self, future: Future):
        self.is_moving = False # 이동 완료 후 플래그 해제
        self.get_logger().info("이동 완료")

    # --- Gripper Methods ---
    def move_gripper(self, position: float):
        if not self.gripper_client.wait_for_server(timeout_sec=1.0):
            return
        goal = GripperCommand.Goal()
        goal.command.position = float(position)
        goal.command.max_effort = 10.0
        self.gripper_client.send_goal_async(goal)

def main(args=None):
    rclpy.init(args=args)
    node = Manipulator_pub()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()