import argparse

from ytvideouploader import YTVideoUploader
from typing import Optional


def run(video_path: str, video_title: Optional[str] = str, headless: bool = False, fullscreen: bool = True):
    assert YTVideoUploader(video_path, video_title, headless, fullscreen).upload_video()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--title")
    parser.add_argument("--headless", type=bool, default=False)
    parser.add_argument("--fullscreen", type=bool, default=True)
    args = parser.parse_args()
    run(args.video, args.title, args.headless, args.fullscreen)
