import asyncio
import socket
from pathlib import Path
from typing import Any, AsyncGenerator

import docker
import httpx
import pytest
import pytest_asyncio
import requests
from core import settings
from docker import DockerClient
from pytest import Config
from pytest_docker.plugin import Services
from requests.exceptions import ConnectionError

CONTAINER_TIMEOUT = 90.0
PROJECT_NAME = "blogapi-integration-tests"


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


async def wait_for_service(url: str, timeout: int = 20) -> bool:
    async with httpx.AsyncClient() as client:
        for _ in range(timeout):
            try:
                resp = await client.get(url)
                if resp.status_code < 500:
                    return True
            except Exception:
                pass
            await asyncio.sleep(1)
    raise RuntimeError(f"Service at {url} did not become ready in {timeout}s")


def _check_tcp_connection(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        try:
            sock.connect((host, port))
        except OSError:
            return False
    return True


@pytest.fixture(scope="package")
def app_service(
    docker_ip: str,
    docker_services: Services,
) -> str:
    port = docker_services.port_for("app", 8000)
    url = f"http://{docker_ip}:{port}"
    url_ping = "{}{}{}/ping".format(
        url,
        settings.api.prefix,
        settings.api.admin.prefix,
    )
    docker_services.wait_until_responsive(
        timeout=CONTAINER_TIMEOUT, pause=1.0, check=lambda: is_responsive(url_ping)
    )
    return url


@pytest_asyncio.fixture(scope="package")
async def app_service_redis_inactive() -> AsyncGenerator[str, None]:
    client: DockerClient = docker.from_env()
    env = {
        "BLOGAPI__DB__URL": "postgresql+asyncpg://pgadmin:pgadmin@pg:5432/blog_app",
        "BLOGAPI__DB__LOGIN": "pgadmin",
        "BLOGAPI__DB__PASS": "pgadmin",
        "BLOGAPI__DB__SCHEMA": "blog_app",
        "BLOGAPI__DB__ECHO": "0",
        "BLOGAPI__DB__ECHO_POOL": "0",
        "BLOGAPI__CACHE__URL": "redis://:radmin@redis:6379",
        "BLOGAPI__CACHE__PASS": "radmin",
        "BLOGAPI__ES__URL": "http://elasticsearch:9200",
        # Redis inactivate
        "BLOGAPI__CACHE__RESP__INACTIVE": "true",
    }

    network_name = f"{PROJECT_NAME}_backend"
    image_name = f"{PROJECT_NAME}-app"

    container = client.containers.run(
        f"{image_name}:latest",
        name="app_without_redis",
        environment=env,
        detach=True,
        remove=True,
        network=network_name,
        ports={"8000/tcp": None},
    )

    container.reload()
    host_port = container.attrs["NetworkSettings"]["Ports"]["8000/tcp"][0]["HostPort"]
    url = f"http://localhost:{host_port}"
    await wait_for_service(f"{url}/admin/ping", int(CONTAINER_TIMEOUT))
    yield url
    container.stop()


@pytest.fixture(scope="package")
def pg_service(docker_ip: str, docker_services: Services) -> dict[str, Any]:
    port = docker_services.port_for("pg", 5432)
    docker_services.wait_until_responsive(
        timeout=CONTAINER_TIMEOUT,
        pause=1.0,
        check=lambda: _check_tcp_connection(docker_ip, port),
    )
    return {"host": docker_ip, "port": port}


@pytest.fixture(scope="package")
def redis_service(docker_ip: str, docker_services: Services) -> dict[str, Any]:
    port = docker_services.port_for("redis", 6379)
    docker_services.wait_until_responsive(
        timeout=CONTAINER_TIMEOUT,
        pause=1.0,
        check=lambda: _check_tcp_connection(docker_ip, port),
    )
    return {"host": docker_ip, "port": port}


@pytest.fixture(scope="package")
def elasticsearch_service(docker_ip: str, docker_services: Services) -> str:
    port = docker_services.port_for("elasticsearch", 9200)
    url = f"http://{docker_ip}:{port}"
    docker_services.wait_until_responsive(
        timeout=CONTAINER_TIMEOUT,
        pause=1.0,
        check=lambda: is_responsive(url),
    )
    return url


@pytest.fixture(scope="session")
def docker_compose_project_name() -> str:
    return PROJECT_NAME


@pytest.fixture(scope="session")
def docker_setup() -> list[str]:
    return ["down -v", "up --build -d"]
