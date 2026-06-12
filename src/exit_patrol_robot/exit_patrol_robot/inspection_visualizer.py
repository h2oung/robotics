import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from visualization_msgs.msg import Marker


class InspectionVisualizer(Node):
    def __init__(self):
        super().__init__('inspection_visualizer')

        self.state_text = 'WAITING'
        self.zone_text = 'NO_ZONE'

        self.state_sub = self.create_subscription(
            String,
            '/exit_patrol/blockage_state',
            self.state_callback,
            10
        )

        self.zone_sub = self.create_subscription(
            String,
            '/exit_patrol/current_zone',
            self.zone_callback,
            10
        )

        self.marker_pub = self.create_publisher(
            Marker,
            '/exit_patrol/status_marker',
            10
        )

        self.timer = self.create_timer(0.2, self.publish_markers)

        self.get_logger().info('inspection_visualizer started.')

    def state_callback(self, msg: String):
        self.state_text = msg.data

    def zone_callback(self, msg: String):
        self.zone_text = msg.data

    def get_state_name(self):
        return self.state_text.split(',')[0].strip()

    def get_color(self, state):
        if state == 'CONFIRMED_DANGER':
            return (1.0, 0.0, 0.0, 1.0)
        elif state == 'DANGER_CANDIDATE':
            return (1.0, 0.4, 0.0, 1.0)
        elif state == 'CONFIRMED_WARNING':
            return (1.0, 1.0, 0.0, 1.0)
        elif state == 'WARNING_CANDIDATE':
            return (1.0, 0.8, 0.0, 1.0)
        elif state == 'NORMAL':
            return (0.0, 1.0, 0.0, 1.0)
        elif state == 'PATROLLING':
            return (0.2, 0.6, 1.0, 1.0)
        else:
            return (0.5, 0.5, 0.5, 1.0)

    def publish_markers(self):
        state = self.get_state_name()
        color = self.get_color(state)

        self.publish_status_cube(color)
        self.publish_status_text(state, color)

    def publish_status_cube(self, color):
        marker = Marker()
        marker.header.frame_id = 'base_link'
        marker.header.stamp = self.get_clock().now().to_msg()

        marker.ns = 'inspection_status'
        marker.id = 0
        marker.type = Marker.CUBE
        marker.action = Marker.ADD

        marker.pose.position.x = 0.7
        marker.pose.position.y = 0.0
        marker.pose.position.z = 0.45
        marker.pose.orientation.w = 1.0

        marker.scale.x = 0.35
        marker.scale.y = 0.35
        marker.scale.z = 0.35

        marker.color.r = color[0]
        marker.color.g = color[1]
        marker.color.b = color[2]
        marker.color.a = color[3]

        self.marker_pub.publish(marker)

    def publish_status_text(self, state, color):
        marker = Marker()
        marker.header.frame_id = 'base_link'
        marker.header.stamp = self.get_clock().now().to_msg()

        marker.ns = 'inspection_status'
        marker.id = 1
        marker.type = Marker.TEXT_VIEW_FACING
        marker.action = Marker.ADD

        marker.pose.position.x = 0.8
        marker.pose.position.y = 0.0
        marker.pose.position.z = 0.95
        marker.pose.orientation.w = 1.0

        marker.scale.z = 0.22

        marker.color.r = color[0]
        marker.color.g = color[1]
        marker.color.b = color[2]
        marker.color.a = 1.0

        marker.text = f'{self.zone_text}\n{self.state_text}'

        self.marker_pub.publish(marker)


def main(args=None):
    rclpy.init(args=args)
    node = InspectionVisualizer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
