from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    scan_blockage_judge = Node(
        package='exit_patrol_robot',
        executable='scan_blockage_judge',
        name='scan_blockage_judge',
        output='screen'
    )

    inspection_visualizer = Node(
        package='exit_patrol_robot',
        executable='inspection_visualizer',
        name='inspection_visualizer',
        output='screen'
    )

    corridor_patrol = Node(
        package='exit_patrol_robot',
        executable='corridor_patrol',
        name='corridor_patrol',
        output='screen'
    )

    return LaunchDescription([
        scan_blockage_judge,
        inspection_visualizer,
        corridor_patrol,
    ])
