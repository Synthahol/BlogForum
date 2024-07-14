import sqlite3

import psycopg2
from psycopg2 import sql


def sqlite_to_postgres(sqlite_db_path, postgres_conn_string):
    print("Starting the migration process...")
    # Connect to SQLite database
    try:
        sqlite_con = sqlite3.connect(sqlite_db_path)
        sqlite_cur = sqlite_con.cursor()
        print("Connected to SQLite database.")
    except sqlite3.Error as e:
        print(f"Error connecting to SQLite: {e}")
        return

    # Connect to PostgreSQL database
    try:
        postgres_con = psycopg2.connect(postgres_conn_string)
        postgres_cur = postgres_con.cursor()
        print("Connected to PostgreSQL database.")
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return

    # Fetch all tables from SQLite
    try:
        tables = sqlite_cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()
        print(f"Found tables: {tables}")
    except sqlite3.Error as e:
        print(f"Error fetching tables from SQLite: {e}")
        return

    for table_name in tables:
        table_name = table_name[0]
        print(f"Migrating table: {table_name}")

        # Fetch all data from SQLite table
        try:
            sqlite_cur.execute(f"SELECT * FROM {table_name}")
            rows = sqlite_cur.fetchall()
            print(f"Fetched {len(rows)} rows from {table_name}")
        except sqlite3.Error as e:
            print(f"Error fetching data from SQLite table {table_name}: {e}")
            continue

        # Fetch column names and types from SQLite table
        try:
            sqlite_cur.execute(f"PRAGMA table_info({table_name})")
            columns_info = sqlite_cur.fetchall()
            columns = [col[1] for col in columns_info]

            # Adjust column types
            column_definitions = []
            for col in columns_info:
                col_name = col[1]
                col_type = col[2]
                if col_type.upper() == "DATETIME":
                    col_type = "TIMESTAMP"
                if col_name == "password":
                    col_type = "VARCHAR(255)"  # Adjusting length for password column
                column_definitions.append(f"{col_name} {col_type}")

            column_definitions = ", ".join(column_definitions)
            print(f"Columns for {table_name}: {columns}")
        except sqlite3.Error as e:
            print(f"Error fetching column info from SQLite table {table_name}: {e}")
            continue

        # Create table in PostgreSQL
        try:
            if table_name.lower() == "user":
                create_table_query = f'CREATE TABLE "user" ({column_definitions});'
            else:
                create_table_query = (
                    f"CREATE TABLE {table_name} ({column_definitions});"
                )
            postgres_cur.execute(create_table_query)
            print(f"Created table {table_name} in PostgreSQL")
        except psycopg2.Error as e:
            print(f"Error creating PostgreSQL table {table_name}: {e}")
            postgres_con.rollback()
            continue

        # Insert data into PostgreSQL table
        try:
            insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier(table_name if table_name.lower() != "user" else "user"),
                sql.SQL(", ").join(map(sql.Identifier, columns)),
                sql.SQL(", ").join(sql.Placeholder() * len(columns)),
            )
            for row in rows:
                try:
                    postgres_cur.execute(insert_query, row)
                except psycopg2.Error as e:
                    print(
                        f"Error inserting row into PostgreSQL table {table_name}: {e}"
                    )
                    print(f"Row data: {row}")
                    postgres_con.rollback()
            print(f"Inserted data into {table_name}")
        except psycopg2.Error as e:
            print(f"Error inserting data into PostgreSQL table {table_name}: {e}")
            postgres_con.rollback()
            continue

        # Migrate indices
        try:
            indices = sqlite_cur.execute(f"PRAGMA index_list({table_name})").fetchall()
            for index in indices:
                index_name = index[1]
                index_info = sqlite_cur.execute(
                    f"PRAGMA index_info({index_name})"
                ).fetchall()
                index_columns = [col[2] for col in index_info]
                index_columns_str = ", ".join(index_columns)
                create_index_query = sql.SQL("CREATE INDEX {} ON {} ({})").format(
                    sql.Identifier(index_name),
                    sql.Identifier(
                        table_name if table_name.lower() != "user" else "user"
                    ),
                    sql.SQL(index_columns_str),
                )
                postgres_cur.execute(create_index_query)
                print(f"Created index {index_name} on {table_name}")
        except sqlite3.Error as e:
            print(f"Error fetching indices from SQLite table {table_name}: {e}")
        except psycopg2.Error as e:
            print(f"Error creating PostgreSQL index on table {table_name}: {e}")
            postgres_con.rollback()

    # Commit and close connections
    try:
        postgres_con.commit()
        print("Committed changes to PostgreSQL database.")
    except psycopg2.Error as e:
        print(f"Error committing changes to PostgreSQL: {e}")

    sqlite_con.close()
    postgres_con.close()
    print("Migration completed successfully.")


if __name__ == "__main__":
    sqlite_db_path = r"C:\Users\15097\Desktop\FinalBlog\instance\site.db"
    # Use the external URL for running from local machine
    postgres_conn_string = "postgres://blogforum_user:bjeFv7tdR85Sp548mhpwjjeK5sHCypVT@dpg-cq9ltedds78s739fi3fg-a.ohio-postgres.render.com:5432/blogforum"
    sqlite_to_postgres(sqlite_db_path, postgres_conn_string)
