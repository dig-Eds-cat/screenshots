import os
import pandas as pd
from playwright.sync_api import sync_playwright
from PIL import Image


out_dir = "screenshots"
os.makedirs(out_dir, exist_ok=True)

df = pd.read_csv("https://raw.githubusercontent.com/dig-Eds-cat/digEds_cat/refs/heads/main/digEds_cat.csv")

MAX_TIMEOUT = 5000
INGORE_EXISTING = True

print("fetching images")
failed = []

for i, row in df.iterrows():
    if row["Current availability"] == "yes":
        url = row["URL"]
        name = f'{row["id"]}.webp'
        f_name = os.path.join(out_dir, name)
        if os.path.exists(f_name) and INGORE_EXISTING:
            print(f"skipping {f_name}, already exists")
            continue
        print(f"saving screenshot from {url} as {f_name}")
        with sync_playwright() as p:
            browser = p.firefox.launch()
            try:
                page = browser.new_page(viewport={"width": 1200, "height": 800})
                page.set_default_timeout(MAX_TIMEOUT)
                page.set_default_navigation_timeout(MAX_TIMEOUT)
                page.goto(url)
                page.wait_for_timeout(1500)
                page.screenshot(path=f_name)
            except Exception as e:
                failed.append({
                    "url": url,
                    "error": str(e).replace('\n', ' ').replace('\t', ' ').strip()
                })
                continue
            browser.close()
        with Image.open(f_name) as my_image:
            my_image.save(f_name, 'webp', quality=80)
df = pd.DataFrame(failed)
df.to_csv("failed.csv", index=False)
