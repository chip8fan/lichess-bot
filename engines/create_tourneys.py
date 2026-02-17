import berserk
import datetime
import time
client = berserk.Client(session=berserk.TokenSession(open("human.txt", "rb").read().decode("utf-8")), base_url="http://localhost:8080/")
while True:
    if datetime.datetime.now().hour == 7 and datetime.datetime.now().minute == 0 and datetime.datetime.now().second == 0 or datetime.datetime.now().hour == 19 and datetime.datetime.now().minute == 0 and datetime.datetime.now().second == 0:
        client.tournaments.create_arena(clockTime=5, clockIncrement=3, minutes=720, rated=True, streakable=True, wait_minutes=60)
    time.sleep(1)