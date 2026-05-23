"""YOLOv8n detection + state machine → serial commands to Arduino Mega."""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

import cv2
import serial
from ultralytics import YOLO

PICK_TARGETS = {"bottle", "cup", "sports ball", "apple", "orange"}
OBSTACLES = {"person", "chair", "dining table", "backpack", "suitcase"}


class BrainState(str, Enum):
    SEARCHING = "SEARCHING"
    APPROACH = "APPROACH"
    PICK = "PICK"
    AVOID = "AVOID"


@dataclass
class DetectionInfo:
    target_label: Optional[str] = None
    target_center_x: Optional[float] = None
    target_area_ratio: float = 0.0
    obstacle_label: Optional[str] = None
    obstacle_center_x: Optional[float] = None
    obstacle_area_ratio: float = 0.0


class HexapodVision:
    def __init__(
        self,
        stream_source: str | int,
        serial_port: str,
        baud: int = 115200,
        model_path: str = "yolov8n.pt",
        conf_threshold: float = 0.35,
        dry_run: bool = False,
    ) -> None:
        self.stream_source = stream_source
        self.conf_threshold = conf_threshold
        self.dry_run = dry_run
        self.model = YOLO(model_path)
        self.ser = None if dry_run else serial.Serial(serial_port, baud, timeout=0.1)
        self.cap = cv2.VideoCapture(stream_source)
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open stream: {stream_source}")

        self.state = BrainState.SEARCHING
        self.avoid_until = 0.0
        self.pick_cooldown_until = 0.0

    @staticmethod
    def _clamp(value: float, lo: float = -1.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, value))

    def _send_serial(self, fwd: float, strafe: float, rot: float) -> None:
        line = f"{fwd:.2f},{strafe:.2f},{rot:.2f}\n"
        if self.ser is not None:
            self.ser.write(line.encode("utf-8"))

    def _pick_best_detections(self, frame_w: int, frame_h: int, result) -> DetectionInfo:
        info = DetectionInfo()
        best_target = best_obstacle = -1.0
        frame_area = float(frame_w * frame_h)
        boxes = result.boxes
        if boxes is None:
            return info

        for box in boxes:
            conf = float(box.conf[0].item())
            if conf < self.conf_threshold:
                continue
            cls_id = int(box.cls[0].item())
            label = result.names.get(cls_id, str(cls_id)).lower()
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            area_ratio = max(1.0, x2 - x1) * max(1.0, y2 - y1) / frame_area
            cx = (x1 + x2) / 2.0

            if label in PICK_TARGETS and conf > best_target:
                best_target = conf
                info.target_label = label
                info.target_center_x = cx
                info.target_area_ratio = area_ratio
            if label in OBSTACLES and conf > best_obstacle:
                best_obstacle = conf
                info.obstacle_label = label
                info.obstacle_center_x = cx
                info.obstacle_area_ratio = area_ratio
        return info

    def _state_machine(self, det: DetectionInfo, frame_w: int) -> Tuple[float, float, float]:
        now = time.time()
        fwd = strafe = rot = 0.0

        if self.state != BrainState.AVOID and det.obstacle_area_ratio > 0.16:
            self.state = BrainState.AVOID
            self.avoid_until = now + 1.5

        if self.state == BrainState.AVOID:
            if now < self.avoid_until:
                ox = det.obstacle_center_x if det.obstacle_center_x is not None else frame_w / 2.0
                strafe = -0.45 if ox > frame_w / 2.0 else 0.45
                return 0.0, strafe, 0.0
            self.state = BrainState.SEARCHING

        if self.state == BrainState.PICK and now < self.pick_cooldown_until:
            return 0.0, 0.0, 0.0

        if det.target_center_x is None:
            self.state = BrainState.SEARCHING
        elif det.target_area_ratio > 0.22:
            self.state = BrainState.PICK
        else:
            self.state = BrainState.APPROACH

        if self.state == BrainState.SEARCHING:
            return 0.0, 0.0, 0.30

        if self.state == BrainState.APPROACH and det.target_center_x is not None:
            err_x = (det.target_center_x - frame_w / 2.0) / (frame_w / 2.0)
            rot = self._clamp(err_x * 0.65)
            fwd = self._clamp(0.40 - abs(err_x) * 0.18, 0.18, 0.45)
            return fwd, 0.0, rot

        if self.state == BrainState.PICK:
            self.pick_cooldown_until = now + 3.0
            self.state = BrainState.SEARCHING
            return 0.0, 0.0, 0.0

        return fwd, strafe, rot

    def run(self) -> None:
        try:
            while True:
                ok, frame = self.cap.read()
                if not ok or frame is None:
                    self._send_serial(0.0, 0.0, 0.0)
                    time.sleep(0.05)
                    continue

                h, w = frame.shape[:2]
                result = self.model.predict(
                    source=frame, imgsz=320, conf=self.conf_threshold, verbose=False
                )[0]
                det = self._pick_best_detections(w, h, result)
                fwd, strafe, rot = self._state_machine(det, w)
                self._send_serial(fwd, strafe, rot)

                annotated = result.plot(img=frame)
                cv2.putText(
                    annotated,
                    f"State: {self.state.value}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2,
                )
                cv2.imshow("Hexapod Vision", annotated)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        finally:
            self._send_serial(0.0, 0.0, 0.0)
            if self.ser is not None and self.ser.is_open:
                self.ser.close()
            self.cap.release()
            cv2.destroyAllWindows()


def main() -> None:
    parser = argparse.ArgumentParser(description="YOLOv8 → Mega serial bridge")
    parser.add_argument("--port", required=True, help="Serial port, e.g. COM3")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--stream", help="ESP32-CAM MJPEG URL")
    parser.add_argument("--webcam", type=int, help="Webcam index (0)")
    parser.add_argument("--model", default="yolov8n.pt")
    parser.add_argument("--conf", type=float, default=0.35)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.stream is None and args.webcam is None:
        parser.error("Provide --stream <url> or --webcam <index>")
    source: str | int = args.webcam if args.webcam is not None else args.stream

    HexapodVision(
        stream_source=source,
        serial_port=args.port,
        baud=args.baud,
        model_path=args.model,
        conf_threshold=args.conf,
        dry_run=args.dry_run,
    ).run()


if __name__ == "__main__":
    main()
