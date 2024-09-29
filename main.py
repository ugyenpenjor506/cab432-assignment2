from app import app

if __name__ == '__main__':
    # SaveBodyWsgiApp()
    app.run(host='0.0.0.0', port=5005, debug=True)

# from app import app

# if __name__ == '__main__':
#     # Run the Flask app with SSL certificates for HTTPS
#     app.run(host='0.0.0.0', port=5005, debug=True, ssl_context=('cert.pem', 'key.pem'))

