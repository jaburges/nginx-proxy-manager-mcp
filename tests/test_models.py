"""Tests for Pydantic models."""

import pytest

from npm_mcp.models import Certificate, ProxyHost, ProxyHostSummary

PROXY_HOST_BASE = {
    "id": 1,
    "created_on": "2024-01-01T00:00:00Z",
    "modified_on": "2024-01-01T00:00:00Z",
    "owner_user_id": 1,
    "forward_host": "192.168.1.100",
    "forward_port": 8080,
}

SUMMARY_BASE = {
    "id": 1,
    "forward_host": "192.168.1.100",
    "forward_port": 8080,
    "forward_scheme": "http",
    "enabled": True,
    "ssl_forced": False,
}


def build(model, domain_names):
    if model is Certificate:
        return Certificate(domain_names=domain_names)
    if model is ProxyHost:
        return ProxyHost(**PROXY_HOST_BASE, domain_names=domain_names)
    return ProxyHostSummary(**SUMMARY_BASE, domain_names=domain_names)


MODELS = [Certificate, ProxyHost, ProxyHostSummary]


@pytest.mark.parametrize("model", MODELS)
def test_domain_names_drops_null_entries(model):
    assert build(model, [None, "example.com", None]).domain_names == ["example.com"]


@pytest.mark.parametrize("model", MODELS)
def test_domain_names_null_list(model):
    assert build(model, None).domain_names == []


@pytest.mark.parametrize("model", MODELS)
def test_domain_names_drops_empty_strings(model):
    assert build(model, ["", "example.com", ""]).domain_names == ["example.com"]


def test_certificate_domain_names_default():
    assert Certificate().domain_names == []


def test_proxy_host_with_nested_certificate_null_domain_names():
    host = ProxyHost.model_validate(
        {
            **PROXY_HOST_BASE,
            "domain_names": ["example.com"],
            "certificate_id": 5,
            "certificate": {
                "id": 5,
                "provider": "letsencrypt",
                "nice_name": "example.com",
                "domain_names": [None],
            },
        }
    )
    assert host.domain_names == ["example.com"]
    assert host.certificate is not None
    assert host.certificate.domain_names == []
