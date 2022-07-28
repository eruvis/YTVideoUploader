import argparse
import logging
import os.path
from multiprocessing import Pool
from pathlib import Path

from ytvideouploader import YTVideoUploader
from typing import Optional


def run(task_n: int, video_path: str, video_title: Optional[str] = str,
        hide_notify: bool = False, headless: bool = False, fullscreen: bool = False):
    try:
        assert YTVideoUploader(task_n, video_path, video_title, hide_notify, headless, fullscreen).upload_video()
        logging.info('Task end. Video uploaded successfully!')  # debug
    except AssertionError:
        logging.error('Task end. Assertion error: video has not been uploaded!')  # debug
        return


def __clear_list_folder():
    dir_list = os.listdir(args.video)
    folder_list = []

    for i in dir_list:
        if os.path.isdir(Path(args.video) / i):
            folder_list.append(i)

    for f in folder_list:
        dir_list.remove(f)

    return dir_list


def __fill_video_list(vl):
    len_vl = len(vl)
    if args.video_count > len_vl:
        vl = vl * (args.video_count // len_vl)
        for i in range(args.video_count - len(vl)):
            vl.append(vl[i])
    elif args.video_count < len_vl:
        vl = vl[:args.video_count]

    return vl


def __create_args_list():
    args_list = []

    if os.path.isfile(args.video):
        for i, v in enumerate(range(args.video_count), 1):
            args_list.append((i,
                              args.video,
                              args.title,
                              args.hide_notify,
                              args.headless,
                              args.fullscreen))

    elif os.path.isdir(args.video):
        video_list = __clear_list_folder()
        video_list = __fill_video_list(video_list)

        for i, video in enumerate(video_list, 1):
            args_list.append((i,
                              str(Path(args.video) / video),
                              args.title,
                              args.hide_notify,
                              args.headless,
                              args.fullscreen))
    else:
        logging.error('Invalid path!')  # debug

    return args_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--title")
    parser.add_argument("--hide_notify", action='store_true', default=False)
    parser.add_argument("--headless", action='store_true', default=False)
    parser.add_argument("--fullscreen", action='store_true', default=False)
    parser.add_argument("--video_count", type=int, default=1)
    parser.add_argument("--threads", type=int, default=1)
    args = parser.parse_args()

    p = Pool(processes=args.threads)
    p.starmap(run, __create_args_list())
