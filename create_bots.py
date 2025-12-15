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
                    os.system("git clone https://github.com/lichess-bot-devs/lichess-bot.git")
                    os.rename("lichess-bot", binary_name)
                    os.rename(os.path.join(binary_name, "config.yml.default"), os.path.join(binary_name, "config.yml"))
                    config_file = open(f"{binary_name}/config.yml")
                    config_lines = [l.rstrip() for l in config_file]
                    config_file.close()
                    opening_file = open(f"{binary_name}/lib/engine_wrapper.py")
                    opening_lines = [l.rstrip() for l in opening_file]
                    opening_file.close()
                    config_lines[1] = config_lines[1].replace("https://lichess.org/", "http://localhost:8080")
                    config_lines[4] = config_lines[4].replace("./engines/", directory_name)
                    config_lines[5] = config_lines[5].replace("engine_name", binary_name)
                    config_lines[60] = config_lines[60].replace("false", "true")
                    config_lines[97] = config_lines[97].replace("Move Overhead:", "# Move Overhead:")
                    config_lines[98] = config_lines[98].replace("Threads:", "# Threads:")
                    config_lines[99] = config_lines[99].replace("Hash:", "# Hash:")
                    config_lines[100] = config_lines[100].replace("SyzygyPath:", "# SyzygyPath:")
                    opening_lines[967] = opening_lines[967].replace("moves.sort(reverse=True)", "random_move = random.choice(moves)")
                    opening_lines[968] = opening_lines[968].replace("moves[0]", "random_move")
                    opening_lines[969] = opening_lines[969].replace("moves[0]", "random_move")
                    config_file = open(f"{binary_name}/config.yml", "w")
                    for line in config_lines:
                        config_file.write(line+"\n")
                    config_file.close()
                    opening_file = open(f"{binary_name}/lib/engine_wrapper.py", "w")
                    for line in opening_lines:
                        opening_file.write(line+"\n")
                    opening_file.close()
            except chess.engine.EngineTerminatedError:
                pass