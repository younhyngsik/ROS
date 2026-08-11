import rclpy
import random
import time
from rclpy.node import Node
from rclpy.action import ActionServer, ActionClient, GoalResponse, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from example_interfaces.action import Fibonacci
from control_msgs.action import GripperCommand
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from sensor_msgs.msg import JointState

class DancingManipulatorServer(Node):
    def __init__(self):
        super().__init__("dancing_manipulator_server")
        self.callback_group = ReentrantCallbackGroup()

        # 1. 조인트 상태 구독
        self.joint_sub = self.create_subscription(
            JointState, "joint_states", self.joint_callback, 10,
            callback_group=self.callback_group
        )

        # 2. 제어 퍼블리셔 및 그리퍼 클라이언트
        self.joint_pub = self.create_publisher(JointTrajectory, "arm_controller/joint_trajectory", 10)
        self.gripper_client = ActionClient(self, GripperCommand, "/gripper_controller/gripper_cmd", callback_group=self.callback_group)

        # 3. 액션 서버 설정 (취소 수락 함수 cancel_callback 추가)
        self._action_server = ActionServer(
            self, Fibonacci, "dance_robot", 
            execute_callback=self.execute_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.callback_group
        )

        # 사용자 설정 변수
        self.EFFORT_THRESHOLD = 240.0   
        self.collision_detected = False 
        self.current_positions = [0.0, 0.0, 0.0, 0.0] 

        self.get_logger().info("춤추는 로봇 서버 가동 (Ctrl+C 시 홈 복귀 설정됨)")

    def cancel_callback(self, goal_handle):
        """ 클라이언트에서 Ctrl+C 발생 시 취소 요청을 수락함 """
        self.get_logger().warn("취소 요청 수락됨!")
        return CancelResponse.ACCEPT

    def move_to_home(self):
        """ 로봇을 0,0,0,0 위치로 천천히 복귀 """
        self.get_logger().info("원위치(Home)로 복귀 중...")
        msg = JointTrajectory()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.joint_names = ["joint1", "joint2", "joint3", "joint4"]
        
        point = JointTrajectoryPoint()
        point.positions = [0.0, 0.0, 0.0, 0.0] 
        point.time_from_start.sec = 3  # 3초 동안 천천히 이동
        
        msg.points.append(point)
        self.joint_pub.publish(msg)
        
        # 그리퍼도 초기화
        goal = GripperCommand.Goal()
        goal.command.position = 0.01 
        self.gripper_client.send_goal_async(goal)

    def joint_callback(self, msg: JointState):
        self.current_positions = msg.position 
        for effort_val in msg.effort:
            if abs(effort_val) > self.EFFORT_THRESHOLD:
                self.collision_detected = True

    async def execute_callback(self, goal_handle):
        n_steps = goal_handle.request.order
        is_infinite = (n_steps == 0)
        current_count = 0
        self.collision_detected = False

        self.get_logger().info("춤 시작!")

        while is_infinite or (current_count < n_steps):
            # [핵심] 취소 체크: Ctrl+C가 눌렸는지 확인
            if goal_handle.is_cancel_requested:
                self.get_logger().error("사용자가 종료함! 원위치로 돌아갑니다.")
                self.move_to_home() # 즉시 홈으로 이동 명령
                goal_handle.canceled()
                return Fibonacci.Result()

            # 충돌 체크
            if self.collision_detected:
                self.get_logger().error("충돌 감지! 정지합니다.")
                goal_handle.abort()
                return Fibonacci.Result()

            # --- 무작위 춤 동작 (사용자 범위 설정) ---
            current_count += 1
            random_joints = [
                random.uniform(-1.0, 1.0), # J1
                random.uniform(-1.0, 0.0), # J2
                random.uniform(-1.0, 0.5), # J3
                random.uniform(-1.0, 1.0)  # J4
            ]
            
            # 1.5초 동안 이동
            self.publish_movement(random_joints)
            await self.move_gripper(random_gripper := random.uniform(0.0, 0.018))

            # 피드백 전송
            feedback_msg = Fibonacci.Feedback()
            feedback_msg.sequence = [current_count]
            goal_handle.publish_feedback(feedback_msg)

            # [핵심] 대기 시간(2초)을 0.1초씩 나눠서 취소를 감지
            # 단순히 time.sleep(2.0)을 하면 Ctrl+C 반응이 2초간 씹힘
            for _ in range(20): # 0.1초 * 20 = 2초
                if goal_handle.is_cancel_requested:
                    break # 대기 중이라도 취소가 오면 즉시 루프 탈출
                time.sleep(0.1)

        # 정상 종료 시에도 홈 복귀
        self.get_logger().info("공연 완료! 홈으로 복귀.")
        self.move_to_home()
        goal_handle.succeed()
        return Fibonacci.Result()

    def publish_movement(self, positions):
        msg = JointTrajectory()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.joint_names = ["joint1", "joint2", "joint3", "joint4"]
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start.sec = 1
        point.time_from_start.nanosec = 500_000_000 # 1.5초
        msg.points.append(point)
        self.joint_pub.publish(msg)

    async def move_gripper(self, position):
        if not self.gripper_client.wait_for_server(timeout_sec=1.0): return
        goal = GripperCommand.Goal()
        goal.command.position = position
        await self.gripper_client.send_goal_async(goal)

def main(args=None):
    rclpy.init(args=args)
    node = DancingManipulatorServer()
    executor = MultiThreadedExecutor()
    try:
        rclpy.spin(node, executor=executor)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()