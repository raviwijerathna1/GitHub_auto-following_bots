import os
import sys
import logging
from bot import GitHubFollowBot, BotConfig

# Bug #10 Fix - main.py ඇතුළේ logging configure කිරීම
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def validate_token(token: str) -> bool:
    """
    Bug #13 Fix - Token format validation
    GitHub tokens: ghp_, gho_, ghu_, ghs_, ghr_
    """
    valid_prefixes = ("ghp_", "gho_", "ghu_", "ghs_", "ghr_")
    return any(token.startswith(prefix) for prefix in valid_prefixes)


def main() -> int:
    """
    Bug #13 Fix - Return int exit code
    0 = success
    1 = auth error
    2 = network error  
    3 = unexpected error
    """
    logger.info("🚀 GitHub Follow Bot - Starting up")

    # Environment variables
    token = os.getenv("GITHUB_TOKEN")
    target_user = os.getenv("TARGET_USERNAME", "torvalds")

    # Bug #9 - int() conversion (already correct, kept for safety)
    daily_limit = int(os.getenv("DAILY_LIMIT", "300"))

    # Bug #11 Fix - FOLLOW_LIMIT default 100 (render.yaml + .env match)
    follow_limit = int(os.getenv("FOLLOW_LIMIT", "100"))

    min_delay = int(os.getenv("MIN_DELAY", "10"))
    max_delay = int(os.getenv("MAX_DELAY", "45"))

    # Token validation
    if not token:
        logger.error(
            "❌ GITHUB_TOKEN environment variable not set!\n"
            "GitHub Actions: Settings > Secrets > GITHUB_TOKEN"
        )
        return 1

    # Bug #13 Fix - Token format check
    if not validate_token(token):
        logger.error(
            "❌ Invalid token format. "
            "Expected: ghp_... / gho_... / ghu_..."
        )
        return 1

    logger.info(f"🎯 Target: {target_user}")
    logger.info(f"📊 Daily limit: {daily_limit} | Session limit: {follow_limit}")
    logger.info(f"⏱️  Delay: {min_delay}s - {max_delay}s")

    # Bug #12 Fix - follow_limit BotConfig වලට pass කිරීම
    config = BotConfig(
        daily_follow_limit=daily_limit,
        follow_limit=follow_limit,       # Bug #12 Fix
        min_delay=min_delay,
        max_delay=max_delay,
        max_pages=10,
        per_page=100
    )

    try:
        bot = GitHubFollowBot(token=token, config=config)

        results = bot.run(
            target_username=target_user,
            limit=follow_limit
        )

        logger.info("✅ Bot completed successfully")

        # Bug #13 Fix - meaningful exit based on results
        if results.get("session_followed", 0) == 0:
            if results.get("followed_today", 0) >= daily_limit:
                logger.info("ℹ️  Daily limit already reached")
                return 0
            logger.warning("⚠️  No users followed this session")

        return 0

    except PermissionError as e:
        logger.error(f"❌ Authentication failed: {e}")
        return 1

    except ConnectionError as e:
        logger.error(f"❌ Network error: {e}")
        return 2

    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)
        return 3


if __name__ == "__main__":
    sys.exit(main())
