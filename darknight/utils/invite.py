from urllib.parse import urlencode

from fastapi import Request


def build_invite_register_url(request: Request, code: str) -> str:
    origin = (request.headers.get("origin") or "").strip().rstrip("/")
    if not origin:
        referer = (request.headers.get("referer") or "").strip()
        if referer:
            from urllib.parse import urlparse

            parsed = urlparse(referer)
            if parsed.scheme and parsed.netloc:
                origin = f"{parsed.scheme}://{parsed.netloc}"
    if not origin:
        origin = str(request.base_url).rstrip("/")
        if origin.endswith("/api/v1"):
            origin = origin[: -len("/api/v1")]

    query = urlencode({"invite": code})
    # Dashboard 使用 hash 路由（#/portal/register），链接必须带 # 才能打开注册页。
    return f"{origin}/#/portal/register?{query}"
