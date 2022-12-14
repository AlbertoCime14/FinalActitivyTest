import os
import sqlalchemy
from flask import Flask

app = Flask(__name__)

def connect_unix_socket() -> sqlalchemy.engine.base.Engine:
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME"]
    
    db_socket_dir = os.environ.get("DB_SOCKET_DIR", "/cloudsql")
    
    cloud_sql_connection_name = os.environ["CLOUD_SQL_CONNECTION_NAME"]
    
    pool = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL.create(
            drivername="postgresql+pg8000",
            username=db_user, 
            password=db_pass, 
            database=db_name,
            query={"unix_sock": "{}/.s.PGSQL.5432".format(
                db_socket_dir,
                cloud_sql_connection_name)
            }
        ), # [START_EXCLUDE]
        # Pool size is the maximum number of permanent connections to keep.
        pool_size=5,

        # Temporarily exceeds the set pool_size if no connections are available.
        max_overflow=2,

        # The total number of concurrent connections for your application will be
        # a total of pool_size and max_overflow.

        # 'pool_timeout' is the maximum number of seconds to wait when retrieving a
        # new connection from the pool. After the specified amount of time, an
        # exception will be thrown.
        pool_timeout=30,  # 30 seconds

        # 'pool_recycle' is the maximum number of seconds a connection can persist.
        # Connections that live longer than the specified amount of time will be
        # re-established
        pool_recycle=1800,  # 30 minutes
        # [END_EXCLUDE]
    )
    
    pool.dialect.description_encoding = None
    return pool

@app.route('/')
def main():

    db = connect_unix_socket()

    with db.connect() as conn:
        result = conn.execute("SELECT * from land_registry_price_paid_uk where postcode = 'E15 3AR';").fetchall()

    return str(result)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)