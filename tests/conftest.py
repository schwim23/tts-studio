"""Shared pytest fixtures and the --run-network gate."""

from __future__ import annotations

import pytest

from tests.fixtures.generate import (
    SAMPLE_PARAGRAPHS,
    SAMPLE_TITLE,
    build_fixtures,
)


def pytest_addoption(parser):
    parser.addoption(
        "--run-network",
        action="store_true",
        default=False,
        help="Run tests that hit live TTS / web endpoints.",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-network"):
        return
    skip = pytest.mark.skip(reason="needs --run-network")
    for item in items:
        if "network" in item.keywords:
            item.add_marker(skip)


@pytest.fixture(scope="session")
def fixtures(tmp_path_factory):
    """Generate sample .txt/.md/.pdf/.docx and return {kind: path}."""
    dest = tmp_path_factory.mktemp("fixtures")
    return build_fixtures(dest)


@pytest.fixture(scope="session")
def sample_title():
    return SAMPLE_TITLE


@pytest.fixture(scope="session")
def sample_paragraphs():
    return SAMPLE_PARAGRAPHS
