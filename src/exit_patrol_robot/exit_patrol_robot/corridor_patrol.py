import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String, Bool


class CorridorPatrol(Node):
    def __init__(self):
        super().__init__('corridor_patrol')

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.zone_pub = self.create_publisher(String, '/exit_patrol/current_zone', 10)
        self.target_pub = self.create_publisher(String, '/exit_patrol/inspection_target', 10)
        self.active_pub = self.create_publisher(Bool, '/exit_patrol/inspection_active', 10)

        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.blockage_sub = self.create_subscription(
            String,
            '/exit_patrol/blockage_state',
            self.blockage_callback,
            10
        )

        # 실제 월드 마커 좌표:
        # EXIT_1  = (-3.5, 0.0)
        # CENTER  = (0.0, 0.0)
        # EXIT_2  = (3.5, 0.0)
        # OBSTACLE = (3.2, 0.0)
       
        # 로봇은 EXIT_1 근처에서 스폰
        # → CENTER로 직진
        # → CENTER 점검
        # → EXIT_2로 직진
        # → 장애물 감지
        # → CONFIRMED_DANGER
      
        self.steps = [
            {
                'name': 'CENTER',
                'x': 0.00,
                'y': 0.00,
                'yaw': 0.0,
                'inspect': True
            },
            {
                'name': 'EXIT_2',
                'x': 2.45,
                'y': 0.00,
                'yaw': 0.0,
                'inspect': True
            },
            {
                'name': 'CENTER_RETURN',
                'x': 0.00,
                'y': 0.00,
                'yaw': math.pi,
                'inspect': False
            },
            {
                'name': 'EXIT_1_RETURN',
                'x': -2.55,
                'y': 0.00,
                'yaw': 0.0,
                'inspect': False
            },
        ]

        self.current_index = 0

        self.x = None
        self.y = None
        self.yaw = None

        self.front_min_distance = None

        self.mode = 'MOVE'
        self.mode_start_time = None

        self.goal_tolerance = 0.18
        self.yaw_tolerance = 0.18

        self.inspection_duration_sec = 4.0

        # EXIT_2로 가는 중 장애물이 가까우면 목표점까지 가지 않고 점검 시작
        self.obstacle_inspection_distance = 1.15

        self.last_blockage_state = 'UNKNOWN'

        self.timer = self.create_timer(0.1, self.control_loop)

        self.get_logger().info('corridor_patrol started.')
        self.get_logger().info('Straight-line patrol demo: EXIT_1 start -> CENTER -> EXIT_2.')

    def odom_callback(self, msg: Odometry):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation
        self.yaw = self.quaternion_to_yaw(q.x, q.y, q.z, q.w)

    def scan_callback(self, msg: LaserScan):
        self.front_min_distance = self.get_front_min_distance(msg)

    def blockage_callback(self, msg: String):
        self.last_blockage_state = msg.data

        if self.mode == 'INSPECT' and msg.data.startswith('CONFIRMED_DANGER'):
            step = self.steps[self.current_index]

            # 데모에서는 EXIT_2의 빨간 장애물만 최종 차단으로 처리
            if step['name'] == 'EXIT_2':
                self.get_logger().error(f'Blocked confirmed at {step["name"]}: {msg.data}')
                self.set_mode('BLOCKED_STOP')
            else:
                self.get_logger().warn(
                    f'DANGER detected at {step["name"]}, but continue demo: {msg.data}'
                )

    def get_front_min_distance(self, msg: LaserScan):
        values = []

        for i, distance in enumerate(msg.ranges):
            if math.isinf(distance) or math.isnan(distance):
                continue

            angle = msg.angle_min + i * msg.angle_increment
            angle_deg = math.degrees(angle)
            angle_deg = (angle_deg + 180.0) % 360.0 - 180.0

            # 로봇 정면 ±45도만 확인
            if -45.0 <= angle_deg <= 45.0:
                if msg.range_min <= distance <= msg.range_max:
                    values.append(distance)

        if not values:
            return msg.range_max

        return min(values)

    def quaternion_to_yaw(self, x, y, z, w):
        siny_cosp = 2.0 * (w * z + x * y)
        cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
        return math.atan2(siny_cosp, cosy_cosp)

    def normalize_angle(self, angle):
        return math.atan2(math.sin(angle), math.cos(angle))

    def now_sec(self):
        return self.get_clock().now().nanoseconds / 1e9

    def set_mode(self, mode):
        self.mode = mode
        self.mode_start_time = self.now_sec()

    def elapsed_in_mode(self):
        if self.mode_start_time is None:
            return 0.0
        return self.now_sec() - self.mode_start_time

    def publish_status(self, zone_text, target_name, active):
        zone_msg = String()
        zone_msg.data = zone_text
        self.zone_pub.publish(zone_msg)

        target_msg = String()
        target_msg.data = target_name
        self.target_pub.publish(target_msg)

        active_msg = Bool()
        active_msg.data = active
        self.active_pub.publish(active_msg)

    def stop_robot(self):
        cmd = Twist()
        self.cmd_pub.publish(cmd)

    def move_to_pose_position(self, target_x, target_y):
        cmd = Twist()

        dx = target_x - self.x
        dy = target_y - self.y

        distance = math.hypot(dx, dy)
        target_yaw = math.atan2(dy, dx)
        yaw_error = self.normalize_angle(target_yaw - self.yaw)

        if abs(yaw_error) > 0.30:
            cmd.linear.x = 0.0
            cmd.angular.z = max(min(1.2 * yaw_error, 0.50), -0.50)
        else:
            cmd.linear.x = min(0.12, max(0.04, 0.35 * distance))
            cmd.angular.z = max(min(1.2 * yaw_error, 0.30), -0.30)

        self.cmd_pub.publish(cmd)
        return distance

    def align_to_yaw(self, target_yaw):
        cmd = Twist()

        yaw_error = self.normalize_angle(target_yaw - self.yaw)

        if abs(yaw_error) > self.yaw_tolerance:
            cmd.linear.x = 0.0
            cmd.angular.z = max(min(1.2 * yaw_error, 0.45), -0.45)
            self.cmd_pub.publish(cmd)
            return False

        self.stop_robot()
        return True

    def next_step(self):
        self.current_index = (self.current_index + 1) % len(self.steps)
        self.set_mode('MOVE')

    def control_loop(self):
        if self.x is None or self.y is None or self.yaw is None:
            return

        step = self.steps[self.current_index]
        name = step['name']

        if self.mode == 'BLOCKED_STOP':
            self.stop_robot()
            self.publish_status(f'BLOCKED_AT_{name}', name, True)
            return

        if self.mode == 'MOVE':
            self.publish_status(f'MOVING_TO_{name}', name, False)
            
            if (
                name == 'EXIT_2'
                and self.front_min_distance is not None
                and self.front_min_distance < self.obstacle_inspection_distance
            ):
                self.stop_robot()
                self.get_logger().warn(
                    f'Obstacle detected before reaching {name}. '
                    f'Start inspection here. front={self.front_min_distance:.2f}m'
                )
                self.set_mode('ALIGN')
                return

            distance = self.move_to_pose_position(step['x'], step['y'])

            if distance < self.goal_tolerance:
                self.stop_robot()

                if step['inspect']:
                    self.get_logger().info(f'Arrived near {name}. Aligning to inspect zone.')
                    self.set_mode('ALIGN')
                else:
                    self.next_step()

            return

        if self.mode == 'ALIGN':
            self.publish_status(f'ALIGNING_TO_{name}', name, False)

            aligned = self.align_to_yaw(step['yaw'])

            if aligned:
                self.get_logger().info(
                    f'Aligned to {name}. Start inspection for {self.inspection_duration_sec}s.'
                )
                self.set_mode('INSPECT')

            return

        if self.mode == 'INSPECT':
            self.stop_robot()
            self.publish_status(f'INSPECTING_{name}', name, True)

            if self.elapsed_in_mode() >= self.inspection_duration_sec:
                self.get_logger().info(
                    f'Inspection finished at {name}. Last state: {self.last_blockage_state}'
                )
                self.next_step()

            return


def main(args=None):
    rclpy.init(args=args)
    node = CorridorPatrol()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.stop_robot()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
