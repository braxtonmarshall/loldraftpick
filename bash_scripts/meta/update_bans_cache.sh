#!/bin/bash

# Start Celery
cd /home/mars/Workspace/Python/Loldraft.gg/ && source /home/mars/Workspace/Python/Loldraft.gg/.venv/bin/activate
#sudo rabbitmqctl purge_queue loldraft -p marsvhost
#sudo rabbitmqctl purge_queue loldraft_calcs -p marsvhost
#celery -A loldraft worker -Q loldraft --uid 1000 --concurrency 4 --prefetch-multiplier 1 --max-tasks-per-child 1 &
#celery -A loldraft worker -Q loldraft_calcs --uid 1000 --concurrency 4 --prefetch-multiplier 1 --max-tasks-per-child 10 &

# All Patches
printf "Starting Script for Diamond 4 on All Patches for Season 10..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.01/diamond4.sh &&
printf "Starting Script for Diamond 2 on All Patches for Season 10..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.01/diamond2.sh &&
printf "Starting Script for Master on All Patches for Season 10..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.01/master.sh &&
printf "Starting Script for Grandmaster on All Patches for Season 10..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.01/grandmaster.sh &&
printf "Starting Script for Challenger on All Patches for Season 10..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.01/challenger.sh &&
# 10.16
printf "Starting Script for Diamond 4 on Patch 10.16..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.16/diamond4.sh &&
printf "Starting Script for Diamond 2 on Patch 10.16..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.16/diamond2.sh &&
printf "Starting Script for Master on Patch 10.16..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.16/master.sh &&
printf "Starting Script for Grandmaster on Patch 10.16..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.16/grandmaster.sh &&
printf "Starting Script for Challenger on Patch 10.16..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.16/challenger.sh &&
# 10.17
printf "Starting Script for Diamond 4 on Patch 10.17..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.17/diamond4.sh &&
printf "Starting Script for Diamond 2 on Patch 10.17..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.17/diamond2.sh &&
printf "Starting Script for Master on Patch 10.17..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.17/master.sh &&
printf "Starting Script for Grandmaster on Patch 10.17..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.17/grandmaster.sh &&
printf "Starting Script for Challenger on Patch 10.17..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.17/challenger.sh &&
# 10.18
printf "Starting Script for Diamond 4 on Patch 10.18..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.18/diamond4.sh &&
printf "Starting Script for Diamond 2 on Patch 10.18..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.18/diamond2.sh &&
printf "Starting Script for Master on Patch 10.18..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.18/master.sh &&
printf "Starting Script for Grandmaster on Patch 10.18..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.18/grandmaster.sh &&
printf "Starting Script for Challenger on Patch 10.18..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.18/challenger.sh &&
# 10.19
printf "Starting Script for Diamond 4 on Patch 10.19..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.19/diamond4.sh &&
printf "Starting Script for Diamond 2 on Patch 10.19..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.19/diamond2.sh &&
printf "Starting Script for Master on Patch 10.19..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.19/master.sh &&
printf "Starting Script for Grandmaster on Patch 10.19..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.19/grandmaster.sh &&
printf "Starting Script for Challenger on Patch 10.19..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.19/challenger.sh &&
# 10.20
printf "Starting Script for Diamond 4 on Patch 10.20..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.20/diamond4.sh &&
printf "Starting Script for Diamond 2 on Patch 10.20..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.20/diamond2.sh &&
printf "Starting Script for Master on Patch 10.20..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.20/master.sh &&
printf "Starting Script for Grandmaster on Patch 10.20..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.20/grandmaster.sh &&
printf "Starting Script for Challenger on Patch 10.20..." &&
bash /home/mars/Workspace/Python/Loldraft.gg/bash_scripts/individual/Patch-10.20/challenger.sh
