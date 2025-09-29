#!/bin/bash
# Setup script to automatically update stock prices

echo "Stock Price Update Setup"
echo "======================="

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if running on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - use launchd instead of cron
    echo "Setting up automated price updates using launchd (macOS)..."

    PLIST_FILE="$HOME/Library/LaunchAgents/com.stockapp.priceupdate.plist"

    cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.stockapp.priceupdate</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$PROJECT_DIR/update_prices.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <array>
        <dict>
            <key>Hour</key>
            <integer>9</integer>
            <key>Minute</key>
            <integer>30</integer>
        </dict>
        <dict>
            <key>Hour</key>
            <integer>12</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
        <dict>
            <key>Hour</key>
            <integer>16</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
    </array>
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/price_update.log</string>
    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/price_update_error.log</string>
</dict>
</plist>
EOF

    # Load the launch agent
    launchctl load "$PLIST_FILE"
    echo "✅ Price updates scheduled for 9:30 AM, 12:00 PM, and 4:00 PM daily"
    echo "   Logs will be written to: $PROJECT_DIR/price_update.log"

else
    # Linux - use cron
    echo "Setting up automated price updates using cron (Linux)..."

    # Add cron job (runs at market open, noon, and close)
    (crontab -l 2>/dev/null; echo "30 9 * * 1-5 cd $PROJECT_DIR && python3 update_prices.py >> price_update.log 2>&1") | crontab -
    (crontab -l 2>/dev/null; echo "0 12 * * 1-5 cd $PROJECT_DIR && python3 update_prices.py >> price_update.log 2>&1") | crontab -
    (crontab -l 2>/dev/null; echo "0 16 * * 1-5 cd $PROJECT_DIR && python3 update_prices.py >> price_update.log 2>&1") | crontab -

    echo "✅ Cron jobs added for weekdays at 9:30 AM, 12:00 PM, and 4:00 PM"
    echo "   Logs will be written to: $PROJECT_DIR/price_update.log"
fi

echo ""
echo "Manual Commands:"
echo "==============="
echo "Update prices now:           python3 update_prices.py"
echo "View update logs:           tail -f price_update.log"
echo "Test price API:             curl http://localhost:8000/api/prices/current"
echo ""
echo "The web app will now show real stock prices!"
echo "Refresh your browser at: http://localhost:8000"