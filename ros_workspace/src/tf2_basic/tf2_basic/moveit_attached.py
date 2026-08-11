import os
import sys
import time
import rclpy
from geometry_msgs.msg import Pose
from moveit.core.kinematic_constraints import construct_joint_constraint
from moveit.core.robot_state import RobotState
from moveit.planning import MoveItPy
from moveit_msgs.msg import AttachedCollisionObject, CollisionObject
from rclpy.node import Node
from shape_msgs.msg import SolidPrimitive

class OpenManipulatorMoveItNode(Node):
    def __init__(self):
        super().__init__("open_manipulator_controller")
        
        # 1. 초기화
        self.moveit = MoveItPy(node_name="open_manipulator_moveit_py")
        self.arm = self.moveit.get_planning_component("arm")
        self.gripper = self.moveit.get_planning_component("gripper")
        self.planning_scene_monitor = self.moveit.get_planning_scene_monitor()

        self.object_id = "grasped_box"
        self.attach_link = "end_effector_link"
        self.touch_links = ["end_effector_link", "gripper_left_link", "gripper_right_link"]

        # 포즈 데이터 (관절 값)
        self.poses = {
            "pre_pick_1": {"joint1": -0.946466, "joint2": -0.018407, "joint3": 0.951068, "joint4": 0.966407},
            "pre_pick_2": {"joint1": 0.845223, "joint2": 0.444854, "joint3": 0.412640, "joint4": -0.828349},
            "place": {"joint1": -0.972543, "joint2": 0.444854, "joint3": 0.366621, "joint4": -0.840621}
        }

        # [수정] 충돌 방지를 위해 환경 먼저 구성 후, 타이머로 동작 실행
        self.setup_scene()
        self.timer = self.create_timer(2.0, self.run_task) # 2초 대기 후 실행
        self.executed = False

    def create_pose(self, x=0.0, y=0.0, z=0.0, w=1.0) -> Pose:
        pose = Pose()
        pose.position.x, pose.position.y, pose.position.z = x, y, z
        pose.orientation.w = w
        return pose

    def manage_object(self, object_id, dimensions, pose, operation, frame_id="world", is_attached=False):
        co = CollisionObject()
        co.header.frame_id = frame_id
        co.header.stamp = self.get_clock().now().to_msg()
        co.id = object_id
        co.operation = operation

        if operation != CollisionObject.REMOVE:
            box = SolidPrimitive()
            box.type = SolidPrimitive.BOX
            box.dimensions = dimensions
            co.primitives.append(box)
            co.primitive_poses.append(pose)

        if is_attached:
            aco = AttachedCollisionObject()
            aco.link_name = self.attach_link
            aco.object = co
            aco.touch_links = self.touch_links
            with self.planning_scene_monitor.read_write() as scene:
                scene.process_attached_collision_object(aco)
                scene.current_state.update()
        else:
            self.planning_scene_monitor.process_collision_object(co)

    def setup_scene(self):
        """환경 구성 (충돌 방지를 위해 좌표 수정)"""
        # [수정] table의 z값을 -0.07로 낮춤 (link1과의 충돌 방지)
        self.manage_object("table", [0.8, 0.8, 0.05], self.create_pose(0.25, 0.0, -0.07), CollisionObject.ADD)
        
        # [수정] wall의 x값을 0.4로 밀어냄 (로봇 팔과의 충돌 방지)
        self.manage_object("wall", [0.4, 0.02, 0.3], self.create_pose(0.4, 0.0, 0.1), CollisionObject.ADD)
        
        self.manage_object(self.object_id, [0.04, 0.04, 0.08], self.create_pose(0.2, 0.2, 0.065), CollisionObject.ADD)
        self.get_logger().info("환경 구성 완료")

    def run_task(self):
        if self.executed: return
        self.executed = True
        self.move_manipulator()

    def move_manipulator(self):
        # 1. 초기 자세로 이동 (문자열 방식)
        self.plan_and_execute(self.arm, "init", "arm_controller", "arm")
        
        # 2. 작업 수행 (딕셔너리 방식)
        self.plan_and_execute(self.arm, self.poses["pre_pick_1"], "arm_controller", "arm")
        self.plan_and_execute(self.gripper, "open", "gripper_controller", "gripper")
        self.get_logger().info("시퀀스 완료")

    def plan_and_execute(self, component, configuration, controller_name, group_name) -> bool:
        """[수정] group_name 인자를 직접 받도록 변경"""
        component.set_start_state_to_current_state()
        
        if isinstance(configuration, str):
            component.set_goal_state(configuration_name=configuration)
        else:
            robot_model = self.moveit.get_robot_model()
            robot_state = RobotState(robot_model)
            robot_state.joint_positions = configuration
            
            # [수정] component.name 대신 직접 넘겨받은 group_name 사용
            joint_model_group = robot_model.get_joint_model_group(group_name)
            joint_constraint = construct_joint_constraint(
                robot_state=robot_state, joint_model_group=joint_model_group
            )
            component.set_goal_state(motion_plan_constraints=[joint_constraint])

        plan_result = component.plan()
        if plan_result:
            self.moveit.execute(plan_result.trajectory, controllers=[controller_name])
            return True
        self.get_logger().error(f"계획 실패: {configuration}")
        return False

def main() -> None:
    rclpy.init()
    node = OpenManipulatorMoveItNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()