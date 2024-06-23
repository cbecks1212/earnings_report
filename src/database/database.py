from google.cloud import secretmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

client = secretmanager.SecretManagerServiceClient()
project_id = "orbital-kit-400022"
db_secret_id = "POSTGRES_URI"

db_secret = f"projects/{project_id}/secrets/{db_secret_id}/versions/latest"
response = client.access_secret_version(request={"name": db_secret})
db_decoded_secret = response.payload.data.decode("UTF-8")

DATABASE_URL = db_decoded_secret
ENGINE = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)

Base = declarative_base()
