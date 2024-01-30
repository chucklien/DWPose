import os
import gradio as gr
import sys
import cv2
import numpy as np
from moviepy.editor import VideoFileClip

sys.path.append('.')

from annotator.dwpose import DWposeDetector
from utils import get_fps, read_frames, save_videos_from_pil
from annotator.util import resize_image, HWC3
from PIL import Image

os.environ['GRADIO_ALLOW_FLAGGING'] = "never"
detector = DWposeDetector()

def video2pose(fps, source_video):
    output_path = "./pose.mp4"
    orig_fps = get_fps(source_video)
    frames = read_frames(source_video)
    frames = read_frames(source_video)
    kps_results = []
    for i, frame_pil in enumerate(frames):
        frame_pil = np.array(frame_pil, dtype=np.uint8)
        frame_pil = HWC3(frame_pil)
        frame_pil = resize_image(frame_pil, 512)
        result= detector(frame_pil)
        result = HWC3(result)
        img = resize_image(frame_pil, 512)
        H, W, C = img.shape
        result = cv2.resize(
            result, (W, H), interpolation=cv2.INTER_LINEAR
        )
        result = Image.fromarray(result)
        kps_results.append(result)

    save_videos_from_pil(kps_results, output_path, fps=orig_fps)
    print(orig_fps)
    if (int(orig_fps) != fps):
        clip = VideoFileClip(output_path)
        new_clip = clip.set_fps(fps)
        new_output_path = f"./pose_fps_{fps}.mp4"
        new_clip.write_videofile(new_output_path)
        output_path = new_output_path
    print(get_fps(output_path), output_path)
    return os.path.join(os.getcwd(), output_path)

app = gr.Interface(
    fn=video2pose,
    inputs=[gr.Number(value=20, label="fps"), gr.Video()],
    outputs=[gr.Video()],
    description="Tranform video to pose video"
)

app.launch(share=True)