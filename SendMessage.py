import json
import shutil

from os import listdir, path, stat
from os.path import isfile, join

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import time

LOOKUP_DIR = "./filedir"
TARGET_DIR = "./dir2"


class MyHandler(FileSystemEventHandler):

    def __init__(self, driver, group_config):
        self.driver = driver
        self.conf = group_config

    def on_created(self, event):
        print(f"{event.src_path} is received!")
        send_message(self.driver, event.src_path, self.conf)


def send_message(driver, filename, group_config):
    with open(filename) as f1:
        data = f1.readlines()
    # sitename, status = data[0], data[-1]
    sent = False
    for site_details in data:
        for site_name in group_config.keys():
            if site_name in site_details:
                split_details = site_details.strip().split(',')
                d,t,name,status,groups = split_details[group_config[site_name]['date']],\
                                      split_details[group_config[site_name]['time']], \
                                      split_details[group_config[site_name]['site']],\
                                      split_details[group_config[site_name]['status']],\
                                      group_config[site_name]['group']
                if (name and status):
                    for group in groups:
                        inp_xpath_search = '//*[@id="side"]/div[1]/div/label/div/div[2]'
                        input_box_search = WebDriverWait(driver,20).until(lambda driver: driver.find_element_by_xpath(inp_xpath_search))
                        input_box_search.send_keys(group+Keys.ENTER)
                        time.sleep(2)
                        act_elem = driver.switch_to.active_element
                        act_elem.send_keys(f"{name} {status}"+Keys.ENTER)
                sent = True
    if sent:
        base_path = path.basename(filename)
        shutil.move(filename,path.join(TARGET_DIR,base_path))


def process_missed_files(driver, group_config):
    mtime = lambda f: stat(path.join(LOOKUP_DIR, f)).st_mtime
    sorted_files = list(sorted(listdir(LOOKUP_DIR), key=mtime))
    pending_files = [join(LOOKUP_DIR, f) for f in sorted_files if isfile(join(LOOKUP_DIR, f))]
    for file in pending_files:
        send_message(driver, file, group_config)



def main():
    with open('instance_config.json') as f1:
        driver_data = json.load(f1)

    with open('groupConf.json') as f1:
        group_config = json.load(f1)

    driver = webdriver.Remote(command_executor=driver_data['url'],
                              desired_capabilities={})
    driver.close()
    driver.session_id = driver_data['session_id']

    process_missed_files(driver, group_config)
    event_handler = MyHandler(driver, group_config)
    observer = Observer()
    observer.schedule(event_handler, path=LOOKUP_DIR, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    main()