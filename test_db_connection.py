from sqlalchemy import create_engine

DATABASE_URI = "postgresql://blogforum_user:bjeFv7tdR85Sp548mhpwjjeK5sHCypVT@dpg-cq9ltedds78s739fi3fg-a.ohio-postgres.render.com:5432/blogforum"
print(f"Connecting to database: {DATABASE_URI}")

try:
    engine = create_engine(DATABASE_URI)
    connection = engine.connect()
    print("Connection to the database was successful.")
    connection.close()
except Exception as e:
    print(f"Error connecting to the database: {e}")
