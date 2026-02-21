import bs4
import requests
network = str([link for link in bs4.BeautifulSoup(requests.get("https://lczero.org/play/networks/bestnets/").content, 'html.parser').find_all("a") if ".pb.gz" in str(link)][0]).split('"')[1].split('"')[0]
with open(network.split("/")[-1], "wb") as file:
    print(f"Downloading network from {network}...")
    file.write(requests.get(network).content)