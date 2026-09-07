import time
import requests

URL = "https://warmifans-hiteckgroupp.hf.space"

while True:
    try:
        r = requests.get(URL, timeout=10)
        print(f"Status: {r.status_code}")
    except Exception as e:
        print(e)
    time.sleep(300)