import os
import sqlalchemy
from flask import Flask

app = Flask(__name__)

def init_unix_connection_engine(db_config):
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME"]
    
    db_socket_dir = os.environ.get("DB_SOCKET_DIR", "/cloudsql")
    
    cloud_sql_connection_name = os.environ["INSTANCE_CONNECTION_NAME"]
    
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
        ),
        pool_size=5,
        # Temporarily exceeds the set pool_size if no connections are available.
        max_overflow=2,
        # The total number of concurrent connections for your application will be
        # a total of pool_size and max_overflow.
        # [END cloud_sql_postgres_sqlalchemy_limit]

        # [START cloud_sql_postgres_sqlalchemy_backoff]
        # SQLAlchemy automatically uses delays between failed connection attempts,
        # but provides no arguments for configuration.
        # [END cloud_sql_postgres_sqlalchemy_backoff]

        # [START cloud_sql_postgres_sqlalchemy_timeout]
        # 'pool_timeout' is the maximum number of seconds to wait when retrieving a
        # new connection from the pool. After the specified amount of time, an
        # exception will be thrown.
        pool_timeout=30,  # 30 seconds
        # [END cloud_sql_postgres_sqlalchemy_timeout]

        # [START cloud_sql_postgres_sqlalchemy_lifetime]
        # 'pool_recycle' is the maximum number of seconds a connection can persist.
        # Connections that live longer than the specified amount of time will be
        # re-established
        pool_recycle=1800,  # 30 minutes
        # [END cloud_sql_postgres_sqlalchemy_lifetime]
        # [END_EXCLUDE]
    )
    
    pool.dialect.description_encoding = None
    return pool

@app.route('/')
def main():

    db = init_unix_connection_engine(pool_size=20, max_overflow=2, pool_timeout=30, pool_recycle=1800)

    with db.connect() as conn:
        result = conn.execute().fetchall()

    return str(result)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)