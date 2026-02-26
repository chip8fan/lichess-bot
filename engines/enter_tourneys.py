import berserk
import time
client = berserk.Client(session=berserk.TokenSession([line for line in open("config.yml")][0].split('"')[1].split('"')[0]), base_url="http://liladocker.duckdns.org:9663/")
while True:
    client.tournaments.join_arena(client.tournaments.tournaments_by_user("nguyencaptures", nb=1)[0]['id'])
    time.sleep(60*60)