#!/data/data/com.termux/files/usr/bin/bash

clear
echo -e "\033[1;32m====================================================\033[0m"
echo -e "\033[1;35m 🛡️  RUDRAKSHA SHIELD - COMMERCIAL AUTH GATEWAY   \033[0m"
echo -e "\033[1;32m====================================================\033[0m"
echo -e "\033[1;36m[+] Gateway Endpoint: \033[1;33mhttp://127.0.0.1:5000\033[0m\n"

python3 app.py &
PID=$!

sleep 1.5
if command -v termux-open-url &> /dev/null; then
    termux-open-url "http://127.0.0.1:5000"
fi

wait $PID
