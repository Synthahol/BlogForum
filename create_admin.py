from werkzeug.security import generate_password_hash

from app import app, db
from models import User

with app.app_context():
    # check if the admin user already exists
    admin = User.query.filter_by(username="admin").first()
    if admin is None:
        # Create the admin user if it does not exist
        admin = User(
            username="admin",
            email="admin@example.com",
            password=generate_password_hash("adminpassword"),
            role="admin",
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
    else:
        print("Admin user already exists!")
