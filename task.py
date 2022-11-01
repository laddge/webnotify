import os
import time
import datetime
import json
import hashlib
import requests


def main():
    urls = os.getenv("URLS", "")
    updated = []
    try:
        with open("data.json") as f:
            data = json.load(f)
    except Exception:
        data = {}
    ndata = {}
    for i, url in enumerate(urls.split("\n")):
        if not url:
            continue
        print(f"[{int(time.time())}] Fetch url[{i}]")
        res0 = requests.get(url)
        url_hash = hashlib.md5(url.encode()).hexdigest()
        body_hash = hashlib.md5(res0.content).hexdigest()
        if data.get(url_hash) != body_hash:
            updated.append(url)
        ndata[url_hash] = body_hash
    with open("data.json", "w") as f:
        json.dump(ndata, f)
    if not updated:
        print("Nothing updated.")
        return
    now = datetime.datetime.now().strftime("%b %d, %Y %H:%M:%S\n")
    line_text = now + "\n".join(updated)
    res1 = requests.post(
        "https://notify-api.line.me/api/notify",
        headers={"Authorization": f"Bearer {os.getenv('LINE_TOKEN')}"},
        data={"message": line_text},
    )
    if str(res1.status_code)[0] != "2":
        raise Exception("LINE Notify request error.")
    print(f"{len(updated)} pages updated.")


if __name__ == "__main__":
    main()
