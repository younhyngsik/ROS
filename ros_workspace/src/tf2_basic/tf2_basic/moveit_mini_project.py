import os
import sys
import math
import time
import rclpy
from geometry_msgs.msg import Pose, Quaternion
from moveit.core.kinematic_constraints import construct_joint_constraint
from moveit.core.robot_state import RobotState
from moveit.planning import MoveItPy
from moveit_msgs.msg import CollisionObject
from rclpy.node import Node
from shape_msgs.msg import SolidPrimitive

class CircularEnvManipulator(Node):
    def __init__(self):
        super().__init__("open_manipulator_controller")
        
        # 1. MoveItPy 초기화
        self.moveit = MoveItPy(node_name="open_manipulator_moveit_py")
        self.arm = self.moveit.get_planning_component("arm")
        self.gripper = self.moveit.get_planning_component("gripper")
        self.planning_scene_monitor = self.moveit.get_planning_scene_monitor()

        # 2. 환경 구축 (바닥 + 벽 6개)
        self.setup_circular_environment()
        
        # 3. 자동 실행 타이머 (2초 뒤 시작)
        self.timer = self.create_timer(2.0, self.run_automatic_patrol)
        self.executed = False

    def setup_circular_environment(self):
        """원형 바닥과 중심을 향하는 6개의 벽 배치"""
        # 원형 바닥 (Cylinder)
        self.manage_primitive(
            "circular_floor", 
            SolidPrimitive.CYLINDER, 
            [0.01, 0.5], # 높이 1cm, 반지름 50cm
            self.create_pose(z=-0.05) # link1 충돌 방지를 위해 낮게 설정
        )

        # 6개의 벽 배치 (중심을 바라보는 방향)
        radius = 0.25  # 로봇 중심에서의 거리
        for i in range(6):
            angle = math.radians(i * 60)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            
            wall_pose = self.create_pose(x, y, 0.08)
            # [수정] 중심을 향하도록 기존 angle에 90도(pi/2)를 더함
            wall_pose.orientation = self.euler_to_quaternion(0, 0, angle + math.pi/2)

            self.manage_primitive(
                f"wall_{i}", 
                SolidPrimitive.BOX, 
                [0.02, 0.15, 0.18], # 두께 2cm, 폭 15cm, 높이 18cm
                wall_pose
            )
        self.get_logger().info("원형 환경 구축 완료 (벽 6개가 중심을 향함)")

    def run_automatic_patrol(self):
        """6개의 벽 사이사이를 자동으로 순회"""
        if self.executed: return
        self.executed = True

        self.get_logger().info("순회 주행을 시작합니다.")
        
        # 6개의 벽 너머 지점들을 관절 각도로 계산
        for i in range(6):
            angle_deg = i * 60
            angle_rad = math.radians(angle_deg)
            
            self.get_logger().info(f"--- {i}번 벽 방향으로 이동 중 ({angle_deg}도) ---")
            
            # 각 벽의 방향에 맞는 관절 목표값 설정
            # joint1을 angle_rad로 맞추어 해당 벽 쪽을 보게 함
            target_pose = {
                "joint1": angle_rad,
                "joint2": 0.4, 
                "joint3": 0.0, 
                "joint4": 0.6
            }
            
            # 이동 실행 (MoveIt이 벽을 피해 경로를 생성함)
            success = self.plan_and_execute(target_pose, "arm")
            
            if success:
                self.get_logger().info(f"{i}번 위치 도달 성공")
                time.sleep(1.0)
            else:
                self.get_logger().warn(f"{i}번 위치 계획 실패, 다음으로 넘어갑니다.")

        self.get_logger().info("모든 구역 순회 완료. 초기 위치로 복귀합니다.")
        self.plan_and_execute("init", "arm")

    # --- 유틸리티 함수 ---

    def manage_primitive(self, object_id, p_type, dimensions, pose):
        co = CollisionObject()
        co.header.frame_id = "world"
        co.id = object_id
        primitive = SolidPrimitive()
        primitive.type = p_type
        primitive.dimensions = dimensions
        co.primitives.append(primitive)
        co.primitive_poses.append(pose)
        co.operation = CollisionObject.ADD
        self.planning_scene_monitor.process_collision_object(co)

    def create_pose(self, x=0.0, y=0.0, z=0.0) -> Pose:
        pose = Pose()
        pose.position.x, pose.position.y, pose.position.z = x, y, z
        pose.orientation.w = 1.0
        return pose

    def euler_to_quaternion(self, roll, pitch, yaw) -> Quaternion:
        qx = math.sin(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) - math.cos(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
        qy = math.cos(roll/2) * math.sin(pitch/2) * math.cos(yaw/2) + math.sin(roll/2) * math.cos(pitch/2) * math.sin(yaw/2)
        qz = math.cos(roll/2) * math.cos(pitch/2) * math.sin(yaw/2) - math.sin(roll/2) * math.sin(pitch/2) * math.cos(yaw/2)
        qw = math.cos(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) + math.sin(roll/2) * math.sin(pitch/2) * math.cos(yaw/2)
        return Quaternion(x=qx, y=qy, z=qz, w=qw)

    def plan_and_execute(self, configuration, group_name) -> bool:
        self.arm.set_start_state_to_current_state()
        
        if isinstance(configuration, str):
            self.arm.set_goal_state(configuration_name=configuration)
        else:
            robot_model = self.moveit.get_robot_model()
            rs = RobotState(robot_model)
            rs.joint_positions = configuration
            joint_model_group = robot_model.get_joint_model_group(group_name)
            joint_constraint = construct_joint_constraint(robot_state=rs, joint_model_group=joint_model_group)
            self.arm.set_goal_state(motion_plan_constraints=[joint_constraint])

        # 장애물 회피를 위해 충분한 계산 시간 부여
        plan_result = self.arm.plan()
        if plan_result:
            self.moveit.execute(plan_result.trajectory, controllers=["arm_controller"])
            return True
        return False

def main():
    rclpy.init()
    node = CircularEnvManipulator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()