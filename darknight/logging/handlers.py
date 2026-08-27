"""File handlers for DarKnight's structured logs."""

from __future__ import annotations

from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import re

_DATED_SUFFIX = re.compile(r"\.(\d{4}-\d{2}-\d{2})$")


class DailyJsonlHandler(TimedRotatingFileHandler):
    """按本地日期跨零点轮转，历史文件命名为 ``<stem>-YYYY-MM-DD<ext>``。

    stdlib 默认把轮转后的文件叫 ``<baseFilename>.YYYY-MM-DD``，扩展名被埋在中间，
    编辑器和 jq 都不再当它是 jsonl。而一旦用 namer 改名，stdlib 的 getFilesToDelete
    就认不出历史文件了（它只按 ``<baseFilename>.`` 前缀匹配），backupCount 会静默
    失效、旧文件永远不删，所以清理逻辑必须一并重写。
    """

    def __init__(self, path: Path, backup_count: int) -> None:
        self._stem = path.stem
        self._ext = path.suffix
        super().__init__(
            filename=str(path),
            when="midnight",
            interval=1,
            backupCount=backup_count,
            encoding="utf-8",
            utc=False,
        )
        self.suffix = "%Y-%m-%d"
        self.namer = self._dated_name

    def _dated_name(self, default_name: str) -> str:
        path = Path(default_name)
        match = _DATED_SUFFIX.search(path.name)
        if match is None:
            return default_name
        return str(path.with_name(f"{self._stem}-{match.group(1)}{self._ext}"))

    def getFilesToDelete(self) -> list[str]:  # noqa: N802 - stdlib hook
        pattern = re.compile(
            rf"^{re.escape(self._stem)}-\d{{4}}-\d{{2}}-\d{{2}}{re.escape(self._ext)}$"
        )
        directory = Path(self.baseFilename).parent
        dated = sorted(
            path
            for path in directory.glob(f"{self._stem}-*{self._ext}")
            if pattern.match(path.name)
        )
        surplus = len(dated) - self.backupCount
        return [str(path) for path in dated[:surplus]] if surplus > 0 else []


__all__ = ["DailyJsonlHandler"]
