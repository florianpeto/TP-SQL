import requests
import pymongo



MONGO_URI = "mongodb+srv://petoflorian1_db_user:mERgNbx5tKjNCYec@cluster0.554ztei.mongodb.net/?retryWrites=true&w=majority"
DB_NAME = "immobilier_paris"
COLLECTION_NAME = "encadrement_loyers"
API_URL = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/logement-encadrement-des-loyers/records?limit=20"

def force_test():
    print(" Démarrage du script ")

    
    
    print(f"  Database cible : {DB_NAME}")
    print(f"  Collection cible : {COLLECTION_NAME}")

    
    try:
        print(" Appel API...")
        response = requests.get(API_URL)
        data = response.json()
        results = data.get('results', [])
        print(f" API OK : {len(results)} données reçues.")
    except Exception as e:
        print(f" Erreur API : {e}")
        return

    
    try:
        print(" Connexion MongoDB...")
        
        client = pymongo.MongoClient(MONGO_URI)
        
        db = client[DB_NAME]             
        collection = db[COLLECTION_NAME] 
        
        if len(results) > 0:
            insert_result = collection.insert_many(results)
            print(f"🎉 SUCCÈS TOTAL : {len(insert_result.inserted_ids)} documents insérés !")
        else:
            print(" API vide, rien à insérer.")

    except Exception as e:
        print(f" Erreur MongoDB : {e}")

if __name__ == "__main__":
    force_test()