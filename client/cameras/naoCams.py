import cv2

NAO_IP = "192.168.0.65"

topcamUrl = f"tcp://{NAO_IP}:3000"
bottomcamUrl = f"tcp://{NAO_IP}:3001"

top = cv2.VideoCapture(topcamUrl)
bottom = cv2.VideoCapture(bottomcamUrl)

while True:
    ret, frameTop = top.read()
    ret, frameBottom = bottom.read()

    if not ret:
        break
    cv2.imshow('Nao Top', frameTop)
    cv2.imshow('Nao Bottom', frameBottom)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
