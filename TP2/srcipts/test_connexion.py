import os
import pymongo
from dotenv import load_dotenv

# Charger l'env
load_dotenv()

def test_mongo():
    print("Testing MongoDB Connection...")
    uri = os.getenv("MONGO_URI")
    
    if not uri:
        print(" Erreur : Pas de MONGO_URI dans le .env")
        return

    try:
        # Création du client avec un timeout court (5 secondes) pour ne pas attendre indéfiniment
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # Commande 'ping' simple
        client.admin.command('ping')
        
        print(" SUCCÈS : Connexion à MongoDB Atlas établie !")
        
        
    except pymongo.errors.ServerSelectionTimeoutError:
        print(" ÉCHEC : Impossible de joindre le serveur (Timeout).")
        print("   -> Vérifiez votre IP dans la whitelist MongoDB Atlas (Network Access).")
    except pymongo.errors.OperationFailure:
        print(" ÉCHEC : Erreur d'authentification.")
        print("   -> Vérifiez username/password dans MONGO_URI.")
    except Exception as e:
        print(f" Erreur inattendue : {e}")

if __name__ == "__main__":
    test_mongo()