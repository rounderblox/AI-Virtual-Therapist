from fer import FER
import cv2


def detect_emotion(image_path):
    detector = FER(mtcnn=True)
    img = cv2.imread(image_path)

    if img is None:
        return "Image not found or unreadable"

    emotion, score = detector.top_emotion(img)
    return {"emotion": emotion, "score": score}


def detect_emotions_from_video(video_path):
    detector = FER(mtcnn=True)
    cap = cv2.VideoCapture(video_path)
    emotions_per_frame = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect the dominant emotion in this frame
        emotion, score = detector.top_emotion(frame)
        emotions_per_frame.append((emotion, score))
        print(f"Frame Emotion: {emotion} ({score})")

    cap.release()
    return emotions_per_frame
