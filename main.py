import os
from app import create_app, db

# Initialize Flask app and secret key for JWT
app = create_app()

if __name__ == "__main__":
    with app.app_context():
           db.create_all()
           print("Database tables created.")
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))