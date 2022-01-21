# imported from __init__ in the application folder/package
from application import app, api
from application.models import db


if __name__ == "__main__":
    api.init_app(app)
    db.create_all()
    app.run(debug=True, port=5000)
