#!/bin/bash

echo -ne "\\033[2J\033[3;1f"
eval "cat ~/astralix/assets/banner.txt"
printf "\n\n\033[1;32mastralix is running!\033[0m"
