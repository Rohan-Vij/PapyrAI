#!/bin/bash

PYTHON_EXEC=$(which python)
SCRIPT_PATH="$(dirname "$(readlink -f "$0")")/send_newsletter.py"

(crontab -l 2>/dev/null; echo "0 10 * * 6 $PYTHON_EXEC $SCRIPT_PATH") | crontab -

# To run:
# chmod +x schedule_newsletter.sh
# ./schedule_newsletter.sh