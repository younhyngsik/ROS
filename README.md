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

sb
cb
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
SYSTEM_TIME: 
STEADY_TIME: 

pkg 생성: ros2 pkg create --build-type ament_cmake 이름

interface
service

ros2 launch ros_basic param.launch.py param_dir: my_param2.yaml

--------------------------------------
0723

DDS 설정 -> WSL로 mirror-net -> 방화벽 해제
interface(Type) 로 만든 변수 => message(Topic, service, action) -> qos로 DDS에 전송
interface: ros2가 기본 제공, user.interface 생성 가능(idl문법: 구분자가 ---, Topic은 한 덩어리라 구분자 x) 
-> cmake 패키지 필요,

Topic(UserInt), Service(AddAndOdd) 사용
service: server와 client간의 UDP 통신(TCP는 아니지만 비슷하게 구현: RPC) => 기본 비동기 방식 => 외부 변화 상관없이 내부 스레드 항상 구동
server와 client는 각각 특정 노드에 설정
thread_server: 순차적, service 두개일 때 사용

Topic이나 Service나 message를 보낸다는 것은 동일
topic은 보통 주기적인(반복적인) 센서 확인에 사용(리소스 계속 사용), service는 보통 특정 상황에 반응할 때 사용

parameter: 변수를 프로세서 여러개에 운용할 때 사용 -> 보통 환경변수에 .yaml로 많이 사용
내부 변수와 파라미터 변수는 독립적: 외부에서 파라미터 변수를 바꿔도 내부 변수는 동일
->add_on_set_parameter 코드 추가해야 내부 변수 변화 -> 외부 노드(Asyncparameter 코드)나 CLI에서 DDS로 변경

launch: 노드 여러개, 파라미터 로드(파라미터나 보통 .yaml 파일 붙여넣기)





action client와 action server는 동기식 양방향 송수신
action goal과 action result를 양방향으로 송수신하고 중간 과정인 action feedback 을 server에서 client로 전송(Topic으로)
			topic		service	action
연속성		연속성	일회성	복합
방향성		단방향	양방향	양방향
동기성		비동기	동기		동기 + 비동기
다자간 연결 	1:1 ~N:N	1:1		1:1
노드 역할		발행/구독자 	서버/클라이언트
동작 트리거 	발행자		클라이언트
인터페이스		msg		srv		action
사용 예		센서 데이터, 로봇 상태, 좌표, 속도 명령		LED 제어, 모터 토크 on/off, 이동 경로 계산		목적지 이동, 물건 파지, 복합 업무


------------------------
0724
action: IDL로 구현(goal, result, feedback) -> build
msg 비교: topic, service, action의 각 특징 비교
action_server의 노드 생성 -> Node class로 인자 넘겨서 순차처리
action_client: 비동기 코드 => callback 함수 필요(response, result, feedback_callback)
action_thread_server: action_server의 순차처리가 비효율적이므로 thread로 구동
action_client의 cancel 요청 -> action_server에서 cancel
				     <- 			  abort 전송: cancel과 다르게 result 바로 출력

namespace: 하나의 노드로 여러개의 프로세스 구현 => 하나의 노드로 프로세스 만들 때 원래는 토픽과 프로세스 이름이 서로 동일 => 충돌
-> 이를 방지하기 위해 namespace로 다른 이름의 토픽과 프로세스 생성 
namespace => .launch로 생성

tf2: /tf.static, /tf를 발행하는데 특화된 라이브러리 
->x, y, z(linear), x, y, z, w(angular) 총 7개로 구성
/tf.static => 한번 발행하면 DDS에 상주
/tf => 계속 발행 -> 직전의 tf와만 연결되어야 하므로 Header.stamp 중요(시간 체크)
-> turtlesim pose subscription -> tf 발행 







URDF<xml> => 실제로 사용하는
->joint_stat_publisher를 사용해
1. tf 발행
2. /robot_descriptor 토픽 
로 riviz2에서 표현
다만 기본적인 정보밖에 못 넣어서 시뮬에서 사용하기는 부적합(물리적 정보 부족)

simulation(gzsim): SDF<xml> 사용


#팔 추가해서 엘보우 구현(revolute)
#05_add_arm.urdf
#tf 발행해서 직접 동작 -> ros2 run tf2_basic move.u2d2 
