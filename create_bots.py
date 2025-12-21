import os
import chess.engine
for root, folders, files in os.walk(os.getcwd() + "/engines"):
    for file in files:
        file_name = os.path.join(root, file)
        if os.access(file_name, os.X_OK) and "." not in file_name:
            try:
                engine = chess.engine.SimpleEngine.popen_uci(file_name)
                engine.quit()
                binary_name = file_name.split("/")[-1]
                directory_name = file_name.split("/")
                directory_name.pop()
                directory_name = "/".join(directory_name) + "/"
                if os.path.isdir(binary_name) == False:
                    os.chdir("bots")
                    os.system("git clone https://github.com/lichess-bot-devs/lichess-bot.git")
                    os.rename("lichess-bot", binary_name)
                    os.rename(os.path.join(binary_name, "config.yml.default"), os.path.join(binary_name, "config.yml"))
                    lines = [
                        'token: ""',
                        'url: "http://localhost:8080/"',
                        'engine:',
                        f'  dir: {directory_name}',
                        f'  name: {binary_name}',
                        '  protocol: "uci"',
                        '  online_moves:',
                        '    lichess_cloud_analysis:',
                        '      enabled: true',
                        '      move_quality: "good"',
                        'challenge:',
                        '  accept_bot: true',
                        '  time_controls:',
                        '    - bullet',
                        '    - blitz',
                        '    - rapid',
                        '    - classical',
                        '  modes:',
                        '    - casual',
                        '    - rated',
                        '  variants:',
                        '    - standard'
                    ]
                    file = open(os.path.join(binary_name, "config.yml"), "w")
                    for line in lines:
                        file.write(line+"\n")
                    file.close()
                    os.chdir("..")
            except:
                pass