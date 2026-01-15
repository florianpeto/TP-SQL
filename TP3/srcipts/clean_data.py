import os
import pymongo
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DBNAME", "immobilier_paris")
SOURCE_COLLECTION = "encadrement_loyers" 
TARGET_COLLECTION = "encadrement_loyers_clean" 

def clean_and_store():
    print(" Démarrage du nettoyage...")
    
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    data = list(db[SOURCE_COLLECTION].find())
    df = pd.DataFrame(data)
    
    if df.empty:
        print(" Aucune donnée à nettoyer.")
        return

    print(f" Données brutes : {len(df)} lignes")
    print(" Colonnes détectées :", list(df.columns))

   
    if '_id' in df.columns: del df['_id']

    col_gps = 'geo_point_2d' if 'geo_point_2d' in df.columns else 'geo_point'
    
    if col_gps in df.columns:
        def extract_lat(geo):
            if isinstance(geo, dict): return geo.get('lat')
            if isinstance(geo, list) and len(geo) > 0: return geo[0]
            return None
        
        def extract_lon(geo):
            if isinstance(geo, dict): return geo.get('lon')
            if isinstance(geo, list) and len(geo) > 1: return geo[1]
            return None

        df['latitude'] = df[col_gps].apply(extract_lat)
        df['longitude'] = df[col_gps].apply(extract_lon)
    else:
        df['latitude'] = None
        df['longitude'] = None

   
    if 'ref' in df.columns:
        df['loyer_ref'] = pd.to_numeric(df['ref'], errors='coerce')
    elif 'loyer_de_reference' in df.columns:
        df['loyer_ref'] = pd.to_numeric(df['loyer_de_reference'], errors='coerce')
    else:
        print(" Aucune colonne de prix trouvée (ref ou loyer_de_reference)")
        df['loyer_ref'] = None 

   
    col_piece_source = 'piece' if 'piece' in df.columns else 'nombre_pieces_principales'
    
    if col_piece_source in df.columns:
        df['nb_pieces'] = pd.to_numeric(df[col_piece_source], errors='coerce')
    else:
        df['nb_pieces'] = 0

  
    df_clean = df.dropna(subset=['latitude', 'loyer_ref'])
    
    print(f" Données propres restantes : {len(df_clean)} lignes")

    if len(df_clean) > 0:
        records = df_clean.to_dict(orient='records')
        db[TARGET_COLLECTION].delete_many({})
        db[TARGET_COLLECTION].insert_many(records)
        print(f" Sauvegardé dans la collection : {TARGET_COLLECTION}")
    else:
        print(" Attention : Toutes les lignes ont été supprimées lors du nettoyage.")

if __name__ == "__main__":
    clean_and_store()