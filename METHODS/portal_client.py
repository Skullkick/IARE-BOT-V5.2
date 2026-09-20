"""
Async HTTP client and caching layer for interacting with the Samvidha portal.

Replaces blocking synchronous `requests` calls with non-blocking `httpx.AsyncClient`.
Provides in-memory TTL caching for attendance and other high-frequency portal pages
to minimize redundant requests to Samvidha and keep bot response times under 100ms.
"""

import logging
import re
from typing import Optional, Dict, Any
import httpx
from bs4 import BeautifulSoup
from cachetools import TTLCache

logger = logging.getLogger(__name__)

# Common portal headers
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://samvidha.iare.ac.in',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Referer': 'https://samvidha.iare.ac.in/index',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}

DEFAULT_TIMEOUT = httpx.Timeout(15.0, connect=8.0)

_SHARED_CLIENT: Optional[httpx.AsyncClient] = None

def get_http_client() -> httpx.AsyncClient:
    """Return a shared singleton httpx.AsyncClient instance."""
    global _SHARED_CLIENT
    if _SHARED_CLIENT is None or _SHARED_CLIENT.is_closed:
        _SHARED_CLIENT = httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, follow_redirects=True)
    return _SHARED_CLIENT

async def close_http_client():
    """Close the shared httpx.AsyncClient if open."""
    global _SHARED_CLIENT
    if _SHARED_CLIENT is not None and not _SHARED_CLIENT.is_closed:
        await _SHARED_CLIENT.aclose()
        _SHARED_CLIENT = None

# In-memory TTL cache: max 2000 entries, cached for 3 minutes (180s)
# Prevents duplicate requests when users toggle between Attendance and Bunk
_PORTAL_CACHE: TTLCache = TTLCache(maxsize=2000, ttl=180)

def invalidate_user_cache(chat_id: int):
    """Evict all cached entries for a given user chat_id."""
    keys_to_remove = [k for k in _PORTAL_CACHE.keys() if k[0] == chat_id]
    for k in keys_to_remove:
        _PORTAL_CACHE.pop(k, None)

def get_soup(html_text: str) -> BeautifulSoup:
    """Parse HTML using lxml if available for fast parsing, fallback to html.parser."""
    try:
        return BeautifulSoup(html_text, 'lxml')
    except Exception:
        return BeautifulSoup(html_text, 'html.parser')

async def perform_async_login(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Log in to Samvidha using non-blocking httpx and return session payload.

    Args:
        username: Roll number / user ID.
        password: Plaintext password.

    Returns:
        dict with cookies and headers if login succeeds, else None.
    """
    index_url = "https://samvidha.iare.ac.in/index"
    login_url = "https://samvidha.iare.ac.in/pages/login/checkUser.php"
    home_url = "https://samvidha.iare.ac.in/home"

    headers = dict(DEFAULT_HEADERS)
    data = {'username': username, 'password': password}

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, follow_redirects=True) as client:
        try:
            resp = await client.get(index_url, headers=headers)

            # Extract CSRF token if present
            csrf_match = re.search(
                r'<meta\s+[^>]*name=["\']csrf-token["\'][^>]*content=["\']([^"\']+)["\']',
                resp.text,
                re.IGNORECASE
            ) or re.search(
                r'<meta\s+[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']csrf-token["\']',
                resp.text,
                re.IGNORECASE
            )
            if csrf_match:
                headers['X-CSRF-Token'] = csrf_match.group(1)

            # Post credentials
            await client.post(login_url, headers=headers, data=data)

            # Verify home page
            home_resp = await client.get(home_url, headers=headers)
            if '<title>IARE - Dashboard - Student</title>' in home_resp.text:
                cookie_dict = {k: v for k, v in client.cookies.items()}
                return {
                    'cookies': cookie_dict,
                    'headers': headers,
                    'username': username
                }
            return None
        except Exception as e:
            logger.error("Async login network error for user %s: %s", username, e)
            return None

async def async_fetch_page(url: str, cookies: dict, chat_id: Optional[int] = None, cache_action: Optional[str] = None) -> Optional[str]:
    """Fetch an authenticated page asynchronously with optional TTL caching.

    Args:
        url: Portal URL to fetch.
        cookies: User's session cookies.
        chat_id: Telegram chat ID for cache scoping.
        cache_action: Cache identifier (e.g. 'attendance', 'biometric').

    Returns:
        HTML text of the page or None on failure.
    """
    if chat_id is not None and cache_action:
        cache_key = (chat_id, cache_action)
        if cache_key in _PORTAL_CACHE:
            return _PORTAL_CACHE[cache_key]

    async with httpx.AsyncClient(cookies=cookies, timeout=DEFAULT_TIMEOUT, follow_redirects=True) as client:
        try:
            response = await client.get(url, headers=DEFAULT_HEADERS)
            html = response.text
            if chat_id is not None and cache_action and response.status_code == 200:
                _PORTAL_CACHE[(chat_id, cache_action)] = html
            return html
        except Exception as e:
            logger.error("Async fetch failed for url %s: %s", url, e)
            return None

async def async_logout_portal(cookies: dict):
    """Notify the portal of logout asynchronously."""
    logout_url = 'https://samvidha.iare.ac.in/logout'
    try:
        async with httpx.AsyncClient(cookies=cookies, timeout=httpx.Timeout(5.0)) as client:
            await client.get(logout_url, headers=DEFAULT_HEADERS)
    except Exception as e:
        logger.debug("Silent logout request error: %s", e)
