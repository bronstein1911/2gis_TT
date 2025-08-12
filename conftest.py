import pytest
import requests
import time


@pytest.fixture(scope="session")
def base_url() -> str:
    return "https://regions-test.2gis.com"


@pytest.fixture(scope="session")
def session() -> requests.Session:
    """сессия с оптимизациями для быстрых запросов"""
    session = requests.Session()
    
    # настройки для ускорения
    session.headers.update({
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'pytest-test-runner/1.0'
    })
    
    # адаптер с пулом соединений
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=10,
        pool_maxsize=20,
        max_retries=1
    )
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    return session


@pytest.fixture(scope="session")
def auth_token(session: requests.Session, base_url: str) -> str:
    """
    получение токена один раз на всю сессию
    токен живет 2 секунды, но для большинства тестов этого достаточно
    """
    response = session.post(f"{base_url}/v1/auth/tokens")
    assert response.status_code == 200, f"не удалось получить токен: {response.status_code}"
    
    token = response.cookies.get("token")
    assert token, "токен не найден в cookie"
    
    return token


@pytest.fixture(scope="session")
def auth_headers(auth_token: str) -> dict:
    """заголовки с токеном для аутентификации"""
    return {"Cookie": f"token={auth_token}"}


@pytest.fixture(scope="session")
def expired_token(session: requests.Session, base_url: str) -> str:
    """
    получение заведомо истекшего токена
    токен живет 2 секунды, ждём чуть больше и возвращаем его
    """
    response = session.post(f"{base_url}/v1/auth/tokens")
    token = response.cookies.get("token")
    assert token, "токен не найден в cookie"
    time.sleep(2.1)
    return token


@pytest.fixture(scope="session")
def valid_coordinates() -> dict:
    """валидные координаты для тестов"""
    return {
        "lat": 55.028254,
        "lon": 82.918501
    }


@pytest.fixture(scope="session")
def valid_title() -> str:
    """валидный title для тестов"""
    return "тестовое место"


@pytest.fixture(scope="session")
def valid_favorite_data(valid_title: str, valid_coordinates: dict) -> dict:
    """валидные данные для создания избранного места"""
    return {
        "title": valid_title,
        **valid_coordinates
    }


@pytest.fixture(scope="session")
def long_title() -> str:
    """title длиной 999 символов"""
    return "a" * 999


@pytest.fixture(scope="session")
def invalid_payloads() -> list:
    """невалидные данные для негативных тестов"""
    return [
        {"title": "", "lat": 55.028254, "lon": 82.918501},
        {"lat": 55.028254, "lon": 82.918501},  # missing title
        {"title": "a" * 1000, "lat": 55.028254, "lon": 82.918501},
        {"title": "ok", "lat": 91.0, "lon": 82.0},
        {"title": "ok", "lat": -91.0, "lon": 82.0},
        {"title": "ok", "lat": 55.0, "lon": 181.0},
        {"title": "ok", "lat": 55.0, "lon": -181.0},
        {"title": "ok", "lat": "abc", "lon": "xyz"},
        {"title": "ok", "lat": 55.0},  # missing lon
        {"title": "ok", "lon": 82.0},  # missing lat
    ]



