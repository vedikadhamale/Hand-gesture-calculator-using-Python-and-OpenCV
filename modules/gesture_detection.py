import cv2
import os

# Hide TensorFlow CUDA warnings when GPU runtime is not installed.
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
import mediapipe as mp


class GestureDetector:
    NUMBER_GESTURES = {
        (0, 0, 0, 0, 0): 0,
        (0, 1, 0, 0, 0): 1,
        (0, 1, 1, 0, 0): 2,
        (0, 1, 1, 1, 0): 3,
        (0, 1, 1, 1, 1): 4,
        (1, 1, 1, 1, 1): 5,
    }

    OPERATOR_GESTURES = {
        (1, 1, 0, 0, 0): "+",
        (1, 0, 1, 0, 0): "-",
        (1, 0, 0, 1, 0): "*",
        (1, 0, 0, 0, 1): "/",
    }

    SPECIAL_GESTURES = {
        (1, 0, 0, 0, 0): ("clear", "CLEAR"),
        (0, 1, 0, 0, 1): ("equals", "="),
    }

    def __init__(self, max_num_hands=2, detection_conf=0.7, tracking_conf=0.7):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=detection_conf,
            min_tracking_confidence=tracking_conf,
        )
        self.mp_draw = mp.solutions.drawing_utils

    def _finger_states(self, hand_landmarks):
        lm = hand_landmarks.landmark

        # Infer hand side from landmarks (more reliable than handedness on mirrored frames)
        is_right_hand = lm[5].x < lm[17].x

        # Thumb: for right hand, extended thumb points to left (smaller x)
        if is_right_hand:
            thumb_up = lm[4].x < lm[3].x
        else:
            thumb_up = lm[4].x > lm[3].x

        index_up = lm[8].y < lm[6].y
        middle_up = lm[12].y < lm[10].y
        ring_up = lm[16].y < lm[14].y
        pinky_up = lm[20].y < lm[18].y

        return [int(thumb_up), int(index_up), int(middle_up), int(ring_up), int(pinky_up)]

    def _classify_gesture(self, fingers):
        key = tuple(fingers)

        if key in self.SPECIAL_GESTURES:
            gesture_type, label = self.SPECIAL_GESTURES[key]
            return gesture_type, None, label

        if key in self.OPERATOR_GESTURES:
            op_char = self.OPERATOR_GESTURES[key]
            return "operator", op_char, op_char

        if key in self.NUMBER_GESTURES:
            number = self.NUMBER_GESTURES[key]
            return "number", number, str(number)

        return None, None, None

    def detect(self, frame, draw=True):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)

        gestures = []

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                    )

                fingers = self._finger_states(hand_landmarks)
                gesture_type, gesture_value, gesture_label = self._classify_gesture(fingers)
                if gesture_type:
                    gestures.append((gesture_type, gesture_value, gesture_label))

        if not gestures:
            return frame, None, None, None

        for gesture_type, gesture_value, gesture_label in gestures:
            if gesture_type in ("clear", "equals"):
                return frame, gesture_type, gesture_value, gesture_label

        for gesture_type, gesture_value, gesture_label in gestures:
            if gesture_type == "operator":
                return frame, gesture_type, gesture_value, gesture_label

        numbers = [
            gesture_value
            for gesture_type, gesture_value, _ in gestures
            if gesture_type == "number" and isinstance(gesture_value, int)
        ]
        if numbers:
            total = sum(numbers)
            if len(numbers) > 1:
                label = "+".join(str(n) for n in numbers) + f"={total}"
            else:
                label = str(numbers[0])
            return frame, "number", total, label

        return frame, None, None, None

