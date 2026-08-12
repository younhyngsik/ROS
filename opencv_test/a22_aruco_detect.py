import cv2

def main():
    # 1. 카메라 설정 (MJPEG 포맷 적용으로 가로줄 노이즈 방지)
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("❌ 카메라는 열 수 없습니다.")
        return

    # 2. ArUco 딕셔너리 및 디텍터 설정 (OpenCV 4.7+ 최신 방식)
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    
    # 💡 최신 ArucoDetector 객체 생성
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    print("✅ 최신 OpenCV 연동 ArUco 마커 감지 작동 시작! (종료: 'q')")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 3. ArUco 마커 실시간 검출
        corners, ids, rejected = detector.detectMarkers(frame)

        # 마커가 감지된 경우 화면에 바운딩 박스 및 ID 그리기
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            
            # 감지된 마커 ID 터미널에 출력
            for i, marker_id in enumerate(ids.flatten()):
                c = corners[i][0]
                cx = int(c[:, 0].mean())
                cy = int(c[:, 1].mean())
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                # print(f"📍 감지된 ArUco 마커 ID: {marker_id} (중심 픽셀: {cx}, {cy})")

        cv2.imshow("ArUco Detection (OpenCV 4.14+)", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()