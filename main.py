#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random
import subprocess
import sys
import time

from argparse import ArgumentParser


VALID_EXTENSIONS = {'.jpg', '.png', '.jpeg', '.gif'}
PIDFILE = '/tmp/i3-wallpapers-{}.pid'.format(os.getuid())


# Check if file ends with valid picture extension
def is_valid_picture(filename):
    name, ext = os.path.splitext(filename)
    return ext.lower() in VALID_EXTENSIONS


def get_picture_list(directory):
    directory = os.path.abspath(directory)
    pictures = []
    for item in os.listdir(directory):
        full = os.path.join(directory, item)
        if os.path.isfile(full) and is_valid_picture(full):
            pictures.append(full)
    return pictures


# Handle Command Line Arguments
def handle_arguments():
    p = ArgumentParser(description='Use directory of pictures as wallpapers.')
    p.add_argument('directory', help='Directory to use as wallpaper source')
    p.add_argument('-r', '--random', action='store_true', default=False,
                   help='Randomize wallpaper order (default: %(default)s)')
    p.add_argument('-t', '--time', type=int, default=5, help='Minutes '
                   'to display one wallpaper before change '
                   '(default: %(default).1f)')
    args = p.parse_args()
    print(args)
    return args


def is_running():
    try:
        with open(PIDFILE) as fp:
            pid = int(fp.read())
        return os.kill(pid, 0)
    except Exception:
        return False


def randomize_pictures(pictures):
    if len(pictures) <= 1:
        return pictures
    first = pictures[0]
    while True:
        random.shuffle(pictures)
        if first != pictures[0]:
            return pictures


def loop(pictures, duration):
    for pic in pictures:
        start = time.monotonic()
        subprocess.run(['feh', '--bg-scale', pic])
        time.sleep(duration * 60 - (time.monotonic() - start))


def main():
    args = handle_arguments()
    pictures = get_picture_list(args.directory)
    if is_running():
        print('Script already running')
        return
    with open(PIDFILE, 'w') as fp:
        fp.write(str(os.getpid()))
    try:
        while True:
            if args.random:
                pictures = randomize_pictures(pictures)
            loop(pictures, args.time)
    except KeyboardInterrupt:
        print('\rClosing now...')
    finally:
        os.remove(PIDFILE)


if __name__ == "__main__":
    main()
