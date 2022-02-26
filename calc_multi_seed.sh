#!/bin/bash

# bash calc_multi_seed.sh [filename] [num : 0 ~ num.txt]


if [ $2 ]; then
    end=$(($2-1))
else
    end=9
fi

rm score_log.txt && touch score_log.txt

for i in `seq 0 $end`
do
    num=$(printf "%04d\n" "$i")
    ./tester.exe python $1 < in/$num.txt > out 2>> score_log.txt
    printf "\r[ $((i + 1)) / $(($end + 1)) ]"
done
printf "\n"

python calc_total_score.py $end < score_log.txt
