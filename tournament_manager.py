import berserk
import time
import os
while True:
    for root, folders, files in os.walk(os.getcwd() + "/bots"):
        for file in files:
            if file == "config.yml":
                file_name = os.path.join(root, file)
                config_file = open(file_name)
                config_lines = [line.rstrip() for line in config_file]
                config_file.close()
                session = berserk.TokenSession(token=config_lines[0].split('"')[1].split('"')[0])
                client = berserk.Client(session=session, base_url="http://localhost:8080/")
                try:
                    print(client.tournaments.join_arena(client.tournaments.tournaments_by_user("Human", nb=1)[0]['id']))
                except:
                    pass
    time.sleep(60*60*10)