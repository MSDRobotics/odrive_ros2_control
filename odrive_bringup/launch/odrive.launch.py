# Copyright 2021 Factor Robotics
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "enable_front_left",
            default_value="true",
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "enable_front_right",
            default_value="true",
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "front_left_controller",
            default_value="front_left_velocity_controller",
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "front_right_controller",
            default_value="front_right_velocity_controller",
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "enable_back_left",
            default_value="true",
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "enable_back_right",
            default_value="true",
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "back_left_controller",
            default_value="back_left_velocity_controller",
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "back_right_controller",
            default_value="back_right_velocity_controller",
        )
    )

    enable_front_left = LaunchConfiguration("enable_front_left")
    enable_front_right = LaunchConfiguration("enable_front_right")
    front_left_controller = LaunchConfiguration("front_left_controller")
    front_right_controller = LaunchConfiguration("front_right_controller")

    enable_back_left = LaunchConfiguration("enable_back_left")
    enable_back_right = LaunchConfiguration("enable_back_right")
    back_left_controller = LaunchConfiguration("back_left_controller")
    back_right_controller = LaunchConfiguration("back_right_controller")

    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [
                    FindPackageShare("odrive_description"),
                    "urdf",
                    "odrive.urdf.xacro",
                ]
            ),
            " ",
            "enable_front_left:=",
            enable_front_left,
            " ",
            "enable_front_right:=",
            enable_front_right,
            " ",
            "enable_back_left:=",
            enable_back_left,
            " ",
            "enable_back_right:=",
            enable_back_right,
        ]
    )
    robot_description = {"robot_description": robot_description_content}

    robot_controllers = PathJoinSubstitution(
        [
            FindPackageShare("odrive_bringup"),
            "config",
            "odrive_controllers.yaml",
        ]
    )

    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_description, robot_controllers],
        output={
            "stdout": "screen",
            "stderr": "screen",
        },
    )

    robot_state_pub_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[robot_description],
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner.py",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )

    front_left_controller_spawner = Node(
        package="controller_manager",
        executable="spawner.py",
        arguments=[front_left_controller, "-c", "/controller_manager"],
        condition=IfCondition(enable_front_left),
    )

    front_right_controller_spawner = Node(
        package="controller_manager",
        executable="spawner.py",
        arguments=[front_right_controller, "-c", "/controller_manager"],
        condition=IfCondition(enable_front_right),
    )

    back_left_controller_spawner = Node(
        package="controller_manager",
        executable="spawner.py",
        arguments=[back_left_controller, "-c", "/controller_manager"],
        condition=IfCondition(enable_back_left),
    )

    back_right_controller_spawner = Node(
        package="controller_manager",
        executable="spawner.py",
        arguments=[back_right_controller, "-c", "/controller_manager"],
        condition=IfCondition(enable_back_right),
    )

    nodes = [
        control_node,
        robot_state_pub_node,
        joint_state_broadcaster_spawner,
        front_left_controller_spawner,
        front_right_controller_spawner,
        back_left_controller_spawner,
        back_right_controller_spawner,
    ]

    return LaunchDescription(declared_arguments + nodes)
