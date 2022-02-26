#!/bin/bash

# bash calc_selected_seed.sh [filename] [num : in/num.txt] [times=10]


if [ $3 ]; then
    end=$(($3-1))
else
    end=9
fi

rm score_log.txt && touch score_log.txt

num=$(printf "%04d\n" "$2")

for i in `seq 0 $end`
do
    ./tester.exe python $1 < in/$num.txt > out 2>> score_log.txt
    printf "\r[ $((i + 1)) / $(($end + 1)) ]"
done
printf "\n"

python calc_total_score.py $end < score_log.txt