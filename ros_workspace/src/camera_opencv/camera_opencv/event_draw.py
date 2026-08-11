import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
from camera_opencv import color
import sys

class GStreamerDrawingNode(Node):
    def __init__(self):
        super().__init__('gstreamer_drawing_node')
        self.publisher = self.create_publisher(Image, 'camera_image', 10)
        self.bridge = CvBridge()

        pipeline = (
            "v4l2src device=/dev/video0 ! "
            "image/jpeg,width=640,height=480,framerate=30/1 ! "
            "jpegdec ! "
            "videoconvert ! "
            "video/x-raw,format=BGR ! "
            "appsink drop=true sync=false"
        )
        self.cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

        if not self.cap.isOpened():
            self.get_logger().error("카메라를 열 수 없습니다.")
            sys.exit()

        # 2. 드로잉 관련 변수
        self.canvas = np.zeros((480, 640, 3), dtype=np.uint8) 
        self.is_drawing = False
        self.old_x, self.old_y = 0, 0
        
        # 3. 색상 설정 (color.py의 COLORS 활용)
        self.color_list = list(color.COLORS.values())
        self.color_names = list(color.COLORS.keys())
        self.color_idx = 0
        
        # 4. 윈도우 생성 및 마우스 콜백 설정
        cv2.namedWindow("GStreamer Paint")
        cv2.setMouseCallback("GStreamer Paint", self.on_mouse)

        # 5. 주기적 실행을 위한 타이머
        self.timer = self.create_timer(0.03, self.timer_callback)
        self.get_logger().info("실행 완료: 스페이스바로 색상 변경, 마우스로 그리기")

    def on_mouse(self, event, x, y, flags, param):
        """마우스 이벤트 처리 함수"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.is_drawing = True
            self.old_x, self.old_y = x, y
            # 클릭 시 작은 점 하나 찍기
            cv2.circle(self.canvas, (x, y), 2, self.color_list[self.color_idx], -1)

        elif event == cv2.EVENT_MOUSEMOVE:
            if flags & cv2.EVENT_FLAG_LBUTTON: # 드래그 중일 때
                # 도화지(canvas)에 선 그리기
                cv2.line(self.canvas, (self.old_x, self.old_y), (x, y), 
                         self.color_list[self.color_idx], 3, cv2.LINE_AA)
                self.old_x, self.old_y = x, y

        elif event == cv2.EVENT_LBUTTONUP:
            self.is_drawing = False

    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # 6. 카메라 영상과 도화지 합성
        # 도화지에서 선이 있는 부분(0이 아닌 부분)만 카메라 영상 위에 덮어씀
        gray_canvas = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray_canvas, 1, 255, cv2.THRESH_BINARY)
        
        # 선이 그려진 부분만 frame을 교체
        frame[mask > 0] = self.canvas[mask > 0]

        # 7. 현재 색상 정보 표시 (화면 좌측 상단)
        current_color_name = self.color_names[self.color_idx]
        cv2.putText(frame, f"Color: {current_color_name} (Space to change)", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.circle(frame, (600, 25), 15, self.color_list[self.color_idx], -1)

        # 8. 화면 출력
        cv2.imshow("GStreamer Paint", frame)
        
        # 9. 키 입력 처리
        key = cv2.waitKey(1)
        if key == ord('q'):
            self.cap.release()
            cv2.destroyAllWindows()
            rclpy.shutdown()
        elif key == ord(' '): # 스페이스바 누르면 색상 변경
            self.color_idx = (self.color_idx + 1) % len(self.color_list)
            self.get_logger().info(f"색상 변경: {self.color_names[self.color_idx]}")
        elif key == ord('c'): # C 누르면 전체 지우기 (추가 기능)
            self.canvas = np.zeros_like(self.canvas)

        # 10. ROS 2 퍼블리시
        img_msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        self.publisher.publish(img_msg)

def main():
    rclpy.init()
    node = GStreamerDrawingNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()

if __name__ == "__main__":
    main()