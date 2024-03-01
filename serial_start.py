from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QPushButton, QLabel, QCheckBox
import serial.tools.list_ports
import sys
import numpy as np
import cv2
import time
import serial
speeds = ['1200','2400', '4800', '9600', '19200', '38400', '57600', '115200']

class MainApp(QWidget):
    
    def __init__(self): #конструктор начального окна
        super().__init__()
        ports = list(serial.tools.list_ports.comports())
        layout = QVBoxLayout()
        self.Label1=QLabel(self)
        self.Label2=QLabel(self)
        self.Label3=QLabel(self)
        self.Label1.setText("Выберите номер камеры")
        self.Label2.setText("Выберите порт")
        self.Label3.setText("Выберите скорость")
        self.comboBox_camera_port = QComboBox(self)
        self.comboBox_device_port = QComboBox(self)
        self.comboBox_device_speed = QComboBox(self)
        self.checkbox_flip=QCheckBox('Зеркально',self)
        self.checkbox_flip.setChecked(True)
        for number in range(256):
            self.comboBox_camera_port.addItem(str(number))
        for speed in speeds:
            self.comboBox_device_speed.addItem(str(speed))
        for port in ports:
            self.comboBox_device_port.addItem(str(port.device))

        self.start_button = QPushButton("Connect")
        self.start_button.clicked.connect(self.start_selected_function)
        layout.addWidget(self.Label1)
        layout.addWidget(self.comboBox_camera_port)
        layout.addWidget(self.checkbox_flip)
        layout.addWidget(self.Label2)
        layout.addWidget(self.comboBox_device_port)
        layout.addWidget(self.Label3)
        layout.addWidget(self.comboBox_device_speed)
        layout.addWidget(self.start_button)

        self.setLayout(layout)
        self.setWindowTitle("Stat panel")
        self.show()

    def start_selected_function(self): #выбор функции
        ser = serial.Serial(port=str(self.comboBox_device_port.currentText()), baudrate=int(self.comboBox_device_speed.currentIndex()))
        model = cv2.dnn.readNetFromDarknet('yolov3.cfg', 'yolov3.weights')
        model.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        model.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

        # Загрузка изображения для пробного распознавания

        # Определение размеров окна для вывода изображения
        window_name = "Video"
        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

        # Захват видео с веб-камеры
        cap = cv2.VideoCapture(int(self.comboBox_camera_port.currentText()))

        while True:
            # Захват каждого кадра
            ret, frame = cap.read()
            if self.checkbox_flip.isChecked():
                frame=cv2.flip(frame, 1)
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
                        if classID ==39:
                            boxes.append([x, y, int(width), int(height)])
                            confidences.append(float(confidence))
                            classIDs.append(classID)
                            data='bottle'
                            ser.write(data.encode())
                            print("bottle")
                            time.sleep(2)                       
                            

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
            key = cv2.waitKey(1)
            if key == 27:
                break
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                break

        # Остановка видеопотока
        cap.release()

        # Закрытие окна отображения
        cv2.destroyAllWindows()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = MainApp()
    sys.exit(app.exec())