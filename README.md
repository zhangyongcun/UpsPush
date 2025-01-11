# UPS Monitor

A Python-based monitoring system for Santak UPS devices with Bark notification integration.

## Features

- Real-time UPS status monitoring
- Power state change notifications via Bark
- Battery status monitoring
- Detailed status logging

## Requirements

- Python 3.6+
- hidapi library
- Bark app (for notifications)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/zhangyongcun/UpsPush.git
cd /opt/UpsPush
```

2. Generate environment configuration:
```bash
chmod +x generate_env.sh
./generate_env.sh
```
The script will:
- Detect your UPS device's Vendor ID and Product ID
- Generate a .env file with the correct device IDs

3. Create and activate virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Configure environment variables:
Edit the generated `.env` file and update your Bark API key and other preferences:
```bash
vim .env
```

## Supervisor Configuration

The application can be run as a service using supervisor. Create a configuration file at `/etc/supervisor/conf.d/ups_push.conf`:

```ini
[program:ups_push]
command=/opt/UpsPush/.venv/bin/python /opt/UpsPush/main.py
directory=/opt/UpsPush
user=root
autostart=true
autorestart=true
logfile=/var/log/supervisord.log
logfile_maxbytes=50MB
logfile_backups=10
loglevel=info
stderr_logfile=/var/log/ups_push.err.log
stdout_logfile=/var/log/ups_push.out.log
environment=PYTHONUNBUFFERED=1
```

Then reload supervisor:
```bash
supervisorctl reread
supervisorctl update
supervisorctl start ups_push
```

## Usage

If running manually (without supervisor):
```bash
python main.py
```

The program will:
- Connect to your UPS device
- Monitor power status continuously
- Send notifications on power events
- Display real-time status in console

## Monitoring States

The system monitors:
- AC power presence
- Battery status
- Charging status
- Load status
- Device connection status

## Notifications

Notifications are sent via Bark when:
- Power outage occurs
- Power is restored
- Battery is low
- Device connection is lost

## License

MIT
