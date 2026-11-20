
import os

SECRET_KEY = os.environ["SUPERSET_SECRET_KEY"]

SQLALCHEMY_DATABASE_URI = (
    "postgresql+psycopg2://"
    f"superset:{os.environ['SUPERSET_DB_PASSWORD']}"
    "@superset-db:5432/superset"
)

SQLALCHEMY_TRACK_MODIFICATIONS = False
