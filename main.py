import cv2
import numpy as np

# Загрузка модели YOLO
model = cv2.dnn.readNetFromDarknet('yolov3.cfg', 'yolov3.weights')
model.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
model.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

# Загрузка изображения для пробного распознавания

# Определение размеров окна для вывода изображения
window_name = "Video"
cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

# Захват видео с веб-камеры
cap = cv2.VideoCapture(0)

while True:
    # Захват каждого кадра
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    # Конвертация изображения в формат BGR
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Выделение области интереса
    (H, W) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)

    # Применение модели YOLO
    model.setInput(blob)
    layerOutputs = model.forward(["yolo_82", "yolo_94", "yolo_106"])

    # Выделение бутылок на изображении
    boxes = []
    confidences = []
    classIDs = []

    for output in layerOutputs:
        for detection in output:
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]

            if confidence > 0.5:
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")

                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                if classID==41:
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    classIDs.append(classID)
                    print("bottle")
                    print(boxes)
                
                    

    # Выделение бутылок на изображении
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.3)
    # cv2.putText(frame, 'bottle', (confidences[0], confidences[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)

    if len(idxs) > 0:
        for i in idxs.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Отображение изображения
    cv2.imshow(window_name, frame)

    # Если нажата клавиша 'q', то выход из цикла
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Остановка видеопотока
cap.release()

# Закрытие окна отображения
cv2.destroyAllWindows()