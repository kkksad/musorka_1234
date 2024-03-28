from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QPushButton, QLabel, QCheckBox
import serial.tools.list_ports
import sys
import sqlite3
from pyzbar.pyzbar import decode
import numpy as np
import cv2
import time
import serial
import asyncio
from auth_system import main
speeds = ['1200','2400', '4800', '9600', '19200', '38400', '57600', '115200']
db_path='auth_tabel.db'


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
        self.start_button.clicked.connect(self.save_config)
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

    def save_config(self):
        self.port=str(self.comboBox_device_port.currentText())
        self.speed=int(self.comboBox_device_speed.currentIndex())
        self.number_cam=int(self.comboBox_camera_port.currentText())
        self.flip=bool(self.checkbox_flip.isChecked())
        self.change_label()

    def change_label(self):
        # Удаляем все виджеты из макета
        
                       
        layout = self.layout()
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # Создаем новую надпись
        self.button = QPushButton('Начать распознавание')
        layout.addWidget(self.button)
        self.button.clicked.connect(self.start_selected_function)
    def start_selected_function(self): #выбор функции
        self.stop_scan=False
        def stop():
            self.stop_scan=True
        self.bonus_size=0
        layout = self.layout()
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # Создаем новую надпись
        self.button1 = QPushButton('Закончить распознавание')
        layout.addWidget(self.button1)
        self.button1.clicked.connect(stop)
        ser = serial.Serial(port=self.port, baudrate=self.speed)
        model = cv2.dnn.readNetFromDarknet('yolov3.cfg', 'yolov3.weights')
        model.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        model.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

        # Загрузка изображения для пробного распознавания

        # Определение размеров окна для вывода изображения
        window_name = "Video"
        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

        # Захват видео с веб-камеры
        cap = cv2.VideoCapture(self.number_cam)

        while True:
            # Захват каждого кадра
            ret, frame = cap.read()
            if self.flip:
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
                            idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.3)
                            # cv2.putText(frame, 'bottle', (confidences[0], confidences[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
                            if len(idxs) > 0:
                                for i in idxs.flatten():
                                    (x, y) = (boxes[i][0], boxes[i][1])
                                    (w, h) = (boxes[i][2], boxes[i][3])
                                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            data='1'
                            ser.write(data.encode())
                            print("bottle")
                            self.bonus_size+=1
                            print(self.bonus_size)
                            
                            
        
            if self.stop_scan:
                break
            

                
        
                
                
                                                  
                            

            # Выделение бутылок на изображении
            

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
        if self.bonus_size > 0:
            self.scan_qr_code()
        else:
            self.change_label()
    def scan_qr_code(self):
        # Define the text properties
        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (10,200)
        fontScale = 2
        fontColor = (255,255,255)
        thickness = 4
        lineType = 3

        # Open the camera
        cap = cv2.VideoCapture(self.number_cam)

        # Connect to the SQLite database
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # Start a while loop
        while True:
            # Read a frame from the camera
            _, frame = cap.read()

            # Convert the frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Decode the QR code
            decoded = decode(gray)

            # Check if a QR code is found
            if decoded:
                # Decode the QR code data
                qr_data = decoded[0][0].decode('utf-8')

                # Check if the QR code data exists in the database
                cursor.execute('select id from user_table')
                ids = list(cursor.fetchall()[0])
                if qr_data in ids:
                    # Update the bonus for the user
                    cursor.execute('UPDATE user_table SET bonus = bonus + ? WHERE id = ?',(self.bonus_size,str(qr_data),))
                    connection.commit()

                    # Display a success message on the frame
                    cv2.putText(frame,'Sucsess',bottomLeftCornerOfText,font,fontScale,fontColor,thickness,lineType)

                    # Wait for a second
                    time.sleep(1)
                    break

                elif qr_data not in ids:
                    # Display a wrong QR message on the frame
                    cv2.putText(frame,'Wrong QR',bottomLeftCornerOfText,font,fontScale,fontColor,thickness,lineType)

                # Print the QR code data
                print('QR code data:', qr_data)

            # Show the frame
            cv2.imshow('QR Code Scanner', frame)

            # Break the loop if 'q' key is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the camera and close the window
        cap.release()
        cv2.destroyAllWindows()
        self.change_label()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = MainApp()
    # asyncio.run(main())
    sys.exit(app.exec())