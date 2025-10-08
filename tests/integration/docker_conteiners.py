import socket
from pathlib import Path
from typing import Any

import pytest
import requests
from core import settings
from pytest import Config
from pytest_docker.plugin import Services
from requests.exceptions import ConnectionError


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig: Config) -> Path:
    doc_comp = pytestconfig.rootpath / "docker-compose.yml"
    return doc_comp


def is_responsive(url: str) -> bool:
    try:
        response = requests.get(url, timeout=1)
        return response.status_code == 200
    except ConnectionError:
        return False


def _check_tcp_connection(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        try:
            sock.connect((host, port))
        except OSError:
            return False
    return True


@pytest.fixture(scope="package")
def app_service(docker_ip: str, docker_services: Services) -> str:
    port = docker_services.port_for("app", 8000)
    url = f"http://{docker_ip}:{port}"
    url_ping = "{}{}{}/ping".format(
        url,
        settings.api.prefix,
        settings.api.admin.prefix,
    )
    docker_services.wait_until_responsive(
        timeout=60.0, pause=1.0, check=lambda: is_responsive(url_ping)
    )
    return url


@pytest.fixture(scope="package")
def pg_service(docker_ip: str, docker_services: Services) -> dict[str, Any]:
    port = docker_services.port_for("pg", 5432)
    docker_services.wait_until_responsive(
        timeout=60.0,
        pause=1.0,
        check=lambda: _check_tcp_connection(docker_ip, port),
    )
    return {"host": docker_ip, "port": port}


@pytest.fixture(scope="package")
def redis_service(docker_ip: str, docker_services: Services) -> dict[str, Any]:
    port = docker_services.port_for("redis", 6379)
    docker_services.wait_until_responsive(
        timeout=60.0,
        pause=1.0,
        check=lambda: _check_tcp_connection(docker_ip, port),
    )
    return {"host": docker_ip, "port": port}


@pytest.fixture(scope="package")
def elasticsearch_service(docker_ip: str, docker_services: Services) -> str:
    port = docker_services.port_for("elasticsearch", 9200)
    url = f"http://{docker_ip}:{port}"
    docker_services.wait_until_responsive(
        timeout=90.0,
        pause=1.0,
        check=lambda: is_responsive(url),
    )
    return url


@pytest.fixture(scope="session")
def docker_compose_project_name() -> str:
    return "blogapi-integration-tests"


@pytest.fixture(scope="session")
def docker_setup() -> list[str]:
    return ["down -v", "up --build -d"]
