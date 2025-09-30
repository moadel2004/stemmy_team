from ultralytics import YOLO
import cv2
import numpy as np
import os
from typing import Optional, Union, Tuple, List
import time
from collections import deque, Counter
try:
    import torch
except Exception:
    torch = None

class FaceEmotionRecognizer:
    """
    A YOLO-based face and emotion recognizer.

    This class loads a pretrained YOLO model once and provides methods to predict
    emotions from images, files, or a live webcam stream. It is optimized for
    real-time performance using streaming.
    """

    def __init__(self, weights_path: Optional[str] = None, image_size: int = 640, confidence_threshold: float = 0.30, iou_threshold: float = 0.45, max_detections: int = 10, smoothing_window: int = 5) -> None:
        """
        Initializes the recognizer and loads the YOLO model weights.

        Args:
            weights_path (Optional[str]): Path to the YOLO model weights file (e.g., 'best.pt').
                                          If None, it defaults to 'best.pt' in the same directory.
            image_size (int): Inference image size; higher can improve accuracy at cost of speed.
            confidence_threshold (float): Minimum confidence to accept detections.
            iou_threshold (float): IoU threshold for NMS.
            max_detections (int): Maximum detections per image.
            smoothing_window (int): Frames over which to smooth the predicted label.
        """
        if weights_path is None:
            # Default to weights located next to this file
            weights_path = os.path.join(os.path.dirname(__file__), "best.pt")

        if not os.path.exists(weights_path):
            raise FileNotFoundError(
                f"Model weights not found at the specified path: {weights_path}. "
                "Please ensure the 'best.pt' file is in the correct location or provide the correct path."
            )
        self.model = YOLO(weights_path)

        # Inference parameters
        self.image_size = max(320, int(image_size))
        self.confidence_threshold = float(confidence_threshold)
        self.iou_threshold = float(iou_threshold)
        self.max_detections = int(max_detections)
        self.smoothing_window = max(1, int(smoothing_window))
        self._label_history = deque(maxlen=self.smoothing_window)

        # Optimize OpenCV
        try:
            cv2.setUseOptimized(True)
            cv2.setNumThreads(0)
        except Exception:
            pass

        # Select device, enable half precision when available
        self.device = None
        self.use_half = False
        if torch is not None and hasattr(torch, "cuda") and torch.cuda.is_available():
            self.device = 0  # CUDA:0
            self.use_half = True
            try:
                torch.backends.cudnn.benchmark = True
            except Exception:
                pass
        elif torch is not None and hasattr(torch, "mps") and torch.backends.mps.is_available():
            # Apple MPS (no half precision)
            self.device = "mps"
            self.use_half = False
        else:
            self.device = "cpu"
            self.use_half = False

        # Warmup to stabilize performance
        try:
            _ = self.model.predict(
                np.zeros((self.image_size, self.image_size, 3), dtype=np.uint8),
                imgsz=self.image_size,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                max_det=self.max_detections,
                device=self.device,
                half=self.use_half,
                verbose=False,
            )
        except Exception:
            pass

    def _to_bgr_image(self, image: Union[str, bytes, np.ndarray]) -> np.ndarray:
        """
        Converts various image formats (path, bytes, ndarray) into an OpenCV BGR image.
        """
        if isinstance(image, np.ndarray):
            return image
        if isinstance(image, (bytes, bytearray)):
            np_buffer = np.frombuffer(image, dtype=np.uint8)
            frame = cv2.imdecode(np_buffer, cv2.IMREAD_COLOR)
            if frame is None:
                raise ValueError("Failed to decode image from bytes.")
            return frame
        if isinstance(image, str):
            frame = cv2.imread(image)
            if frame is None:
                raise FileNotFoundError(f"Could not read image at path: {image}")
            return frame
        raise TypeError("Unsupported image type. Use a numpy array, bytes, or a file path string.")

    def predict_with_confidence(self, image: Union[str, bytes, np.ndarray]) -> Tuple[str, float]:
        """
        Predicts the emotion and confidence for the highest-confidence detection in an image.

        Args:
            image: The input image as a path, bytes, or numpy array.

        Returns:
            A tuple containing the emotion label (str) and confidence score (float).
            Defaults to ('neutral', 0.0) if no face is detected.
        """
        frame = self._to_bgr_image(image)
        # Use verbose=False to reduce console spam
        results = self.model.predict(
            frame,
            imgsz=self.image_size,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            max_det=self.max_detections,
            device=self.device,
            half=self.use_half,
            verbose=False,
        )
        
        # Results is a list, we typically care about the first element
        result = results[0]
        
        if result.boxes is not None and len(result.boxes) > 0:
            # Find the detection with the highest confidence
            best_idx = result.boxes.conf.argmax()
            confidence = float(result.boxes.conf[best_idx])
            class_id = int(result.boxes.cls[best_idx])
            emotion = self._class_name_from_id(class_id)
            return emotion, confidence
            
        return "neutral", 0.0
    
    def predict(self, image: Union[str, bytes, np.ndarray]) -> str:
        """
        Predicts the emotion label for the highest-confidence detection in an image.

        Args:
            image: The input image as a path, bytes, or numpy array.

        Returns:
            The emotion label string. Defaults to 'neutral' if no face is detected.
        """
        emotion, _ = self.predict_with_confidence(image)
        return emotion

    def _class_name_from_id(self, class_id: int) -> str:
        names = self.model.names
        if isinstance(names, dict):
            return names.get(class_id, "neutral")
        if isinstance(names, list) and 0 <= class_id < len(names):
            return names[class_id]
        return "neutral"

    def run_webcam(self, camera_index: int = 0, confidence_threshold: float = 0.3, window_name: str = "Emotion Recognition", target_resolution: Optional[Tuple[int, int]] = None, print_to_console: bool = True, print_interval_seconds: float = 1.0) -> None:
        """
        Opens a webcam feed, performs real-time emotion recognition, and displays the results.

        Args:
            camera_index (int): The index of the camera to use (e.g., 0 for the default camera).
            confidence_threshold (float): Detections below this confidence will be ignored.
            window_name (str): The title of the OpenCV display window.
            target_resolution (Optional[Tuple[int,int]]): Desired (width, height) for capture.
            print_to_console (bool): If True, print label and confidence to terminal.
            print_interval_seconds (float): Minimum seconds between prints when label unchanged.
        """
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print(f"Error: Could not open camera with index {camera_index}.")
            print("Please check if the camera is connected and not in use by another application.")
            return

        try:
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            print("Webcam started. Press 'q' or ESC to quit.")

            # Optionally set capture resolution for performance/accuracy tradeoff
            if target_resolution is not None and len(target_resolution) == 2:
                try:
                    w, h = int(target_resolution[0]), int(target_resolution[1])
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
                except Exception:
                    pass

            # KEY CHANGE: Use stream=True for efficient video processing
            # This returns a generator, which is much better for real-time feeds.
            results_generator = self.model.predict(
                source=camera_index,
                stream=True,
                show=False,
                imgsz=self.image_size,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                max_det=self.max_detections,
                device=self.device,
                half=self.use_half,
                verbose=False,
            )

            last_print_label = None
            last_print_time = 0.0

            for result in results_generator:
                # Get the original frame from the result object
                frame = result.orig_img
                if frame is None:
                    break

                if result.boxes is not None and len(result.boxes) > 0:
                    # Find the best detection based on confidence
                    confidences = result.boxes.conf
                    best_idx = confidences.argmax()
                    
                    if confidences[best_idx] >= confidence_threshold:
                        class_id = int(result.boxes.cls[best_idx])
                        label = self.model.names.get(class_id, "Unknown")
                        conf = float(confidences[best_idx])
                        
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = map(int, result.boxes.xyxy[best_idx].tolist())
                        
                        # --- Draw Bounding Box and Label ---
                        # Box rectangle
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        
                        # Label text
                        # Temporal smoothing of label to reduce flicker
                        self._label_history.append(label)
                        smoothed_label = Counter(self._label_history).most_common(1)[0][0]
                        label_text = f"{smoothed_label}: {conf:.2f}"

                        # Optionally print to console when label changes or interval elapses
                        if print_to_console:
                            now = time.time()
                            if smoothed_label != last_print_label or (now - last_print_time) >= max(0.1, float(print_interval_seconds)):
                                print(f"[Webcam] Emotion={smoothed_label}, Confidence={conf:.3f}")
                                last_print_label = smoothed_label
                                last_print_time = now
                        
                        # Calculate text size to draw a background rectangle
                        (text_width, text_height), baseline = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                        
                        # Label background
                        cv2.rectangle(frame, (x1, y1 - text_height - 10), (x1 + text_width, y1), (0, 255, 0), -1)
                        
                        # Label text on top of background
                        cv2.putText(frame, label_text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

                # Display the resulting frame
                cv2.imshow(window_name, frame)

                # Check for exit key
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # 'q' or ESC
                    break
        finally:
            print("Shutting down webcam.")
            cap.release()
            cv2.destroyAllWindows()


# --- Convenience Functions ---
# Lazy-loaded singleton instance to avoid reloading the model repeatedly.
_DEFAULT_RECOGNIZER: Optional[FaceEmotionRecognizer] = None

def _get_recognizer(weights_path: Optional[str] = None) -> FaceEmotionRecognizer:
    """Helper to get or create the default recognizer instance."""
    global _DEFAULT_RECOGNIZER
    if _DEFAULT_RECOGNIZER is None or weights_path is not None:
        # Create a new instance if one doesn't exist or if a custom path is provided
        _DEFAULT_RECOGNIZER = FaceEmotionRecognizer(weights_path)
    return _DEFAULT_RECOGNIZER

def predict_emotion(image: Union[str, bytes, np.ndarray], weights_path: Optional[str] = None) -> str:
    """Predicts emotion from a single image using a shared recognizer instance."""
    recognizer = _get_recognizer(weights_path)
    return recognizer.predict(image)

def run_webcam(camera_index: int = 0, confidence_threshold: float = 0.3, weights_path: Optional[str] = None, target_resolution: Optional[Tuple[int, int]] = None) -> None:
    """Runs the webcam emotion recognition using a shared recognizer instance."""
    recognizer = _get_recognizer(weights_path)
    recognizer.run_webcam(camera_index=camera_index, confidence_threshold=confidence_threshold, target_resolution=target_resolution)


# This allows the script to be run directly to test the webcam functionality.
if __name__ == "__main__":
    print("Attempting to start webcam for emotion recognition...")
    try:
        # Ensure 'best.pt' is in the same directory as this script,
        # or specify the full path: run_webcam(weights_path="path/to/your/best.pt")
        run_webcam(camera_index=0, confidence_threshold=0.3)
    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        print("Please make sure the model weights file ('best.pt') is in the same folder as this Python script.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
