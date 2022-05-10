from app import app
from waitress import serve


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] in ('--test', 'test', '-t'):
        app.run(host='0.0.0.0', port=3456, debug=True)
    else:
        serve(app, host='0.0.0.0', port=5000, max_request_body_size=(1073741824 * 10))
