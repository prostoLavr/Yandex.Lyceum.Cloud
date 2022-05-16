from app import app


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] in ('--test', 'test', '-t'):
        app.run(host='0.0.0.0', port=3456, debug=True)
    else:
        app.run(host='127.0.0.1', port=80)
