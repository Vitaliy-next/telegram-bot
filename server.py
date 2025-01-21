from waitress import serve
from bot0125 import app  # Импорт вашего основного приложения Flask

if __name__ == "__main__":
    # Запуск приложения с помощью waitress
    serve(app, host='0.0.0.0', port=8080)