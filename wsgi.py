from app import wsgi_app


if __name__ == "__main__":
    import sys
    import app
    if len(sys.argv) < 2:
        print('\n\nВНИМАНИЕ!Укажите имя сервера\n\n')
    app.server_name = 'test.lava-land.ru'
    wsgi_app.run(host='127.0.0.1', port=3456, debug=True)
