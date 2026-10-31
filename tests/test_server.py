"""Tests for the server module and its FastMCP initialization."""

from npm_mcp import server
from npm_mcp.models import Certificate, ProxyHost


def test_server_imports():
    """Ensure that the server and mcp instance can be imported without errors."""
    from npm_mcp.server import mcp

    assert mcp is not None
    assert mcp.name == "npm-mcp"


def test_server_http_app():
    """Ensure that the http_app can be retrieved without AttributeError."""
    from npm_mcp.server import mcp

    app = mcp.http_app()
    assert app is not None


class _FakeClient:
    def __init__(self, hosts=None, certs=None):
        self._hosts = hosts or []
        self._certs = certs or []

    async def get_proxy_hosts(self):
        return self._hosts

    async def get_certificates(self):
        return self._certs


def _patch_client(monkeypatch, client):
    monkeypatch.setattr(server, "_resolve", lambda instance: (client, None))


async def test_list_proxy_hosts_with_null_domain_names(monkeypatch):
    host = ProxyHost(
        id=1,
        created_on="2024-01-01T00:00:00Z",
        modified_on="2024-01-01T00:00:00Z",
        owner_user_id=1,
        forward_host="192.168.1.100",
        forward_port=8080,
        domain_names=[None, "example.com", None],
    )
    _patch_client(monkeypatch, _FakeClient(hosts=[host]))

    result = await server.list_proxy_hosts()

    assert "Error" not in result
    assert "[1] example.com" in result


async def test_list_certificates_with_null_domain_names(monkeypatch):
    certs = [
        Certificate(id=1, nice_name="a", provider="letsencrypt", domain_names=[None]),
        Certificate(id=2, nice_name="b", provider="other", domain_names=None),
        Certificate(id=3, nice_name="c", provider="letsencrypt", domain_names=["x.com", None]),
    ]
    _patch_client(monkeypatch, _FakeClient(certs=certs))

    result = await server.list_certificates()

    assert "Error" not in result
    assert "Found 3 certificate(s)" in result
    assert "Domains: x.com" in result
