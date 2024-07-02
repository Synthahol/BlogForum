from werkzeug.security import generate_password_hash

from app import app, db
from models import User

with app.app_context():
    # check if the admin user already exists
    if not User.query.filter_by(username="admin").first():
        # Create the admin user if it does not exist
        admin = User(
            username="admin",
            email="85cawill@gmail.com",
            password=generate_password_hash("adminpassword", method="sha256"),
            role="admin",
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
    else:
        print("Admin user already exists!")
