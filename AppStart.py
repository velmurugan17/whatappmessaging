import os
import json

from selenium import webdriver


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
DRIVER_BIN = os.path.join(PROJECT_ROOT, "chromedriver")
print(DRIVER_BIN)
driver = webdriver.Chrome(executable_path=DRIVER_BIN)
driver.get("https://web.whatsapp.com")
print("Scan QR Code, And then Enter")
input()
print("Logged In")

executor_url = driver.command_executor._url
session_id = driver.session_id

driver_instance = {"url": executor_url, "session_id": session_id}

with open('instance_config.json', 'w') as f1:
    json.dump(driver_instance, f1)
