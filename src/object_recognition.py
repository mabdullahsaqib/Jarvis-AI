import cv2
import numpy as np
import tensorflow as tf

# Load the pre-trained model and labels
model = tf.saved_model.load("ssd_mobilenet_v2_fpnlite_320x320/saved_model")
category_index = {1: "person", 2: "bicycle", 3: "car", 4: "motorcycle", 5: "airplane", 6: "bus"}


# Function to perform object detection
def detect_objects():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        input_tensor = tf.convert_to_tensor([frame])
        detections = model(input_tensor)

        for detection in detections['detection_boxes']:
            ymin, xmin, ymax, xmax = detection.numpy()[0]
            cv2.rectangle(frame, (int(xmin * frame.shape[1]), int(ymin * frame.shape[0])),
                          (int(xmax * frame.shape[1]), int(ymax * frame.shape[0])), (0, 255, 0), 2)
            label = category_index[int(detections['detection_classes'][0])]
            cv2.putText(frame, label, (int(xmin * frame.shape[1]), int(ymin * frame.shape[0] - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        cv2.imshow('Object Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
