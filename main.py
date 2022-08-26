import os
import sqlalchemy
from flask import Flask

app = Flask(__name__)

def init_unix_connection_engine():
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME"]
    
    db_socket_dir = os.environ.get("DB_SOCKET_DIR", "/cloudsql")
    
    cloud_sql_connection_name = os.environ["CLOUD_SQL_CONNECTION_NAME"]
    
    pool = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL(
            drivername="postgresql+pg8000",
            username=db_user, 
            password=db_pass, 
            database=db_name,
            query={"unix_sock": "{}/{}/.s.PGSQL.5432".format(
                db_socket_dir,
                cloud_sql_connection_name)
            }
        )
    )
    
    pool.dialect.description_encoding = None
    return pool

@app.route('/')
def main():

    db = init_unix_connection_engine()

    with db.connect() as conn:
        result = conn.execute("SELECT * from land_registry_price_paid_uk where postcode = 'E15 3AR';").fetchall()

    return str(result)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)