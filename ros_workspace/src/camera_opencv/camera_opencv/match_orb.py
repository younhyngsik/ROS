# orb keypoints와 descriptor를 사용해서 임의의 물체를 검출
# 1 keypoints -> 사진 찍어서 orb로 얻기
# 2 keypoints -> 카메라 영상을 사용
# a34번, camera_pub 예제 활용

import os
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
from pathlib import Path

class OrbObjectDetector(Node):
    def __init__(self):
        super().__init__('orb_object_detector')
        self.bridge = CvBridge()
        
        # 1. 대상 물체(Reference) 이미지 로드 및 특징점 추출
        # 경로를 본인의 파일 위치에 맞게 수정하세요.
        file_path = Path(__file__).parent
        ref_img_path = str(file_path / "/home/youn/ROS/ros_workspace/src/camera_opencv/camera_opencv/data/mouse.jpg") 
        self.ref_img = cv2.imread(ref_img_path)
        
        if self.ref_img is None:
            self.get_logger().error(f"대상 이미지를 찾을 수 없습니다: {ref_img_path}")
            exit()

        self.gray_ref = cv2.cvtColor(self.ref_img, cv2.COLOR_BGR2GRAY)
        
        # ORB 알고리즘 초기화 (1000개의 특징점)
        self.orb = cv2.ORB_create(nfeatures=1000)
        self.kp_ref, self.des_ref = self.orb.detectAndCompute(self.gray_ref, None)
        
        # 특징점 매칭을 위한 BFMatcher (해밍 거리 사용)
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        # 2. 카메라 설정 (GStreamer 최적화 파이프라인)
        self.width = 640
        self.height = 480
        pipeline = (
            "v4l2src device=/dev/video0 ! "
            f"image/jpeg,width={self.width},height={self.height},framerate=30/1 ! "
            "jpegdec ! videoconvert ! video/x-raw,format=BGR ! appsink drop=true sync=false"
        )
        self.cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

        # 3. 퍼블리셔 설정
        self.pub = self.create_publisher(Image, "camera/image_raw", 10)
        
        # 4. 루프 타이머 (30 FPS)
        self.create_timer(1/30, self.detect_callback)
        self.get_logger().info("ORB 물체 검출 노드 시작됨")

    def detect_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # 현 프레임 그레이스케일 변환 및 특징점 추출
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        kp_frame, des_frame = self.orb.detectAndCompute(gray_frame, None)

        if des_frame is not None:
            # 두 이미지 간 특징점 매칭
            matches = self.bf.match(self.des_ref, des_frame)
            # 거리에 따라 정렬
            matches = sorted(matches, key=lambda x: x.distance)

            # 좋은 매칭점 선별 (상위 50개 혹은 일정 거리 이하)
            good_matches = matches[:50]

            # 매칭점이 충분히 많을 때만 호모그래피 계산 (최소 10개)
            if len(good_matches) > 15:
                src_pts = np.float32([self.kp_ref[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                dst_pts = np.float32([kp_frame[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

                # 호모그래피(H) 행렬 찾기 (RANSAC 활용)
                H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

                if H is not None:
                    # 대상 이미지의 모서리 좌표 정의
                    h, w = self.gray_ref.shape
                    pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
                    
                    # 호모그래피를 이용해 프레임상에서의 물체 모서리 계산 (크기 변화 대응 핵심)
                    try:
                        dst = cv2.perspectiveTransform(pts, H)
                        # 검출된 물체 테두리 그리기 (파란색 선)
                        frame = cv2.polylines(frame, [np.int32(dst)], True, (255, 0, 0), 3)
                        
                        cv2.putText(frame, "Object Detected", (int(dst[0][0][0]), int(dst[0][0][1])-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    except:
                        pass

        # 결과 화면 출력
        cv2.imshow("Real-time ORB Detection", frame)
        cv2.waitKey(1)

        # ROS 2 메시지로 발행
        img_msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        img_msg.header.stamp = self.get_clock().now().to_msg()
        img_msg.header.frame_id = "camera_link"
        self.pub.publish(img_msg)

def main(args=None):
    rclpy.init(args=args)
    node = OrbObjectDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cap.release()
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()