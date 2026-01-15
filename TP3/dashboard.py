import streamlit as st
import pymongo
import pandas as pd
import os
from dotenv import load_dotenv
import time


st.set_page_config(page_title="Immo Paris Dashboard", layout="wide")
load_dotenv()


@st.cache_resource
def get_connection():
    MONGO_URI = os.getenv("MONGO_URI")
    return pymongo.MongoClient(MONGO_URI)

try:
    client = get_connection()
    db = client[os.getenv("MONGO_DBNAME", "immobilier_paris")]
    collection = db["encadrement_loyers_clean"]
except Exception as e:
    st.error(f"Erreur de connexion MongoDB : {e}")
    st.stop()


st.sidebar.title(" Gestion Immo")


st.sidebar.subheader("Ajouter manuellement")
with st.sidebar.form("add_form"):
    
    quartier_input = st.text_input("Quartier", "Bastille")
    pieces_input = st.number_input("Nb Pièces", 1, 10, 2)
    loyer_input = st.number_input("Loyer Ref (€/m²)", 10.0, 50.0, 25.0)
    

    lat_input = st.number_input("Latitude", 48.80, 48.90, 48.85)
    lon_input = st.number_input("Longitude", 2.25, 2.45, 2.34)
    
    submitted = st.form_submit_button("Ajouter en base")
    if submitted:
        new_doc = {
            "nom_quartier": quartier_input, 
            "nb_pieces": pieces_input,
            "loyer_ref": loyer_input,
            "latitude": lat_input,
            "longitude": lon_input,
            "ville": "Paris",
            "source": "Manuel"
        }
        collection.insert_one(new_doc)
        st.sidebar.success(" Ajouté !")
        time.sleep(1) 
        st.rerun() 


st.sidebar.markdown("---")
st.sidebar.subheader("Supprimer des données")
quartier_to_del = st.sidebar.text_input("Nom du quartier à supprimer")
if st.sidebar.button(" Supprimer"):
    if quartier_to_del:
        res = collection.delete_many({"nom_quartier": quartier_to_del})
        st.sidebar.warning(f"{res.deleted_count} annonces supprimées.")
        time.sleep(1)
        st.rerun()


st.title(" Dashboard Encadrement des Loyers")



data = list(collection.find({}, {"_id": 0})) 
df = pd.DataFrame(data)

if not df.empty:
    
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Annonces", len(df))
    
    
    prix_moyen = round(df['loyer_ref'].mean(), 2) if 'loyer_ref' in df.columns else 0
    kpi2.metric("Loyer Moyen", f"{prix_moyen} €/m²")
    
    nb_quartiers = df['nom_quartier'].nunique() if 'nom_quartier' in df.columns else 0
    kpi3.metric("Quartiers", nb_quartiers)

    st.markdown("---")

    
    col_map, col_chart = st.columns([2, 1])

    with col_map:
        st.subheader(" Carte des logements")
        
        if 'latitude' in df.columns and 'longitude' in df.columns:
            
            map_df = df.dropna(subset=['latitude', 'longitude'])
            st.map(map_df)
        else:
            st.warning("Pas de colonnes latitude/longitude trouvées.")

    with col_chart:
        st.subheader(" Prix vs Pièces")
        if 'nb_pieces' in df.columns and 'loyer_ref' in df.columns:
            chart_data = df.groupby('nb_pieces')['loyer_ref'].mean()
            st.bar_chart(chart_data)
        else:
            st.info("Données insuffisantes pour le graphique.")

    
    st.subheader(" Tableau des données")
    st.dataframe(df, use_container_width=True)

else:
    st.warning(" La collection est vide. Lance le script 'clean_data.py' d'abord !")