import os
import sys
import logging
from bot import GitHubFollowBot, BotConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def validate_token(token: str) -> bool:
    valid_prefixes = ("ghp_", "gho_", "ghu_", "ghs_", "ghr_")
    return any(token.startswith(prefix) for prefix in valid_prefixes)


def main() -> int:
    logger.info("🚀 GitHub Follow Bot - Starting up")

    token         = os.getenv("GITHUB_TOKEN")
    target_user   = os.getenv("TARGET_USERNAME", "torvalds")
    daily_limit   = int(os.getenv("DAILY_LIMIT",  "300"))
    follow_limit  = int(os.getenv("FOLLOW_LIMIT", "50"))   # Fix: default 50
    min_delay     = int(os.getenv("MIN_DELAY",    "30"))
    max_delay     = int(os.getenv("MAX_DELAY",    "60"))

    if not token:
        logger.error(
            "❌ GITHUB_TOKEN environment variable not set!\n"
            "GitHub Actions: Settings > Secrets > FOLLOW_BOT_TOKEN"
        )
        return 1

    if not validate_token(token):
        logger.error(
            "❌ Invalid token format. "
            "Expected: ghp_... / gho_... / ghu_..."
        )
        return 1

    logger.info(f"🎯 Target      : {target_user}")
    logger.info(f"📊 Daily limit : {daily_limit}")
    logger.info(f"📊 Session limit: {follow_limit}")
    logger.info(f"⏱️  Delay       : {min_delay}s - {max_delay}s")

    config = BotConfig(
        daily_follow_limit=daily_limit,
        follow_limit=follow_limit,
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

        if results.get("session_followed", 0) == 0:
            if results.get("followed_today", 0) >= daily_limit:
                logger.info("ℹ️  Daily limit already reached")
            else:
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
