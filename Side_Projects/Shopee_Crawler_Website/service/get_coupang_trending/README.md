# Coupang Trending Crawler Service

This service automatically crawls trending items from Coupang using Safari WebDriver and saves the results to CSV files.

## 📁 Directory Structure

```
service/get_coupang_trending/
├── get_trending_coupang_safari.py    # Main crawler script using Safari
├── run_coupang_crawler.sh            # Service runner script
├── com.user.coupang.crawler.daily.plist  # macOS Launch Agent configuration
├── install_service.sh                # Service installation script
├── uninstall_service.sh              # Service uninstallation script
├── manage_service.sh                 # Service management script
└── README.md                         # This file
```

## 🚀 Installation

### Prerequisites

1. **Safari Configuration**: Enable Safari remote automation:
   - Safari > Preferences > Advanced > Check "Show Develop menu in menu bar"
   - Develop menu > Allow Remote Automation

2. **Python Environment**: Ensure you have the required packages:
   ```bash
   pip install selenium pandas pytz
   ```

### Install the Service

```bash
cd service/get_coupang_trending
./install_service.sh
```

## 🛠️ Management

Use the management script for easy control:

```bash
# Check service status
./manage_service.sh status

# Start service immediately (for testing)
./manage_service.sh start

# Stop service
./manage_service.sh stop

# Restart service
./manage_service.sh restart

# View recent logs
./manage_service.sh logs

# Test the crawler manually
./manage_service.sh test

# Uninstall service
./manage_service.sh uninstall
```

## 📊 Service Details

- **Trigger**: Once per day at first login (perfect for daily machine shutdowns)
- **Smart Logic**: Only runs once per day, even if you log in multiple times
- **Categories**: Phone, Computer, Home Electronics (configurable in the script)
- **Output Location**: `../../data/ranking/`
- **Log Location**: `../../logs/`
- **Service Name**: `com.user.coupang.crawler.daily`

## 📝 Configuration

### Modify Categories

Edit `get_trending_coupang_safari.py` to change the categories:

```python
coupang_web_links = {
    "phone": "...",
    "computer": "...",
    "home_electronic": "..."
}
```

### Change Schedule

To modify when the service runs, edit `com.user.coupang.crawler.daily.plist`:

**Current: Run at Login (once per day)**
```xml
<key>RunAtLoad</key>
<true/>
```

**Alternative: Run at specific time**
```xml
<key>RunAtLoad</key>
<false/>
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>2</integer>  <!-- Change this for different hour -->
    <key>Minute</key>
    <integer>0</integer>  <!-- Change this for different minute -->
</dict>
```

After changing the schedule, reload the service:
```bash
./manage_service.sh uninstall
./manage_service.sh install
```

## 🔧 Manual Commands

```bash
# Check if service is running
launchctl list | grep coupang

# Start service immediately
launchctl start com.user.coupang.crawler.daily

# Stop service
launchctl stop com.user.coupang.crawler.daily

# View service configuration
cat ~/Library/LaunchAgents/com.user.coupang.crawler.daily.plist
```

## 📋 Output Format

The service generates CSV files with the following columns:
- `ranking`: Product ranking (1-120)
- `name`: Product name
- `link`: Product URL
- `price`: Product price (integer)

Files are saved as: `coupang_trending_{category}_{date}.csv`

## 🐛 Troubleshooting

### Check Logs
```bash
./manage_service.sh logs
```

### Common Issues

1. **Safari Permission Denied**: Make sure "Allow Remote Automation" is enabled
2. **Service Not Running**: Check if you're logged in (service requires active user session)
3. **Python Import Errors**: Verify virtual environment and package installation
4. **File Permission Errors**: Ensure scripts are executable (`chmod +x *.sh`)

### Log Files

- `../../logs/coupang_crawler_service.log` - Main service log
- `../../logs/coupang_crawler_error.log` - Error log
- `../../logs/launchd_stdout.log` - LaunchD standard output
- `../../logs/launchd_stderr.log` - LaunchD error output

## ⚠️ Important Notes

1. **Safari Visibility**: Safari windows will be visible during crawling (no headless mode)
2. **User Session Required**: Service only runs when you're logged in to macOS
3. **Network Dependency**: Requires internet connection to access Coupang
4. **Rate Limiting**: Built-in retry logic and delays to avoid being blocked

## 🔄 Updates

To update the crawler script:
1. Modify `get_trending_coupang_safari.py`
2. Test with `./manage_service.sh test`
3. Restart service if needed: `./manage_service.sh restart`
