import argparse
from functools import partial
import re
import time
import datetime

import numpy as np
from PIL import Image, ImageDraw
import svgwrite
import gstreamer
import requests

from pose_engine import PoseEngine

EDGES = (
    ("nose", "left eye"),
    ("nose", "right eye"),
    ("nose", "left ear"),
    ("nose", "right ear"),
    ("left ear", "left eye"),
    ("right ear", "right eye"),
    ("left eye", "right eye"),
    ("left shoulder", "right shoulder"),
    ("left shoulder", "left elbow"),
    ("left shoulder", "left hip"),
    ("right shoulder", "right elbow"),
    ("right shoulder", "right hip"),
    ("left elbow", "left wrist"),
    ("right elbow", "right wrist"),
    ("left hip", "right hip"),
    ("left hip", "left knee"),
    ("right hip", "right knee"),
    ("left knee", "left ankle"),
    ("right knee", "right ankle"),
)


def shadow_text(dwg, x, y, text, font_size=16):
    dwg.add(
        dwg.text(
            text,
            insert=(x + 1, y + 1),
            fill="black",
            font_size=font_size,
            style="font-family:sans-serif",
        )
    )
    dwg.add(
        dwg.text(
            text,
            insert=(x, y),
            fill="white",
            font_size=font_size,
            style="font-family:sans-serif",
        )
    )


x = 0
report = True


def draw_pose(draw, dwg, pose, first=False, color="blue", threshold=0.3):
    global x, report

    xys = {}

    original_right_eye_y = 270

    if pose.score < threshold:
        return

    for label, keypoint in pose.keypoints.items():
        if keypoint.score < 0.8:
            continue
        if label == "right eye":
            print(
                " %-20s x=%-4d y=%-4d score=%.1f"
                % (label, keypoint.yx[1], keypoint.yx[0], keypoint.score)
            )
        xys[label] = (int(keypoint.yx[1]), int(keypoint.yx[0]))
        dwg.add(
            dwg.circle(
                center=(int(keypoint.yx[1]), int(keypoint.yx[0])),
                r=5,
                fill="cyan",
                fill_opacity=keypoint.score,
                stroke=color,
            )
        )

        if (
            label == "right eye"
            and abs(keypoint.yx[0] - original_right_eye_y) > 50
            and keypoint.yx[0] != 0
        ):
            x += 1

            print(x)

            print(abs(keypoint.yx[0] - original_right_eye_y))

            if x > 20:
                draw.ellipse((0, 0, 1000, 1000), fill=(255, 0, 0, 0))
                data = {
                    "time": str(datetime.datetime.now()),
                    "x_position": float(keypoint.yx[1]),
                    "y_position": float(keypoint.yx[0]),
                    "baseline_y_position": float(original_right_eye_y),
                    "score": float(keypoint.score)
                }

                if report == True:
                    requests.post("http://172.16.249.255:8000/event", json=data)
                    report = False

        if (
            label == "right eye"
            and abs(keypoint.yx[0] - original_right_eye_y) < 50
            and keypoint.yx[0] != 0
        ):
            x = 0
            report = True

        draw.ellipse(
            (
                int(keypoint.yx[1]) - 5,
                int(keypoint.yx[0]) - 5,
                int(keypoint.yx[1]) + 5,
                int(keypoint.yx[0]) + 5,
            ),
            fill=(255, 0, 0, 0),
        )

    for a, b in EDGES:
        if a not in xys or b not in xys:
            continue
        ax, ay = xys[a]
        bx, by = xys[b]
        dwg.add(dwg.line(start=(ax, ay), end=(bx, by), stroke=color, stroke_width=2))
        draw.line([(ax, ay), (bx, by)], fill=color, width=2)


def run(callback, use_appsrc=False):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--mirror", help="flip video horizontally", action="store_true")
    parser.add_argument("--model", help=".tflite model path.", required=False)
    parser.add_argument(
        "--res",
        help="Resolution",
        default="1280x720",
        choices=["480x360", "640x480", "1280x720"],
    )
    parser.add_argument(
        "--videosrc", help="Which video source to use", default="/dev/video0"
    )
    parser.add_argument("--h264", help="Use video/x-h264 input", action="store_true")
    args = parser.parse_args()

    default_model = "models/posenet_mobilenet_v1_075_%d_%d_quant_decoder_edgetpu.tflite"
    if args.res == "480x360":
        src_size = (640, 480)
        appsink_size = (480, 360)
        model = args.model or default_model % (353, 481)
    elif args.res == "640x480":
        src_size = (640, 480)
        appsink_size = (640, 480)
        model = args.model or default_model % (481, 641)
    elif args.res == "1280x720":
        src_size = (1280, 720)
        appsink_size = (1280, 720)
        model = args.model or default_model % (721, 1281)

    print("Loading model: ", model)
    engine = PoseEngine(model, mirror=args.mirror)
    gstreamer.run_pipeline(
        partial(callback, engine),
        src_size,
        appsink_size,
        use_appsrc=use_appsrc,
        mirror=args.mirror,
        videosrc=args.videosrc,
        h264input=args.h264,
    )


def main():
    last_time = time.monotonic()
    n = 0
    sum_fps = 0
    sum_process_time = 0
    sum_inference_time = 0

    out = Image.new("RGB", (1280, 720))
    draw = ImageDraw.Draw(out)

    def render_overlay(engine, image, svg_canvas):
        nonlocal n, sum_fps, sum_process_time, sum_inference_time, last_time, out, draw

        start_time = time.monotonic()
        outputs, inference_time = engine.DetectPosesInImage(image)
        end_time = time.monotonic()
        n += 1
        sum_fps += 1.0 / (end_time - last_time)
        sum_process_time += 1000 * (end_time - start_time) - inference_time
        sum_inference_time += inference_time
        last_time = end_time
        text_line = "PoseNet: %.1fms Frame IO: %.2fms TrueFPS: %.2f Nposes %d" % (
            sum_inference_time / n,
            sum_process_time / n,
            sum_fps / n,
            len(outputs),
        )

        shadow_text(svg_canvas, 10, 20, text_line)

        draw_pose(draw, svg_canvas, outputs[0])

        if n % 10 == 0:
            out.save("output.png")
            out = Image.new("RGB", (1280, 720))
            draw = ImageDraw.Draw(out)

    run(render_overlay)


if __name__ == "__main__":
    main()
