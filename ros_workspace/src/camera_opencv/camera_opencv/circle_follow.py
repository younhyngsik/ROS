import os
import cv2
import numpy as np
import random
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

class GStreamerCameraNode(Node):
    def __init__(self):
        super().__init__('gstreamer_camera_node')
        self.publisher = self.create_publisher(Image, 'camera_image', 10)
        self.bridge = CvBridge()

        # 1. GStreamer 파이프라인 설정 (가장 빠르고 끊김 없는 방식)
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
            self.get_logger().error("GStreamer를 통한 카메라 오픈 실패!")
            exit()

        # 2. 랜덤 이동 로직 변수
        self.max_points = 10
        self.points = []          # 방문한 좌표 저장
        self.target_points = self.generate_random_points(self.max_points)
        self.current_idx = 0
        self.frame_count = 0      # 이동 속도 조절용

        # 3. 타이머 설정 (30 FPS 주기에 맞춰 0.03초 설정)
        self.timer = self.create_timer(0.03, self.timer_callback)
        self.get_logger().info("GStreamer 카메라 노드가 시작되었습니다.")

    def generate_random_points(self, n):
        """640x480 해상도 내 랜덤 좌표 n개 생성"""
        return [(random.randint(50, 590), random.randint(50, 430)) for _ in range(n)]

    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # 10개 지점 이동 및 라인 그리기 로직
        if self.current_idx < self.max_points:
            # 매 프레임 이동하면 너무 빠르므로 15프레임(0.5초)마다 다음 점 추가
            if self.frame_count % 15 == 0:
                self.points.append(self.target_points[self.current_idx])
                self.current_idx += 1
            self.frame_count += 1

        # 그려진 선과 원 화면에 표시
        for i in range(len(self.points)):
            # 점(원) 그리기
            cv2.circle(frame, self.points[i], 6, (0, 0, 255), -1) # 빨간색
            # 이전 점과 현재 점 연결 (라인)
            if i > 0:
                cv2.line(frame, self.points[i-1], self.points[i], (255, 0, 0), 2, cv2.LINE_AA)

        # 10곳 모두 방문 시 초기화
        if len(self.points) >= self.max_points and self.frame_count % 30 == 0:
            self.get_logger().info("10곳 순회 완료! 초기화합니다.")
            self.points = []
            self.target_points = self.generate_random_points(self.max_points)
            self.current_idx = 0
            self.frame_count = 0

        # 이미지 표시
        cv2.imshow("GStreamer Real-time Move", frame)
        
        # 'q' 키 종료 처리
        if cv2.waitKey(1) == ord('q'):
            self.cap.release()
            cv2.destroyAllWindows()
            rclpy.shutdown()

        # DDS로 이미지 Publish
        img_msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        self.publisher.publish(img_msg)

def main():
    rclpy.init()
    node = GStreamerCameraNode()
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