#!/bin/bash
echo "Stopping bbs-proxy..."
if pm2 stop bbs-proxy; then
    echo "bbs-proxy stopped successfully."
else
    echo "Error: Failed to stop bbs-proxy. Please check if the process is running."
    exit 1
fi
# 自動で検索して削除
echo "Searching for BBS-Proxy directory in /home/*..."
for user_dir in /home/*; do
    if [ -d "$user_dir/BBS-Proxy" ]; then
        echo "Found BBS-Proxy directory in $user_dir"
        echo "Removing BBS-Proxy directory..."
        if rm -rf "$user_dir/BBS-Proxy"; then
            echo "BBS-Proxy directory removed successfully from $user_dir"
        else
            echo "Error: Failed to remove BBS-Proxy directory from $user_dir. Please check if you have the necessary permissions."
            exit 1
        fi
    else
        echo "No BBS-Proxy directory found in $user_dir"
    fi
done

echo "All operations completed successfully."
