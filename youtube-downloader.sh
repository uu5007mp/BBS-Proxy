#!/bin/bash

echo "Select an option:"
echo "1) Start the application"
echo "2) Stop and delete the application"

read -p "Enter your choice: " CHOICE

if [ "$CHOICE" == "1" ]; then
    git clone https://github.com/hirotomoki12345/youtube.git
    cd youtube

    npm install

    read -p "Please enter the port number: " PORT

    pm2 start npm --name "youtube-app" -- start --PORT=$PORT
    echo "Application started on port $PORT."

elif [ "$CHOICE" == "2" ]; then
    pm2 stop "youtube-app"
    pm2 delete "youtube-app"
    echo "Application stopped and deleted."

else
    echo "Invalid choice. Please run the script again and select a valid option."
fi
