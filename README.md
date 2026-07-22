# kongju_ROS

--------
0720


ros 환경 구축
-WSL을 통한 vscode로 Ubuntu 접속
ros2를 vscode를 통하여 기본적인 turtlesim 구현
-topic, service, action과 같은 기초 패턴 구현

CLI
ros2 run => 실행 명령어
ros2 node => 노드의 ~
ros2 topic echo/pub/sub/bw/hz => 토픽 정보
ros2 service call => 서비스 실행
ros2 action send_goal => 
ros2 interface proto => 인터페이스 확인

GUI (QT)
rqt => 실행
graph => 노드끼리의 연결을 직관적으로 확인
CLI와 대응대는 위젯들 => 

ros2 param => 프로세서들의 변수, 환경변수
background_r/g/b/ 불러와서 .yaml로 저장 -> 불러와서 사용 가능

---------------
0721

os linux, cloud, 노트북 등에 ros2를 설치해서 DDS로 통신 -> 분산구조 용이
os에서 센서나 액추에이터 구동 시 병목현상으로 리얼타임 보장 한계 -> MCU로 별도 제어 

ros2 common package
Buildsystem, RMW, RCL, Utility, ROS Interface pipeline, Interface definitions, Launch, Featues, Robots ~~

DDS(Data Distribution Service): OMG에서 표준화한 통신 미들웨어 -> RTPS, UDP(피드백 없어서 반응 빠름) 기반이되 TCP(반응 느림) 선택적으로 사용가능
-> 데이터 	
Topic: 비동기식 
Service: 동기식
Action: 비동기식, 동기식 양방향 메시지 송수신 

노드마다 루프 돌다가 신호에 반응



실습
ros2 pkg create --build-type ament_python ros_basic => 패키지 폴더 생성
colcon build => build, install, log(기본 폴더들) 생성

ros2 launch ros_basic hello.launch.py

-----------------------
0722
Header -> 보통 시간 표현
->getclock 후 msg타입으로 변경 후 stamp로 받아옴

launch 사용법 -> setup.py(데이터 추가)

turtlesim를 Twist타입으로 제어(launch를 실행하여 제어)
발행-액추에이터(코드 필요), 구독-센서(업데이트만)



ROS2: DDS의 인식이 subnet -> 같아야 함
subnet -> ifconfig: 앞 세문단이 같으면 같은 랜(리눅스)
ipconfig: (윈도우)

랜과 ip 다른 걸 해결 ->
1. WSL -> window 포트포워딩
2. WSL 방화벽 ufw
3. window 방화벽 defener (in-band/out-vand)

ROS_DOMAIN_ID 같아야 연결
->.bashrc에 export ROS_DOMAIN_ID=~

QoS 중 주요 설정
durability: KEEP_ALL/KEEP_LAST -> 모든 데이터 보관/depth만큼만 보관
history: BEST_EFFORT/RELIABLE -> 속도 중시/데이터 수신에 집중
relibility: TRANSIENT_LOCAL/VOLATILE -> 생성 이전의 데이터 보관/이전 데이터는 무시

단위: mks,A,Radian,Hz,Celcious
좌표 표현 방식:
반시계방향이 정방향
좌표계는 x, y, z를 RED, GREEN, BLUE로 표현 ENU를 기준으로 함(East, Nourth, Up)
좌표계의 표현 방식이 다르면 접미사로 _optical, _ned를 붙여서 구분(좌표계 변경)

시간: stamp, frame id 를 포함하여 토픽을 발행 -> 보통 Header로 명칭
ROS_TIME: 노드가 생성될 때 기준 시간 -> Use_sin_time: True면 /clock이라는 토픽 발행
SYSTEM_TIME
STEADY_TIME


pkg 생성: ros2 pkg create --build-type ament_cmake 이름

interface
service

ros2 launch ros_basic param.launch.py param_dir: my_param2.yaml
