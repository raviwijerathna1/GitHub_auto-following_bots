import requests
import time
import random
import os
import json
import logging
from datetime import datetime, date
from dataclasses import dataclass, field
from typing import Optional

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


@dataclass
class BotConfig:
    """Bot සඳහා configuration settings"""
    daily_follow_limit: int = 300        # දවසකට උපරිම follows
    min_delay: int = 10                  # අවම delay (තත්පර)
    max_delay: int = 45                  # උපරිම delay (තත්පර)
    rate_limit_threshold: int = 50       # Rate limit warning threshold
    max_pages: int = 10                  # Pagination - උපරිම pages
    per_page: int = 100                  # එක් page එකකට users


@dataclass
class BotStats:
    """Bot statistics track කිරීම"""
    followed_today: int = 0
    failed_today: int = 0
    total_requests: int = 0
    session_start: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )
    last_run_date: str = field(
        default_factory=lambda: date.today().isoformat()
    )


class RateLimitError(Exception):
    """GitHub Rate Limit exceeded"""
    pass


class GitHubFollowBot:
    """
    GitHub Follow Bot
    - Pagination සහිතව followers ගැනීම
    - Rate limit නිවැරදිව handle කිරීම
    - Random delays සහ daily caps
    - සම්පූර්ණ error handling
    """

    STATS_FILE = "bot_stats.json"

    def __init__(self, token: str, config: Optional[BotConfig] = None):
        if not token:
            raise ValueError("GitHub token required")

        self.token = token
        self.config = config or BotConfig()
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            # Bot identify කිරීම - ToS requirement
            "User-Agent": "GitHub-Follow-Bot/1.0"
        }

        # Stats load කිරීම
        self.stats = self._load_stats()

        # Daily reset check
        self._check_daily_reset()

    # -------------------------------------------------------------------------
    # Stats Management
    # -------------------------------------------------------------------------

    def _load_stats(self) -> BotStats:
        """Saved stats load කිරීම"""
        try:
            if os.path.exists(self.STATS_FILE):
                with open(self.STATS_FILE, "r") as f:
                    data = json.load(f)
                    return BotStats(**data)
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Stats file error: {e}. Starting fresh.")

        return BotStats()

    def _save_stats(self) -> None:
        """Current stats save කිරීම"""
        try:
            with open(self.STATS_FILE, "w") as f:
                json.dump(self.stats.__dict__, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save stats: {e}")

    def _check_daily_reset(self) -> None:
        """නව දිනයක් නම් stats reset කිරීම"""
        today = date.today().isoformat()

        if self.stats.last_run_date != today:
            logger.info(
                f"📅 New day detected. Resetting daily stats. "
                f"(Previous: {self.stats.last_run_date})"
            )
            self.stats.followed_today = 0
            self.stats.failed_today = 0
            self.stats.last_run_date = today
            self._save_stats()

    # -------------------------------------------------------------------------
    # Rate Limit Handling
    # -------------------------------------------------------------------------

    def _handle_rate_limit(self, response: requests.Response) -> None:
        """
        GitHub rate limit headers නිවැරදිව handle කිරීම

        Headers:
        - X-RateLimit-Remaining: ඉතිරි requests ගණන
        - X-RateLimit-Reset: Reset වන Unix timestamp
        """
        remaining = int(response.headers.get("X-RateLimit-Remaining", 100))
        reset_timestamp = int(response.headers.get("X-RateLimit-Reset", 0))

        logger.debug(f"Rate limit remaining: {remaining}")

        if remaining < self.config.rate_limit_threshold:
            wait_seconds = max(0, reset_timestamp - time.time())

            logger.warning(
                f"⚠️  Rate limit low: {remaining} requests remaining. "
                f"Waiting {wait_seconds:.0f}s until reset."
            )

            # Reset time දක්වා wait කිරීම + buffer
            time.sleep(wait_seconds + 5)

        # Hard limit - 0 ට ආසන්නව
        if remaining <= 1:
            raise RateLimitError(
                f"Rate limit exhausted. "
                f"Resets at: {datetime.fromtimestamp(reset_timestamp)}"
            )

    def _random_delay(self) -> None:
        """Random delay - bot detection avoid කිරීම"""
        delay = random.randint(
            self.config.min_delay,
            self.config.max_delay
        )
        logger.info(f"⏳ Waiting {delay} seconds...")
        time.sleep(delay)

    # -------------------------------------------------------------------------
    # API Requests
    # -------------------------------------------------------------------------

    def _make_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> requests.Response:
        """
        Central request handler
        - Error handling
        - Rate limit checking
        - Stats tracking
        """
        try:
            response = requests.request(
                method,
                url,
                headers=self.headers,
                timeout=30,  # Connection timeout
                **kwargs
            )

            self.stats.total_requests += 1

            # Rate limit check - GET requests සඳහා
            if method.upper() == "GET":
                self._handle_rate_limit(response)

            # Status code handling
            if response.status_code == 401:
                raise PermissionError(
                    "❌ Invalid token. Check your GITHUB_TOKEN."
                )
            elif response.status_code == 403:
                raise RateLimitError(
                    "❌ Forbidden. Rate limit or permissions issue."
                )
            elif response.status_code == 404:
                raise ValueError(f"❌ Not found: {url}")
            elif response.status_code == 422:
                raise ValueError(
                    "❌ Unprocessable Entity. Check request parameters."
                )

            # 2xx නොවන responses handle කිරීම
            if response.status_code not in (200, 204):
                response.raise_for_status()

            return response

        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                "❌ Network error. Check internet connection."
            )
        except requests.exceptions.Timeout:
            raise TimeoutError(
                "❌ Request timed out. GitHub may be slow."
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Request failed: {e}")

    # -------------------------------------------------------------------------
    # Core Functions
    # -------------------------------------------------------------------------

    def get_followers_with_pagination(self, username: str) -> list[str]:
        """
        Pagination handle කරමින් සියලු followers ගැනීම

        GitHub API default: 30 per page
        Maximum per page: 100
        """
        all_followers = []
        page = 1

        logger.info(f"📋 Fetching followers for: {username}")

        while page <= self.config.max_pages:
            url = (
                f"{self.base_url}/users/{username}/followers"
                f"?per_page={self.config.per_page}&page={page}"
            )

            try:
                response = self._make_request("GET", url)
                followers_page = response.json()

                # Empty page = අවසාන page
                if not followers_page:
                    logger.info(
                        f"✅ All pages fetched. "
                        f"Total: {len(all_followers)} followers"
                    )
                    break

                # Usernames extract කිරීම
                usernames = [user["login"] for user in followers_page]
                all_followers.extend(usernames)

                logger.info(
                    f"  📄 Page {page}: {len(usernames)} followers "
                    f"(Total so far: {len(all_followers)})"
                )

                # Daily limit check
                if len(all_followers) >= self.config.daily_follow_limit:
                    logger.info(
                        f"🛑 Reached daily limit threshold. "
                        f"Stopping pagination."
                    )
                    break

                page += 1

                # Pages අතර small delay
                time.sleep(random.uniform(1, 3))

            except (RateLimitError, PermissionError) as e:
                logger.error(f"Critical error during pagination: {e}")
                break
            except Exception as e:
                logger.warning(f"Page {page} error: {e}. Stopping pagination.")
                break

        return all_followers

    def check_already_following(self, username: str) -> bool:
        """දැනටමත් follow කරනවාද check කිරීම"""
        url = f"{self.base_url}/user/following/{username}"

        try:
            response = self._make_request("GET", url)
            # 204 = following, 404 = not following
            return response.status_code == 204
        except ValueError:
            # 404 = not following
            return False
        except Exception as e:
            logger.debug(f"Could not check following status for {username}: {e}")
            return False

    def follow_user(self, username: str) -> bool:
        """
        User කෙනෙකුව follow කිරීම

        Returns:
            True  - follow සාර්ථකයි
            False - follow අසාර්ථකයි
        """
        # Daily limit check
        if self.stats.followed_today >= self.config.daily_follow_limit:
            logger.warning(
                f"🛑 Daily follow limit reached: "
                f"{self.stats.followed_today}/{self.config.daily_follow_limit}"
            )
            return False

        url = f"{self.base_url}/user/following/{username}"

        try:
            response = self._make_request("PUT", url)

            if response.status_code == 204:
                self.stats.followed_today += 1
                self._save_stats()
                return True

            return False

        except (PermissionError, RateLimitError) as e:
            logger.error(f"Cannot follow {username}: {e}")
            self.stats.failed_today += 1
            self._save_stats()
            return False
        except Exception as e:
            logger.warning(f"Failed to follow {username}: {e}")
            self.stats.failed_today += 1
            self._save_stats()
            return False

    # -------------------------------------------------------------------------
    # Main Bot Flow
    # -------------------------------------------------------------------------

    def run(self, target_username: str, limit: Optional[int] = None) -> dict:
        """
        Main bot execution

        Args:
            target_username: Follow කළ යුතු user ගේ followers target
            limit: Follow කළ යුතු maximum count (None = daily limit)

        Returns:
            Session stats dictionary
        """
        # Effective limit calculate කිරීම
        remaining_daily = (
            self.config.daily_follow_limit - self.stats.followed_today
        )

        if remaining_daily <= 0:
            logger.warning("🛑 Daily follow limit already reached today.")
            return self._get_session_summary()

        effective_limit = min(
            limit or self.config.daily_follow_limit,
            remaining_daily
        )

        logger.info("=" * 50)
        logger.info(f"🤖 GitHub Follow Bot Starting")
        logger.info(f"🎯 Target: {target_username}")
        logger.info(f"📊 Will follow up to: {effective_limit} users")
        logger.info(
            f"📅 Today's progress: "
            f"{self.stats.followed_today}/{self.config.daily_follow_limit}"
        )
        logger.info("=" * 50)

        # Followers ගැනීම pagination සහිතව
        followers = self.get_followers_with_pagination(target_username)

        if not followers:
            logger.error(f"No followers found for {target_username}")
            return self._get_session_summary()

        logger.info(f"\n🚀 Starting to follow {effective_limit} users...\n")

        session_followed = 0
        session_skipped = 0

        for username in followers[:effective_limit]:
            # Daily limit recheck (loop ඇතුළේ)
            if self.stats.followed_today >= self.config.daily_follow_limit:
                logger.warning("🛑 Daily limit reached during session.")
                break

            # Already following check
            if self.check_already_following(username):
                logger.info(f"⏭️  Already following: {username}")
                session_skipped += 1
                continue

            # Follow attempt
            if self.follow_user(username):
                logger.info(
                    f"✅ Followed: {username} "
                    f"({self.stats.followed_today}/"
                    f"{self.config.daily_follow_limit} today)"
                )
                session_followed += 1
            else:
                logger.warning(f"❌ Failed: {username}")

            # Random delay - bot detection avoid
            self._random_delay()

        return self._get_session_summary(session_followed, session_skipped)

    def _get_session_summary(
        self,
        followed: int = 0,
        skipped: int = 0
    ) -> dict:
        """Session summary return කිරීම"""
        summary = {
            "session_followed": followed,
            "session_skipped": skipped,
            "followed_today": self.stats.followed_today,
            "failed_today": self.stats.failed_today,
            "total_requests": self.stats.total_requests,
            "daily_limit": self.config.daily_follow_limit,
            "remaining_today": max(
                0,
                self.config.daily_follow_limit - self.stats.followed_today
            )
        }

        logger.info("\n" + "=" * 50)
        logger.info("📊 SESSION SUMMARY")
        logger.info("=" * 50)
        for key, value in summary.items():
            logger.info(f"  {key}: {value}")
        logger.info("=" * 50)

        return summary
