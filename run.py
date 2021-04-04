from flaskapp.app import app, create_routes

if __name__ == "__main__":
    create_routes()
    app.run(host="0.0.0.0", debug=True)