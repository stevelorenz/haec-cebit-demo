#! /bin/sh
#
# run_demo_local.sh
# Run demo with only one worker locally.

sudo -v

# Start Ryu
ryu run --observe-links ryu_haec.py &
sleep 3

# Run MaxiNet Frondend server
MaxiNetFrontendServer &
sleep 3

# Run MaxiNet worker
sudo MaxiNetWorker &
sleep 5

# Run demo script
python main.py
