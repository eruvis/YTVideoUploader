import argparse
import os.path
import time
from multiprocessing import Pool
from pathlib import Path

from ytvideouploader import YTVideoUploader
from typing import Optional


def run(video_path: str, video_title: Optional[str] = str, headless: bool = False, fullscreen: bool = True):
    assert YTVideoUploader(video_path, video_title, headless, fullscreen).upload_video()


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
            print(vl[i])
            vl.append(vl[i])
    elif args.video_count < len_vl:
        vl = vl[:args.video_count]

    return vl


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--title")
    parser.add_argument("--headless", action='store_true', default=False)
    parser.add_argument("--fullscreen", action='store_true', default=False)
    parser.add_argument("--video_count", type=int, default=1)
    parser.add_argument("--threads", type=int, default=1)
    args = parser.parse_args()

    args_list = []
    if os.path.isfile(args.video):
        if args.video_count == 1:
            args_list.append((args.video, args.title, args.headless, args.fullscreen))
        else:
            video_list = __fill_video_list([args.video])
            for v in video_list:
                args_list.append((str(Path(args.video) / v), args.title, args.headless, args.fullscreen))
    elif os.path.isdir(args.video):
        video_list = __clear_list_folder()
        print(video_list, len(video_list))
        video_list = __fill_video_list(video_list)
        print(video_list, len(video_list))

        for v in video_list:
            args_list.append((str(Path(args.video) / v), args.title, args.headless, args.fullscreen))
    else:
        print('Invalid path')

    print(args_list)
    print(len(args_list))

    p = Pool(processes=args.threads)
    p.starmap(run, args_list)
