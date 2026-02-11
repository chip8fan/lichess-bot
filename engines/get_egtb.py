import os
import requests
import bs4
import sys
if os.path.isdir("syzygy"):
    sys.exit()
os.mkdir("syzygy")
os.chdir("syzygy")
dtz_links = bs4.BeautifulSoup(requests.get("https://tablebase.lichess.ovh/tables/standard/3-4-5-dtz/").content, 'html.parser').find_all("a")
for dtz_link in dtz_links:
    link = str(dtz_link).split('href="')[1].split('"')[0]
    if link.endswith(".rtbz"):
        with open(link, "wb") as file:
            file.write(requests.get(f"https://tablebase.lichess.ovh/tables/standard/3-4-5-dtz/{link}").content)
wdl_links = bs4.BeautifulSoup(requests.get("https://tablebase.lichess.ovh/tables/standard/3-4-5-wdl/").content, 'html.parser').find_all("a")
for wdl_link in wdl_links:
    link = str(wdl_link).split('href="')[1].split('"')[0]
    if link.endswith(".rtbw"):
        with open(link, "wb") as file:
            file.write(requests.get(f"https://tablebase.lichess.ovh/tables/standard/3-4-5-wdl/{link}").content)