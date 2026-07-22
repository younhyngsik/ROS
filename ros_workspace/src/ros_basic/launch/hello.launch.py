from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
        Node(package="ros_basic", executable="class_pub"),
        Node(package="ros_basic", executable="class_sub"),
        Node(package="ros_basic", executable="class2_sub"),
        Node(package="ros_basic", executable="time_pub"),
        Node(package="ros_basic", executable="time_sub"),
        ]
    )