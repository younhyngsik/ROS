from roboflow import Roboflow
from ultralytics import YOLO

# [Step 1] 로보플로우에서 복사한 본인의 코드를 이 아랫줄에 붙여넣으세요.
# 예시:


from roboflow import Roboflow
rf = Roboflow(api_key="V6RdML252LDiSbPlwXbj")
project = rf.workspace("fams-testing").project("can-d5wp7")
version = project.version(1)
dataset = version.download("yolo26")

                
rf = Roboflow(api_key="YOUR_API_KEY")
project = rf.workspace("swmaker-jun").project("object-detection-xxxx")
dataset = project.version(2).download("yolov8")

# [Step 2] 가장 가볍고 빠른 YOLOv8 나노(nano) 모델 불러오기
model = YOLO('yolov8n.pt') 

# [Step 3] 내가 다운로드한 데이터셋으로 AI 모델 학습 시작하기
# data=dataset.location + "/data.yaml" 은 다운로드된 데이터 설정 파일을 자동으로 지정합니다.
# epochs=20은 전체 사진을 총 20번 반복해서 공부하라는 뜻입니다.
model.train(data=dataset.location + "/data.yaml", epochs=20, imgsz=640)

print("🎉 AI 모델 학습이 완료되었습니다!")