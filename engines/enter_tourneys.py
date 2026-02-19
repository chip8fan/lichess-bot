import berserk
import datetime
import time
client = berserk.Client(session=berserk.TokenSession([line for line in open("config.yml")][0].split('"')[1].split('"')[0]), base_url="http://localhost:8080/")
while True:
    if datetime.datetime.now().hour == 7 and datetime.datetime.now().minute == 0 and datetime.datetime.now().second == 30 or datetime.datetime.now().hour == 19 and datetime.datetime.now().minute == 0 and datetime.datetime.now().second == 30:
        client.tournaments.join_arena(client.tournaments.tournaments_by_user("Human", nb=1)[0]['id'])
    time.sleep(1)