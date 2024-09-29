from app import app

if __name__ == '__main__':
    # SaveBodyWsgiApp()
    app.run(host='0.0.0.0', port=5005, debug=True)
