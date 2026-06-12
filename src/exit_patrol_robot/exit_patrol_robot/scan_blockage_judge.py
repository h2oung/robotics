import math

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import LaserScan
from std_msgs.msg import String, Bool


class ScanBlockageJudge(Node):
    def __init__(self):
        super().__init__('scan_blockage_judge')

        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.inspection_active_sub = self.create_subscription(
            Bool,
            '/exit_patrol/inspection_active',
            self.inspection_active_callback,
            10
        )

        self.target_sub = self.create_subscription(
            String,
            '/exit_patrol/inspection_target',
            self.target_callback,
            10
        )

        self.state_pub = self.create_publisher(
            String,
            '/exit_patrol/blockage_state',
            10
        )

        self.raw_state_pub = self.create_publisher(
            String,
            '/exit_patrol/raw_blockage_state',
            10
        )

        # 구역 앞에서 바라보는 방향 기준 전방 ±60도 검사
        self.front_angle_deg = 60.0

        # 데모용 기준
        self.warning_distance = 1.8
        self.danger_distance = 1.4

        # 이 시간 이상 지속되어야 확정
        self.confirm_duration_sec = 2.0

        self.inspection_active = False
        self.current_target = 'NONE'

        self.candidate_state = 'NORMAL'
        self.candidate_start_time = None
        self.confirmed_state = 'NORMAL'

        self.get_logger().info('scan_blockage_judge started with zone-based persistent detection.')

    def inspection_active_callback(self, msg: Bool):
        if self.inspection_active != msg.data:
            self.reset_candidate()

        self.inspection_active = msg.data

    def target_callback(self, msg: String):
        if self.current_target != msg.data:
            self.reset_candidate()

        self.current_target = msg.data

    def reset_candidate(self):
        self.candidate_state = 'NORMAL'
        self.candidate_start_time = None
        self.confirmed_state = 'NORMAL'

    def normalize_angle_deg(self, angle_deg):
        return (angle_deg + 180.0) % 360.0 - 180.0

    def scan_callback(self, msg: LaserScan):
        # 순찰 이동 중에는 확정 판단하지 않음
        if not self.inspection_active:
            result_msg = String()
            result_msg.data = (
                f'PATROLLING, target={self.current_target}, '
                f'raw=IDLE, min_front_distance=-1.00m, duration=0.0s'
            )
            self.state_pub.publish(result_msg)
            return

        min_distance = self.get_front_min_distance(msg)
        raw_state = self.classify_raw_state(min_distance)

        now = self.get_clock().now()
        confirmed_state, duration = self.update_persistent_state(raw_state, now)

        raw_msg = String()
        raw_msg.data = (
            f'{raw_state}, target={self.current_target}, '
            f'min_front_distance={min_distance:.2f}m'
        )
        self.raw_state_pub.publish(raw_msg)

        result_msg = String()
        result_msg.data = (
            f'{confirmed_state}, '
            f'target={self.current_target}, '
            f'raw={raw_state}, '
            f'min_front_distance={min_distance:.2f}m, '
            f'duration={duration:.1f}s'
        )
        self.state_pub.publish(result_msg)

        self.get_logger().info(result_msg.data)

    def get_front_min_distance(self, msg: LaserScan):
        front_ranges = []

        for i, distance in enumerate(msg.ranges):
            if math.isinf(distance) or math.isnan(distance):
                continue

            angle = msg.angle_min + i * msg.angle_increment
            angle_deg = self.normalize_angle_deg(math.degrees(angle))

            if -self.front_angle_deg <= angle_deg <= self.front_angle_deg:
                if msg.range_min <= distance <= msg.range_max:
                    front_ranges.append(distance)

        if not front_ranges:
            return msg.range_max

        return min(front_ranges)

    def classify_raw_state(self, min_distance):
        if min_distance < self.danger_distance:
            return 'DANGER'
        elif min_distance < self.warning_distance:
            return 'WARNING'
        else:
            return 'NORMAL'

    def update_persistent_state(self, raw_state, now):
        if raw_state == 'NORMAL':
            self.reset_candidate()
            return 'NORMAL', 0.0

        if raw_state != self.candidate_state:
            self.candidate_state = raw_state
            self.candidate_start_time = now
            return f'{raw_state}_CANDIDATE', 0.0

        if self.candidate_start_time is None:
            self.candidate_start_time = now
            return f'{raw_state}_CANDIDATE', 0.0

        duration = (now - self.candidate_start_time).nanoseconds / 1e9

        if duration >= self.confirm_duration_sec:
            self.confirmed_state = f'CONFIRMED_{raw_state}'
            return self.confirmed_state, duration

        return f'{raw_state}_CANDIDATE', duration


def main(args=None):
    rclpy.init(args=args)
    node = ScanBlockageJudge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
