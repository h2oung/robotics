# 🚨 ROS2 기반 TurtleBot3 비상구 및 대피로 차단 점검 로봇

## 팀 정보

| 항목 | 내용      |
| -- | ------- |
| 팀명 | 올라프     |
| 팀원 | 김현영     |
| 학번 | 2371023 |

---

## 프로젝트 소개

ROS2 + Gazebo 시뮬레이션 환경에서 TurtleBot3 Waffle Pi를 이용해 실내 복도의 **비상구·대피로 차단 여부를 자동으로 점검**하는 로봇 시스템입니다.

LiDAR 센서 데이터를 기반으로 전방 장애물을 감지하며, 일시적 감지가 아닌 **지속 감지 기반**으로 위험을 확정하여 오탐을 최소화합니다.

```text
EXIT_1 출발 → CENTER 점검(NORMAL) → EXIT_2 이동 → 장애물 지속 감지 → CONFIRMED_DANGER → 정지
```

---

## 개발 환경

| Category      | Technology           |
| ------------- | -------------------- |
| OS            | Ubuntu 22.04 LTS     |
| ROS           | ROS2 Humble          |
| Simulator     | Gazebo Classic       |
| Robot         | TurtleBot3 Waffle Pi |
| Language      | Python               |
| Visualization | RViz2                |
| Sensor        | LiDAR `/scan`        |

---

## 주요 기능

* **구역 기반 자동 순찰** — 지정 점검 구역에서만 장애물 판단 활성화
* **지속 감지 기반 위험 확정** — 일시 감지는 `CANDIDATE`, 일정 시간 지속 시 `CONFIRMED_DANGER`로 확정
* **RViz Marker 시각화** — 상태별 색상(Blue/Green/Yellow/Orange/Red)으로 직관적 확인

---

## 패키지 구조

```text
exit_patrol_robot/
├── exit_patrol_robot/
│   ├── __init__.py
│   ├── scan_blockage_judge.py     # LiDAR 기반 장애물 판단
│   ├── inspection_visualizer.py   # RViz Marker 시각화
│   ├── corridor_patrol.py         # 자동 순찰 제어
│   └── simple_patrol.py
├── launch/
│   └── inspection.launch.py
├── worlds/
│   ├── exit_corridor.world
│   └── exit_corridor_obstacle.world
├── maps/
│   ├── exit_corridor_map.yaml
│   └── exit_corridor_map.pgm
├── config/
│   └── nav2_params.yaml
├── package.xml
└── setup.py
```

---

## 실행 방법

### 1. 빌드

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select exit_patrol_robot --symlink-install
source install/setup.bash
```

### 2. Gazebo 실행

```bash
export TURTLEBOT3_MODEL=waffle_pi
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/opt/ros/humble/share/turtlebot3_gazebo/models

LIBGL_ALWAYS_SOFTWARE=1 gzserver --verbose \
  -s libgazebo_ros_init.so -s libgazebo_ros_factory.so \
  ~/ros2_ws/src/exit_patrol_robot/worlds/exit_corridor_obstacle.world
```

### 3. 로봇 스폰

```bash
ros2 run gazebo_ros spawn_entity.py \
  -entity waffle_pi \
  -file /opt/ros/humble/share/turtlebot3_gazebo/models/turtlebot3_waffle_pi/model.sdf \
  -x -2.55 -y 0.00 -z 0.05 -Y 0.0
```

### 4. 점검 시스템 실행

```bash
ros2 launch exit_patrol_robot inspection.launch.py
```

### 5. 상태 확인

```bash
ros2 topic echo /exit_patrol/blockage_state
ros2 topic echo /exit_patrol/current_zone
```

---

## 역할 분담

본 프로젝트는 1인 팀으로 진행하였으므로 별도의 역할 분담은 없습니다.

* 프로젝트 주제 선정 및 기획
* ROS2 노드 구현
* Gazebo 시뮬레이션 환경 구성
* LiDAR 기반 장애물 판단 로직 구현
* RViz 시각화 구성
* 데모 촬영 및 제출 자료 정리

---

## AI 사용 여부

* 디버깅 보조
* README 문서 초안 작성 보조

---

## 참고 자료

| 구분    | 자료명                                         | 참고한 내용                                          | 링크                                                                                                        |
| ----- | ------------------------------------------- | ----------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| 공식 문서 | ROS2 Humble Tutorials                       | ROS2 노드, 토픽, launch 실행 방식 참고                    | https://docs.ros.org/en/humble/Tutorials.html                                                             |
| 공식 문서 | TurtleBot3 Simulation                       | TurtleBot3 Waffle Pi 모델 및 Gazebo 시뮬레이션 실행 방식 참고 | https://emanual.robotis.com/docs/en/platform/turtlebot3/simulation/                                       |
| 공식 문서 | Gazebo with ROS2                            | Gazebo와 ROS2 연동 및 시뮬레이션 월드 실행 방식 참고             | https://docs.ros.org/en/humble/Tutorials/Advanced/Simulators/Gazebo/Simulation-Gazebo.html                |
| 공식 문서 | sensor_msgs / LaserScan                     | LiDAR `/scan` 메시지 구조와 거리 데이터 처리 방식 참고           | https://docs.ros.org/en/humble/p/sensor_msgs/                                                             |
| 공식 문서 | RViz Marker Display Types                   | RViz Marker를 이용한 점검 상태 시각화 방식 참고                | https://docs.ros.org/en/humble/Tutorials/Intermediate/RViz/Marker-Display-types/Marker-Display-types.html |
| 뉴스 기사 | KBS 뉴스 - ‘제천 참사’ 겪고도…비상구 관리 여전히 엉망          | 비상구 관리 부실 사례 및 프로젝트 주제 배경 참고                    | https://news.kbs.co.kr/news/pc/view/view.do?ncd=3612239                                                   |
| 뉴스 기사 | YTN - ‘화재로 10명 부상’ 소공동 호텔, 과거 ‘비상구 적치물’ 신고돼 | 비상구 적치물 문제 및 대피로 차단 사례 참고                       | https://www.ytn.co.kr/_ln/0103_202603181754183220                                                         |


---

## YouTube 링크

* https://www.youtube.com/watch?v=ElgCcUDCmIM

---

## GitHub 링크

* https://github.com/h2oung/robotics.git

