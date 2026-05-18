import logging
from dataclasses import dataclass
from threading import Lock
from typing import Dict


logger = logging.getLogger(__name__)


@dataclass
class UserQuota:
    username: str
    quota: int
    executed: int = 0


class InMemoryQuotaStore:
    """
    Untuk versi awal, quota disimpan di memory.

    Untuk production scale:
    - ganti ini dengan database transaction
    - atau Redis atomic counter
    """

    def __init__(self, users: Dict[str, Dict[str, int]]):
        self._lock = Lock()
        self._users: Dict[str, UserQuota] = {}

        for username, config in users.items():
            quota = config.get("quota", 0)
            executed = config.get("executed", 0)

            if quota < 0:
                raise ValueError(f"Invalid quota for user: {username}")

            self._users[username] = UserQuota(
                username=username,
                quota=quota,
                executed=executed,
            )

    def has_user(self, username: str) -> bool:
        return username in self._users

    def try_reserve(self, username: str) -> bool:
        """
        Reserve quota sebelum task dieksekusi.

        Ini dibuat atomic menggunakan Lock agar lebih aman
        jika nanti scheduler berjalan secara paralel.
        """

        with self._lock:
            if username not in self._users:
                raise KeyError(f"User not found: {username}")

            user = self._users[username]

            if user.executed >= user.quota:
                return False

            user.executed += 1
            return True

    def release(self, username: str) -> None:
        """
        Mengembalikan quota jika task gagal dieksekusi.
        """

        with self._lock:
            if username not in self._users:
                raise KeyError(f"User not found: {username}")

            user = self._users[username]

            if user.executed > 0:
                user.executed -= 1

    def reset_all(self) -> None:
        with self._lock:
            for user in self._users.values():
                user.executed = 0

        logger.info("All user quotas have been reset")

    def get_status(self, username: str) -> UserQuota:
        if username not in self._users:
            raise KeyError(f"User not found: {username}")

        return self._users[username]