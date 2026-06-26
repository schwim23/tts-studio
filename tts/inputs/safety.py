"""
SSRF guard for user-supplied URLs.

Once the app is public, the URL box lets anyone make the server fetch arbitrary
URLs. Without a guard that includes internal services and the cloud metadata
endpoint (169.254.169.254). This blocks non-http(s) schemes and any host that
resolves to a private / loopback / link-local / reserved address.
"""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


class UnsafeURLError(ValueError):
    pass


def _ip_is_blocked(ip: str) -> bool:
    addr = ipaddress.ip_address(ip)
    return (
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_reserved
        or addr.is_multicast
        or addr.is_unspecified
    )


def assert_safe_url(url: str) -> None:
    """Raise UnsafeURLError if the URL is not safe to fetch server-side."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise UnsafeURLError(f"Only http(s) URLs are allowed (got '{parsed.scheme}').")
    host = parsed.hostname
    if not host:
        raise UnsafeURLError("URL has no host.")

    try:
        infos = socket.getaddrinfo(host, parsed.port or 80, proto=socket.IPPROTO_TCP)
    except socket.gaierror as e:
        raise UnsafeURLError(f"Could not resolve host '{host}'.") from e

    for info in infos:
        ip = info[4][0]
        if _ip_is_blocked(ip):
            raise UnsafeURLError(
                f"Host '{host}' resolves to a non-public address ({ip}) and is blocked."
            )


def is_safe_url(url: str) -> bool:
    try:
        assert_safe_url(url)
        return True
    except UnsafeURLError:
        return False
