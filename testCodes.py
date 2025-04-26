from dotenv import load_dotenv
import os

if __name__ == '__main__':
    # Încarcă variabilele din fișierul .env
    load_dotenv()

    # Accesează variabila de mediu
    database_url = os.getenv("DATABASE_URL")

    print("DATABASE_URL:", database_url)