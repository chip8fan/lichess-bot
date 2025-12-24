import copy
import shutil
import os
engines = open("engines.txt")
engine_releases = [["/".join(engine.rstrip().split("/")[0:len(engine.rstrip().split("/"))-1])+"/", engine.rstrip().split("/")[-1]] for engine in engines]
engines.close()
config = open("config.yml")
config_lines = [line.rstrip() for line in config]
config.close()
for engine in engine_releases:
    if os.path.isdir(engine[1]) == False:
        shutil.copytree("lichess-bot", engine[1])
        engine_lines = copy.deepcopy(config_lines)
        engine_lines[engine_lines.index('  dir: ""')] = f'  dir: "{engine[0]}"'
        engine_lines[engine_lines.index('  name: ""')] = f'  name: "{engine[1]}"'
        file = open(f"{engine[1]}/config.yml", "w")
        for line in engine_lines:
            file.write(line+"\n")
        file.close()