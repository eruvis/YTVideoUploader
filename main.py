import argparse

from ytvideouploader import YTVideoUploader
from typing import Optional


def run(video_path: str, video_title: Optional[str] = str):
    assert YTVideoUploader(video_path, video_title).upload_video()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--title")
    args = parser.parse_args()
    run(args.video, args.title)
