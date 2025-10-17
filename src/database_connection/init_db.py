from .database import Base, engine
import os
# IMPORT TOATE MODELELE
from src.model.entities import User, SocialMediaAccount, Analysis, Post, PostPhoto, Comment



# !!!!TREBUIE IMPORTATE TOATE MODELELE AICI PENTRU A FI CREATE IN BAZA DE DATE!!!!!

# PENTRU A CREA TOATE TABELELE IN POSTGRES
# NU POATE FACE UPDATE LA TABELE DACA ADAUG COLOANE NOI DUPA, TREBUIE SA STERG TABELELE INAINTE DE A FACE INIT
# COMANDA TERMINAL:  python -m database_connection.init_db

print(f"Connecting to database: {os.getenv("DATABASE_URL")}")
Base.metadata.create_all(bind=engine)
print("Tabelele au fost create.")