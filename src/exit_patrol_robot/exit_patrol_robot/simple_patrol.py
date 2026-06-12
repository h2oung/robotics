import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


class SimplePatrol(Node):
    def __init__(self):
        super().__init__('simple_patrol')

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.front_min_distance = None
        self.left_clearance = None
        self.right_clearance = None

        self.warning_distance = 1.5
        self.danger_distance = 1.0

        self.timer = self.create_timer(0.1, self.control_loop)

        self.get_logger().info('simple_patrol node started.')

    def normalize_angle_deg(self, angle_deg):
        return (angle_deg + 180.0) % 360.0 - 180.0

    def get_min_range(self, msg, min_deg, max_deg):
        values = []

        for i, distance in enumerate(msg.ranges):
            if math.isinf(distance) or math.isnan(distance):
                continue

            angle = msg.angle_min + i * msg.angle_increment
            angle_deg = self.normalize_angle_deg(math.degrees(angle))

            if min_deg <= angle_deg <= max_deg:
                if msg.range_min <= distance <= msg.range_max:
                    values.append(distance)

        if not values:
            return msg.range_max

        return min(values)

    def scan_callback(self, msg: LaserScan):
        self.front_min_distance = self.get_min_range(msg, -60.0, 60.0)
        self.left_clearance = self.get_min_range(msg, 40.0, 130.0)
        self.right_clearance = self.get_min_range(msg, -130.0, -40.0)

    def choose_turn_direction(self):
        left = self.left_clearance if self.left_clearance is not None else 0.0
        right = self.right_clearance if self.right_clearance is not None else 0.0

        if left >= right:
            return 1.0
        else:
            return -1.0

    def control_loop(self):
        cmd = Twist()

        if self.front_min_distance is None:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
            self.cmd_pub.publish(cmd)
            self.get_logger().warn('No scan received yet. Stop.')
            return

        turn_direction = self.choose_turn_direction()

        if self.front_min_distance < self.danger_distance:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.65 * turn_direction
            state = 'DANGER: stop and turn'

        elif self.front_min_distance < self.warning_distance:
            cmd.linear.x = 0.04
            cmd.angular.z = 0.35 * turn_direction
            state = 'WARNING: slow forward and avoid'

        else:
            cmd.linear.x = 0.14
            cmd.angular.z = 0.0
            state = 'NORMAL: forward'

        self.cmd_pub.publish(cmd)

        self.get_logger().info(
            f'{state}, '
            f'front={self.front_min_distance:.2f}m, '
            f'left={self.left_clearance:.2f}m, '
            f'right={self.right_clearance:.2f}m'
        )


def main(args=None):
    rclpy.init(args=args)
    node = SimplePatrol()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    stop_cmd = Twist()
    node.cmd_pub.publish(stop_cmd)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
