import cv2

cap = cv2.VideoCapture("rtsp://ailabo:ailabo123$@10.2.172.154/stream1")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow('Camera Stream', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
