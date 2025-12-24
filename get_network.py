from bs4 import BeautifulSoup
import requests
import os
soup = BeautifulSoup(requests.get("https://lczero.org/play/networks/bestnets/").content, 'html.parser')
links = soup.find_all('a')
weights = []
for link in links:
    if '.pb.gz' in link.get('href'):
        weights.append(link)
if os.path.isdir("lc0"):
    os.system(f"wget -P lc0 {str(weights[-1]).split('"')[1].split('"')[0]}")