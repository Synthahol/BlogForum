from app import app, db
from models import User

with app.app_context():
    # Use the reflection feature of SQLAlchemy to get the table structure
    user_table = db.inspect(User)
    columns = user_table.columns.keys()
    print(columns)
