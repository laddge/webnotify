import os
import time
import datetime
import json
import hashlib
import requests
from lxml import html


def serialize(content):
    try:
        return html.tostring(content).decode()
    except Exception:
        return str(content)


def main():
    targets = os.getenv("TARGETS", "")
    updated = []
    try:
        with open("data.json") as f:
            data = json.load(f)
    except Exception:
        data = {}
    ndata = {}
    for i, target in enumerate(targets.split("\n")):
        if not target:
            continue
        print(f"[{int(time.time())}] Fetch url[{i}]")
        res0 = requests.get(target.split()[0])
        target_hash = hashlib.md5(target.encode()).hexdigest()
        if "text/html" in res0.headers.get("Content-Type") and len(target.split()) > 1:
            tree = html.fromstring(res0.text)
            xpath = target.split()[1:]
            content = ""
            for xp in xpath:
                content += "".join([serialize(el) for el in tree.xpath(xp)])
        else:
            content = res0.content
        content_hash = hashlib.md5(content.encode()).hexdigest()
        if data.get(target_hash) != content_hash:
            updated.append(target.split()[0])
        ndata[target_hash] = content_hash
    with open("data.json", "w") as f:
        json.dump(ndata, f)
    if not updated:
        print("Nothing updated.")
        return
    now = datetime.datetime.now().strftime("%b %d, %Y %H:%M:%S\n")
    line_text = now + "\n".join(list(set(updated)))
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
