import requests
import time

class GitHubFollowBot:
    def __init__(self, token):
        self.token = token
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'
    
    def get_user_followers(self, username):
        """User කෙනෙකුගේ followers ගන්න"""
        url = f'{self.base_url}/users/{username}/followers'
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def follow_user(self, username):
        """User කෙනෙකුව follow කරන්න"""
        url = f'{self.base_url}/user/following/{username}'
        response = requests.put(url, headers=self.headers)
        return response.status_code == 204
    
    def auto_follow(self, target_username, limit=10):
        """Target user ගේ followers follow කරන්න"""
        followers = self.get_user_followers(target_username)
        
        count = 0
        for user in followers[:limit]:
            username = user['login']
            
            if self.follow_user(username):
                print(f"✅ Followed: {username}")
                count += 1
            else:
                print(f"❌ Failed: {username}")
            
            # Rate limit avoid කරන්න
            time.sleep(2)
        
        print(f"\n📊 Total followed: {count}")

# භාවිතා කරන විදිය
bot = GitHubFollowBot('your_github_token_here')
bot.auto_follow('torvalds', limit=5)
