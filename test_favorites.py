import pytest
import requests
import time
from datetime import datetime


class TestAuth:
    """тесты аутентификации"""
    
    def test_get_token(self, session: requests.Session, base_url: str):
        """получение валидного токена"""
        response = session.post(f"{base_url}/v1/auth/tokens")
        
        assert response.status_code == 200
        assert response.cookies.get("token")
    
    def test_token_expires(self, session: requests.Session, base_url: str):
        """токен истекает через 2000мс"""
        # получаем токен
        response = session.post(f"{base_url}/v1/auth/tokens")
        assert response.status_code == 200
        token = response.cookies.get("token")
        assert token
        
        # ждём 3 секунды (чуть больше 2000мс)
        time.sleep(3)
        
        # пробуем использовать истекший токен
        headers = {"Cookie": f"token={token}"}
        data = {"title": "test", "lat": 55.0, "lon": 82.0}
        
        response = session.post(
            f"{base_url}/v1/favorites",
            data=data,
            headers=headers
        )
        
        assert response.status_code in [401, 403]


class TestCreateFavoritePositive:
    """позитивные тесты создания избранного места"""
    
    def test_create_minimal(self, session: requests.Session, base_url: str, 
                                        auth_headers: dict, valid_favorite_data: dict):
        """создание места с минимальными данными"""
        response = session.post(
            f"{base_url}/v1/favorites",
            data=valid_favorite_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # проверяем структуру ответа
        assert "id" in data
        assert "title" in data
        assert "lat" in data
        assert "lon" in data
        assert "color" in data
        assert "created_at" in data
        
        # проверяем значения
        assert data["title"] == valid_favorite_data["title"]
        assert data["lat"] == valid_favorite_data["lat"]
        assert data["lon"] == valid_favorite_data["lon"]
        assert data["color"] is None
        
        # проверяем типы данных
        assert isinstance(data["id"], int)
        assert isinstance(data["title"], str)
        assert isinstance(data["lat"], float)
        assert isinstance(data["lon"], float)
        assert isinstance(data["created_at"], str)
    
    @pytest.mark.parametrize("color", ["BLUE", "GREEN", "RED", "YELLOW"])
    def test_create_with_colors(self, session: requests.Session, base_url: str,
                                       auth_headers: dict, valid_favorite_data: dict, color: str):
        """создание места с разными цветами"""
        data = {**valid_favorite_data, "color": color}
        
        response = session.post(
            f"{base_url}/v1/favorites",
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["color"] == color

    def test_create_long_title(self, session: requests.Session, base_url: str,
                                           auth_headers: dict, valid_coordinates: dict, long_title: str):
        """title с 999 символов"""
        data = {"title": long_title, **valid_coordinates}
        response = session.post(
            f"{base_url}/v1/favorites",
            data=data,
            headers=auth_headers
        )
        assert response.status_code == 200
        body = response.json()
        assert body["title"] == long_title
        assert len(body["title"]) == 999

    def test_coords_rounding(self, session: requests.Session, base_url: str,
                                 auth_headers: dict, valid_title: str):
        """проверка округления координат до 6 знаков"""
        data = {"title": valid_title, "lat": 55.123456789, "lon": 82.987654321}
        response = session.post(f"{base_url}/v1/favorites", data=data, headers=auth_headers)
        
        body = response.json()
        assert body["lat"] == 55.123457
        assert body["lon"] == 82.987654

    def test_id_increment(self, session: requests.Session, base_url: str,
                        auth_headers: dict, valid_favorite_data: dict):
        """проверка монотонности id"""
        response1 = session.post(f"{base_url}/v1/favorites", data=valid_favorite_data, headers=auth_headers)
        response2 = session.post(f"{base_url}/v1/favorites", data=valid_favorite_data, headers=auth_headers)
        
        id1 = response1.json()["id"]
        id2 = response2.json()["id"]
        assert id2 > id1

    def test_created_at_iso(self, session: requests.Session, base_url: str,
                              auth_headers: dict, valid_favorite_data: dict):
        """проверка формата created_at (ISO 8601)"""
        response = session.post(f"{base_url}/v1/favorites", data=valid_favorite_data, headers=auth_headers)
        created_at = response.json()["created_at"]
        
        datetime.fromisoformat(created_at.replace('Z', '+00:00'))


class TestCreateFavoriteNegative:
    """негативные тесты"""
    
    @pytest.mark.parametrize("token_headers", [
        pytest.param(lambda t: {"Cookie": f"token={t}"}, id="expired"),
        pytest.param(lambda _t: {}, id="absent"),
    ])
    def test_auth_required(self, session: requests.Session, base_url: str,
                                     expired_token: str, valid_favorite_data: dict,
                                     token_headers):
        """ошибка при отсутствии или истекшем токене"""
        headers = token_headers(expired_token)
        response = session.post(
            f"{base_url}/v1/favorites",
            data=valid_favorite_data,
            headers=headers
        )
        assert response.status_code in [401, 403]
    
    def test_validation_errors(self, session: requests.Session, base_url: str,
                                               auth_headers: dict, invalid_payloads: list):
        """валидация входных данных: title/coords"""
        for payload in invalid_payloads:
            response = session.post(
                f"{base_url}/v1/favorites",
                data=payload,
                headers=auth_headers
            )
            assert response.status_code in [400, 422]
            
            # проверяем структуру ошибки если есть
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    assert "error" in error_data or "message" in error_data
                except ValueError:
                    pass  # не json ответ
        
    
