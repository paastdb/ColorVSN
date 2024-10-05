import os

import cv2
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QMessageBox

from app_classes.worker_signals import WorkerSignals
from moviepy.video.io.VideoFileClip import VideoFileClip


# from moviepy.video.io.VideoFileClip import VideoFileClip


class ColorVSNWorker(QThread):
    worker_signals = WorkerSignals()

    def __init__(self, **kwargs):
        super(ColorVSNWorker, self).__init__()
        self.is_running = False
        self.kwargs = kwargs

        self.file_path = self.kwargs["filename"]
        self.output_dir = self.kwargs["output_dir"]

        self.infrared = self.kwargs["infrared"]
        self.brightness = self.kwargs["brightness"]
        self.contrast = self.kwargs["contrast"]
        self.colormap = self.kwargs["colormap"]

        self.output_file_path = None

    def run(self):
        self.process_video()
        # self.worker_signals.finished.emit(True, "Video Processed Successfully!")

    def apply_night_vision(self, frame):
        # Apply brightness and contrast effect
        processed_frame = self.brightness_contrast_effect(frame)

        # Apply infrared effect
        if bool(self.infrared):
            processed_frame = self.infared_effect(processed_frame)
            # Apply colormap effect
        if self.colormap is not None:
            processed_frame = self.apply_colormap(processed_frame)
        return processed_frame

    def brightness_contrast_effect(self, frame):
        # Call addWeighted function. Use beta = 0 to effectively only operate on one image
        out = cv2.addWeighted(frame, self.contrast, frame, 0, self.brightness)
        return out

    def infared_effect(self, frame):
        cimg = frame
        inv_cimg = ~cimg.copy()
        inv_cimg[:, :, 1] = 0
        inv_cimg[:, :, 2] = 0

        inv_hsv = cv2.cvtColor(inv_cimg, cv2.COLOR_BGR2HSV)
        img_hsv = cv2.cvtColor(cimg, cv2.COLOR_BGR2HSV)

        dst = cv2.addWeighted(inv_hsv[:, :, 0], .9, img_hsv[:, :, 0], .9, 0)
        img_hsv[:, :, 0] = dst
        hue_cimg = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2BGR)
        frame = cv2.cvtColor(hue_cimg, cv2.COLOR_BGR2RGB)

        return frame

    def apply_colormap(self, frame):
        # Apply the specified colormap
        colormap_image = cv2.applyColorMap(frame, self.colormap)

        return colormap_image

    def process_video(self):
        try:
            # Open video file
            cap = cv2.VideoCapture(self.file_path)

            # Check if video file opened successfully
            if not cap.isOpened():
                print("Error: Unable to open video file")
                return

            # Get input video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            codec = cv2.VideoWriter_fourcc(*'mp4v')

            file_basename = os.path.basename(self.file_path).replace(".mp4", "")

            output_processed_file_path = os.path.join(self.output_dir, "{0}_processed_wihtout_audio.mp4".format(file_basename))

            # Define codec and create VideoWriter object
            out = cv2.VideoWriter(output_processed_file_path, codec, fps, (width, height))

            # Process each frame
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                # Apply night vision effect to the frame
                processed_frame = self.apply_night_vision(frame)

                # Write the processed frame to output video
                out.write(processed_frame)

                # Display the processed frame
                # cv2.imshow('Night Vision', processed_frame)
                self.worker_signals.update.emit(processed_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # Release resources
            cap.release()
            out.release()
            cv2.destroyAllWindows()

            # Merge processed video with original audio using moviepy
            original_clip = VideoFileClip(self.file_path)
            processed_clip = VideoFileClip(output_processed_file_path)
            final_clip = processed_clip.set_audio(original_clip.audio)

            self.output_file_path = os.path.join(self.output_dir, "{0}_processed_with_audio.mp4".format(file_basename))
            final_clip.write_videofile(self.output_file_path, codec='libx264', audio_codec='aac')
            self.worker_signals.finished.emit(True, "Video Processing finished successfully!")
        except Exception as e:
            error_message = f"An error occurred: {e}"
            print(error_message)
            self.worker_signals.finished.emit(False, f"Error occurred: {e}")



