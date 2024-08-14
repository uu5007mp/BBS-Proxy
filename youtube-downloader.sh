#!/bin/bash


echo "Select an option:"
echo "1) Start the application"
echo "2) Stop and delete the application"
echo "3) Check application status"
echo "4) View application logs"

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

elif [ "$CHOICE" == "3" ]; then
    pm2 status "youtube-app"

elif [ "$CHOICE" == "4" ]; then
    pm2 logs "youtube-app"

else
    echo "Invalid choice. Please run the script again and select a valid option."
fi
