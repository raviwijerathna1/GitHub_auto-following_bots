# GitHub Follow Bot 🤖

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![GitHub API](https://img.shields.io/badge/GitHub-API%20v3-black)
![License](https://img.shields.io/badge/License-MIT-green)

## ⚠️ Disclaimer
> මේ project එක **educational purposes** සඳහා පමණි.
> GitHub Terms of Service violation වෙන්න පුළුවන්.
> Use කරන්නේ ඔයාගේම වගකීමෙන්.

## 📖 Description
GitHub users automatically follow කරන Python bot එකක්.
Target user කෙනෙකුගේ followers list එකෙන් users follow කරනවා.

## ✨ Features
- ✅ Target user ගේ followers follow කරනවා
- ✅ Rate limit protection
- ✅ Follow success/fail tracking
- ✅ Custom follow limit

## 📋 Requirements
- Python 3.8+
- GitHub Personal Access Token

## 🛠️ Installation

### 1. Clone කරන්න
```bash
git clone https://github.com/yourusername/github-follow-bot
cd github-follow-bot
```

### 2. Dependencies Install කරන්න
```bash
pip install requests
```

### 3. GitHub Token හදන්න
```
GitHub → Settings → Developer Settings
→ Personal Access Tokens → Tokens (classic)
→ Generate New Token
→ "user:follow" permission select කරන්න
→ Token copy කරන්න
```

## 💻 Usage

```python
from bot import GitHubFollowBot

# Bot initialize කරන්න
bot = GitHubFollowBot('your_github_token_here')

# Auto follow කරන්න
bot.auto_follow('target_username', limit=10)
```

## 📁 Project Structure
```
github-follow-bot/
│
├── bot.py          # Main bot code
├── README.md       # Documentation
└── requirements.txt
```

## 📊 Output Example
```
✅ Followed: user1
✅ Followed: user2
❌ Failed: user3
✅ Followed: user4

📊 Total followed: 3
```

## ⚡ Rate Limits
| Type | Limit |
|------|-------|
| API Requests | 5000/hour |
| Sleep between follows | 2 seconds |

## 🤝 Contributing
Pull requests welcome!

1. Fork කරන්න
2. Feature branch හදන්න (`git checkout -b feature/amazing`)
3. Commit කරන්න (`git commit -m 'Add amazing feature'`)
4. Push කරන්න (`git push origin feature/amazing`)
5. Pull Request දාන්න

## 📄 License
MIT License - [LICENSE](LICENSE) file

