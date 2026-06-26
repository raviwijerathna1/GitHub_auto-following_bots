import os
import sys
import logging
from bot import GitHubFollowBot, BotConfig

logger = logging.getLogger(__name__)


def main():
    # Environment variables
    token = os.getenv("GITHUB_TOKEN")
    target_user = os.getenv("TARGET_USERNAME", "torvalds")
    daily_limit = int(os.getenv("DAILY_LIMIT", "300"))
    follow_limit = int(os.getenv("FOLLOW_LIMIT", "50"))
    min_delay = int(os.getenv("MIN_DELAY", "10"))
    max_delay = int(os.getenv("MAX_DELAY", "45"))

    # Token validation
    if not token:
        logger.error(
            "GITHUB_TOKEN environment variable not set!\n"
            "Render Dashboard > Environment > Add: GITHUB_TOKEN"
        )
        sys.exit(1)

    # Config setup
    config = BotConfig(
        daily_follow_limit=daily_limit,
        min_delay=min_delay,
        max_delay=max_delay,
        max_pages=10,
        per_page=100
    )

    try:
        # Bot initialize
        bot = GitHubFollowBot(token=token, config=config)

        # Bot run
        results = bot.run(
            target_username=target_user,
            limit=follow_limit
        )

        logger.info("✅ Bot completed successfully")
        return results

    except PermissionError as e:
        logger.error(f"Authentication failed: {e}")
        sys.exit(1)
    except ConnectionError as e:
        logger.error(f"Network error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
