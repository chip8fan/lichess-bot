import os
import requests
import bs4
import sys
if os.path.isdir("syzygy-6"):
    sys.exit()
os.mkdir("syzygy-6")
os.chdir("syzygy-6")
dtz_links = bs4.BeautifulSoup(requests.get("https://tablebase.lichess.ovh/tables/standard/6-dtz/").content, 'html.parser').find_all("a")
for dtz_link in dtz_links:
    link = str(dtz_link).split('href="')[1].split('"')[0]
    if link.endswith(".rtbz"):
        if os.path.isfile(link) == False or os.path.getsize(link) == 0:
            with open(link, "wb") as file:
                file.write(requests.get(f"https://tablebase.lichess.ovh/tables/standard/6-dtz/{link}").content)
wdl_links = bs4.BeautifulSoup(requests.get("https://tablebase.lichess.ovh/tables/standard/6-wdl/").content, 'html.parser').find_all("a")
for wdl_link in wdl_links:
    link = str(wdl_link).split('href="')[1].split('"')[0]
    if link.endswith(".rtbw"):
        if os.path.isfile(link) == False or os.path.getsize(link) == 0:
            with open(link, "wb") as file:
                file.write(requests.get(f"https://tablebase.lichess.ovh/tables/standard/6-wdl/{link}").content)