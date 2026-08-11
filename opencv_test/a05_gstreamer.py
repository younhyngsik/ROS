import cv2
import numpy as np
from inference_sdk import InferenceHTTPClient
import time

# 1. Roboflow 설정
client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="V6RdML252LDiSbPlwXbj"
)

WORKSPACE_NAME = "-0sdbj"
WORKFLOW_ID = "general-segmentation-api"

def main():
    # 2. V4L2를 사용하여 카메라 열기
    # 보통 /dev/video0은 index 0입니다. 
    # 만약 작동하지 않으면 1이나 2로 변경해 보세요.
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

    # 해상도 설정 (성능을 위해 640x480 권장)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("에러: 카메라를 열 수 없습니다. (/dev/video0 확인 필요)")
        return

    print("V4L2 장치 연결 성공. 추론을 시작합니다...")

    while True:
        start_time = time.time()
        
        ret, frame = cap.read()
        if not ret:
            print("프레임을 읽을 수 없습니다.")
            break

        try:
            # 3. Roboflow Workflow 실행
            # frame(numpy array)을 직접 전달합니다.
            result = client.run_workflow(
                workspace_name=WORKSPACE_NAME,
                workflow_id=WORKFLOW_ID,
                images={"image": frame},
                parameters={
                    "classes": "0, Non-reusable bottle, reusable bottle"
                }
            )

            # 4. 결과 파싱 및 시각화
            # 'general-segmentation-api' 워크플로우의 응답 구조에 맞게 데이터를 추출합니다.
            # Roboflow 워크플로우 응답 구조는 사용자가 설정한 Output 노드에 따라 다를 수 있습니다.
            
            if 'outputs' in result and len(result['outputs']) > 0:
                # 'predictions' 또는 워크플로우에서 설정한 출력 키값 확인이 필요합니다.
                # 아래는 일반적인 검출 결과 파싱 예시입니다.
                output = result['outputs'][0]
                
                # 만약 세그멘테이션 결과가 포함되어 있다면 해당 노드 이름을 확인해야 합니다.
                # 여기서는 'predictions'라는 키가 있다고 가정하고 처리합니다.
                predictions = output.get('predictions', []) 
                
                for pred in predictions:
                    # Roboflow API 응답 좌표는 보통 중심점(x, y)과 너비, 높이입니다.
                    x, y, w, h = pred['x'], pred['y'], pred['width'], pred['height']
                    label = pred['class']
                    conf = pred['confidence']

                    # 바운딩 박스 계산
                    x1 = int(x - w/2)
                    y1 = int(y - h/2)
                    x2 = int(x + w/2)
                    y2 = int(y + h/2)

                    # 찌그러짐 여부 등에 따른 색상 변경 (예시)
                    color = (0, 255, 0) if "reusable" in label.lower() else (0, 0, 255)
                    
                    # 그리기
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, f"{label} ({conf:.2f})", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        except Exception as e:
            print(f"추론 중 에러 발생: {e}")

        # FPS 표시
        end_time = time.time()
        fps = 1 / (end_time - start_time)
        cv2.putText(frame, f"FPS: {fps:.1f}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        # 5. 화면 출력
        cv2.imshow("Roboflow V4L2 Detector", frame)

        # 'q' 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()