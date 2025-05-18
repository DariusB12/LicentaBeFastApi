from .database import Base, engine
# IMPORT TOATE MODELELE
from model.entities import User, SocialMediaAccount, Comment, PostPhoto, Post


# !!!!TREBUIE IMPORTATE TOATE MODELELE AICI PENTRU A FI CREATE IN BAZA DE DATE!!!!!

# PENTRU A CREA TOATE TABELELE IN POSTGRES
# NU POATE FACE UPATE LA TABELE DACA ADAUG COLOANE NOI DUPA
# COMANDA TERMINAL:  python -m database_connection.init_db

Base.metadata.create_all(bind=engine)
print("Tabelele au fost create.")
