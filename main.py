import sys
import argparse
import configparser
import csv
import logging
import logging_config
import time
import schedule
from datetime import datetime
from pathlib import Path

from utils.utils import is_supported_os, get_active_app_name
from counter.key_counter import key_counter
from counter.mouse_counter import mouse_counter
from monitor.key_monitor import create_key_monitor
from monitor.mouse_moitor import create_mouse_monitor
from exceptions import UnsupportedException

log = logging.getLogger(__name__)


def write_head(out_file_path):
    header = ['date', 'user_name', 'alphanumeric_key_count', 'special_key_count', 'keyboard_activity',
              'mouse_movement', 'mouse_click_count', 'mouse_scroll_count', 'mouse_activity', 'active_app_name']
    with open(out_file_path, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(header)


def write_data(out_file_path, now, user_name, app_name):
    data = [now, user_name, key_counter.alphanumeric, key_counter.special,
            (key_counter.alphanumeric + key_counter.special), mouse_counter.movement, mouse_counter.click,
            mouse_counter.scroll, (mouse_counter.movement + mouse_counter.click + mouse_counter.scroll), app_name]
    with open(out_file_path, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(data)


def job(out_file_path, user):
    now = "{0:%Y-%m-%d %H:%M:%S}".format(datetime.now())
    app_name = get_active_app_name()
    write_data(out_file_path, now, user, app_name)
    key_counter.reset()
    mouse_counter.reset()


def main():
    # check OS
    is_supported_os()

    # parse argument
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf', default='pynput.conf', type=str)
    parser.add_argument('--out', default='data.csv', type=str)
    args = parser.parse_args()
    log.info("parse argument. --conf = {0}, --out = {1}".format(args.conf, args.out))

    # parse config
    conf_file_path = args.conf
    config = configparser.ConfigParser()
    config.read(conf_file_path, 'UTF-8')
    conf = config['CONF']
    user = conf['USER']

    # output path
    out_file_path = args.out
    out_file = Path(out_file_path)
    if out_file.is_file():
        pass
    else:
        out_file.touch()
        write_head(out_file_path)

    # start keyboard or mouse event
    key_monitor = create_key_monitor()
    mouse_monitor = create_mouse_monitor()
    key_monitor.start()
    mouse_monitor.start()

    # setting job
    schedule.every(10).seconds.do(job, out_file_path, user)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    try:
        is_supported_os()
        main()
    except UnsupportedException as ue:
        log.error(ue)
        sys.exit(1)
