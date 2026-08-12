import cv2

print(cv2.__version__)

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

marker_id = 4
marker_size = 1000

marker = cv2.aruco.generateImageMarker(
    dictionary,
    marker_id,
    marker_size,
)

marker_with_margin = cv2.copyMakeBorder(
    marker,
    100,
    100,
    100,
    100,
    cv2.BORDER_CONSTANT,
    value=255,
)

output_path = "aruco_4.png"

success = cv2.imwrite(output_path, marker_with_margin)

if not success:
    raise RuntimeError(f"이미지 저장 실패: {output_path}")

print(f"{output_path} 생성 완료")