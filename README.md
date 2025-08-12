# тесты api favorites

### test_favorites.py
основные тесты для api избранных мест:
- **TestAuth** - аутентификация (получение токена, проверка истечения)
- **TestCreateFavoritePositive** - позитивные тесты
- **TestCreateFavoriteNegative** - негативные тесты

### conftest.py  
фикстуры pytest:
- `base_url` - базовый url api
- `session` - оптимизированная http сессия с пулом соединений
- `auth_token/auth_headers` - токен и заголовки для авторизации
- `expired_token` - истекший токен для негативных тестов
- `valid_` - валидные данные для тестов
- `invalid_payloads` - невалидные данные для проверки валидации

### run_tests.py
скрипт для быстрого запуска тестов:
- параллелизация (`-n auto`)
- короткий вывод ошибок
- отключение предупреждений
- остановка после 5 ошибок
- поддержка `--fast` режима

## запуск
```bash
python run_tests.py
python run_tests.py --fast  # только быстрые тесты
```
