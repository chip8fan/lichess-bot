python3 get_egtb.py
for year in $(seq -w 2020 2025); do
    if [ ! -d "elite-${year}" ]; then
        mkdir "elite-${year}"
    fi
    if [ ! -s "elite-${year}/${year}-12.bin" ]; then
        cd "elite-${year}"
        for month in $(seq -w 1 12); do
            if [ ! -s "${year}-${month}.bin" ]; then
                wget "https://database.nikonoel.fr/lichess_elite_${year}-${month}.zip"
                unzip "lichess_elite_${year}-${month}.zip"
                jja make --min-wins 10 --min-games 10 --output "${year}-${month}.bin" "lichess_elite_${year}-${month}.pgn"
                if [ ! -s "${year}-${month}.bin" ]; then
                    sudo rm "${year}-${month}.bin"
                fi
                sudo rm "lichess_elite_${year}-${month}.zip"
                sudo rm "lichess_elite_${year}-${month}.pgn"
            fi
        done
        cd ..
    fi
done