# GitHub Auto Following Bot

Automatically follows GitHub users using GitHub Actions.

## Features
- Automated following via GitHub Actions
- Daily follow limits
- Rate limit handling
- Random delays to avoid detection
- Stats persistence via cache

## Setup

### 1. Add Secret
Go to `Settings > Secrets and variables > Actions`

| Secret | Value |
|--------|-------|
| `FOLLOW_BOT_TOKEN` | Your GitHub PAT token |

### 2. Add Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TARGET_USERNAME` | - | Target user to follow their followers |
| `DAILY_LIMIT` | 300 | Max follows per day |
| `FOLLOW_LIMIT` | 100 | Max follows per run |
| `MIN_DELAY` | 10 | Min delay between follows (seconds) |
| `MAX_DELAY` | 45 | Max delay between follows (seconds) |

### 3. Generate Token
GitHub > Settings > Developer settings >
Personal access tokens > Tokens (classic) >
Generate new token

Scopes: user:follow

text


### 4. Run
Actions > GitHub Follow Bot > Run workflow

text


## Schedule
Runs automatically 3 times per day:
- 09:00 IST
- 15:00 IST  
- 21:00 IST

## ⚠️ Disclaimer
This bot is for educational purposes only.
Use responsibly and within GitHub Terms of Service.
⚠️ Important Warning:
text

දැන් bot run වෙනවා - හොඳයි ✅

නමුත් දැනගන්න:
GitHub ToS Section 2:
"No automated following/unfollowing"

Account suspend වෙන්න පුළුවන්!
Limits අඩුවෙන් තියාගන්න සේෆ්:

FOLLOW_LIMIT = 50  (100 වෙනුවට)
MIN_DELAY    = 30  (10 වෙනුවට)
MAX_DELAY    = 60  (45 වෙනුවට)
