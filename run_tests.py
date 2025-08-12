#!/usr/bin/env python3
"""
быстрый прогон тестов 
"""

import subprocess
import sys
import time
import os



def print_config(cmd, is_fast_mode):
    """вывод конфигурации"""
    print(f"режим: {'быстрый' if is_fast_mode else 'полный'}")

def print_summary(returncode, duration, test_file):
    """итог"""
    status = "УСПЕХ" if returncode == 0 else "ОШИБКИ"
    print(f"статус: {status}, время: {duration:.2f} сек")

def run_tests_fast():
    """запуск тестов с максимальной скоростью"""
    
    print("тесты")
    
    # команды для ускорения
    cmd = [
        "python", "-m", "pytest",
        "-n", "auto",  # параллелизация
        "--tb=short",  # короткий traceback
        "--disable-warnings",  # отключить предупреждения
        "--maxfail=5",  # остановиться после 5 ошибок
        "--cache-clear",  # очистить кэш
        "-v"  # verbose
    ]
    
    # определить файл тестов
    test_file = "test_favorites.py"
    if len(sys.argv) > 1:
        # фильтруем аргументы, исключая --fast
        test_args = [arg for arg in sys.argv[1:] if arg != "--fast"]
        if test_args:
            cmd.extend(test_args)
            test_file = test_args[0]
    else:
        cmd.append(test_file)
    
    # опция для быстрых тестов
    is_fast_mode = "--fast" in sys.argv
    if is_fast_mode:
        cmd.extend(["-m", "not slow"])
    
    print_config(cmd, is_fast_mode)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, check=False)
        end_time = time.time()
        
        duration = end_time - start_time
        print_summary(result.returncode, duration, test_file)
        
        return result.returncode
        
    except KeyboardInterrupt:
        print("тесты прерваны")
        return 1
    except Exception as e:
        print(f"ошибка запуска: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests_fast())
