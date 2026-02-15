python3 get_egtb.py
if [ ! -d "pgn-extract" ]; then
    git clone "https://github.com/kentdjb/pgn-extract.git"
fi
cd "pgn-extract"
make
cd ..
for year in $(seq -w 2013 2025); do
    if [ ! -d "${year}" ]; then
        mkdir $year
    fi
    if [ ! -s "${year}/${year}-12.bin" ]; then
        cd $year
        for month in $(seq -w 1 12); do
            if [ ! -s "${year}-${month}.bin" ]; then
                if [ ! -s "lichess_db_standard_rated_${year}-${month}.pgn.zst" ]; then
                    wget "https://database.lichess.org/standard/lichess_db_standard_rated_${year}-${month}.pgn.zst"
                fi
                pzstd -d "lichess_db_standard_rated_${year}-${month}.pgn.zst" | "../pgn-extract/pgn-extract" -t ../pgn_config.txt -7 -C -N -V "lichess_db_standard_rated_${year}-${month}.pgn"
                jja make --min-wins 10 --min-games 10 --output "${year}-${month}.bin" "lichess_db_standard_rated_${year}-${month}.pgn"
                sudo rm "lichess_db_standard_rated_${year}-${month}.pgn"
                sudo rm "lichess_db_standard_rated_${year}-${month}.pgn.zst"
            fi
        done
        cd ..
    fi
done