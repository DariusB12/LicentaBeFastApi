from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL) #OBIECTUL CARE GESTIONEAZA CONEXIUNEA LA BAZA DE DATE
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # CREEAZA O FABRICA DE SESIUNI TEMPORARE db = SessionLocal() PENTRU A FOLOSI O SESIUNE

Base = declarative_base() # folosit la fiecare clasa din model


def get_db():
    """
    Function to get db connection, used as dependency in other functions
    :return: the db connection, if the function which is using the db connection is terminated, then the db session is closed
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
