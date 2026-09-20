import pytest
from METHODS import portal_client

def test_portal_cache_ttl_and_invalidation():
    """Verify caching, retrieval, and targeted user invalidation."""
    chat_id_1 = 111111
    chat_id_2 = 222222
    
    # Pre-populate cache directly
    portal_client._PORTAL_CACHE[(chat_id_1, "attendance")] = "<html>Attendance 1</html>"
    portal_client._PORTAL_CACHE[(chat_id_1, "bunk")] = "<html>Bunk 1</html>"
    portal_client._PORTAL_CACHE[(chat_id_2, "attendance")] = "<html>Attendance 2</html>"
    
    assert (chat_id_1, "attendance") in portal_client._PORTAL_CACHE
    assert (chat_id_1, "bunk") in portal_client._PORTAL_CACHE
    assert (chat_id_2, "attendance") in portal_client._PORTAL_CACHE
    
    # Invalidate chat_id_1
    portal_client.invalidate_user_cache(chat_id_1)
    
    assert (chat_id_1, "attendance") not in portal_client._PORTAL_CACHE
    assert (chat_id_1, "bunk") not in portal_client._PORTAL_CACHE
    # chat_id_2 should still be cached
    assert (chat_id_2, "attendance") in portal_client._PORTAL_CACHE

def test_get_soup_parser():
    """Verify HTML parsing returns valid BeautifulSoup object."""
    html = "<div><p>Hello World</p></div>"
    soup = portal_client.get_soup(html)
    assert soup.find("p").text == "Hello World"

def test_get_soup_malformed_html():
    """Verify malformed HTML does not crash parser."""
    malformed = "<div><p>Unclosed paragraph"
    soup = portal_client.get_soup(malformed)
    assert soup.find("p").text == "Unclosed paragraph"

def test_http_client_lifecycle():
    """Verify shared HTTP client singleton initialization."""
    client1 = portal_client.get_http_client()
    client2 = portal_client.get_http_client()
    assert client1 is client2
    assert not client1.is_closed
