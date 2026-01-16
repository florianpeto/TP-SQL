import os
import pymongo
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()


MONGO_URI = os.getenv("mongodb+srv://petoflorian1_db_user:mERgNbx5tKjNCYec@cluster0.554ztei.mongodb.net/?retryWrites=true&w=majority")
MONGO_DB = os.getenv("immobilier_paris")
MONGO_COLL = "encadrement_loyers_clean"

NEO4J_URI = os.getenv("neo4j+s://1512b3b5.databases.neo4j.io")
NEO4J_USER = os.getenv("neo4j")
NEO4J_PASSWORD = os.getenv("yEqTBJFCqYaM1jWrurLxUaRSCTImNgCxL_i2wwGA-SI")


class ETLGraph:
    def __init__(self):
        
        self.mongo_client = pymongo.MongoClient("mongodb+srv://petoflorian1_db_user:mERgNbx5tKjNCYec@cluster0.554ztei.mongodb.net/?retryWrites=true&w=majority")
        self.mongo_col = self.mongo_client["immobilier_paris"]["encadrement_loyers_clean"]
        
        
        self.driver = GraphDatabase.driver("neo4j+s://1512b3b5.databases.neo4j.io", auth=("neo4j", "yEqTBJFCqYaM1jWrurLxUaRSCTImNgCxL_i2wwGA-SI"))

    def close(self):
        self.driver.close()
        self.mongo_client.close()

    def load_data(self):
        print(" Démarrage de l'export Mongo -> Neo4j...")
        
        
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print(" Base Neo4j nettoyée.")

        
        cursor = self.mongo_col.find({})
        count = 0

        for doc in cursor:
            
            quartier = doc.get("nom_quartier", "Inconnu")
            epoque = doc.get("epoque") or doc.get("epoque_construction", "Inconnue")
            nb_pieces = doc.get("nb_pieces", 0)
            loyer = doc.get("loyer_ref", 0)
            ville = doc.get("ville", "Paris")

            
            with self.driver.session() as session:
                session.execute_write(self._create_nodes, quartier, epoque, nb_pieces, loyer, ville)
            
            count += 1
            if count % 10 == 0:
                print(f" {count} logements traités...")

        print(f" Terminé ! {count} nœuds créés dans le graphe.")

    @staticmethod
    def _create_nodes(tx, quartier_nom, epoque_nom, pieces, loyer, ville_nom):
       
        query = """
        // 1. On s'assure que le Quartier existe (sinon on le crée)
        MERGE (q:Quartier {nom: $quartier})
        
        // 2. On s'assure que l'Époque existe
        MERGE (e:Epoque {annee: $epoque})
        
        // 3. On crée le Logement (CREATE car chaque logement est unique)
        CREATE (l:Logement {
            loyer: $loyer,
            pieces: $pieces,
            ville: $ville
        })
        
        // 4. On crée les liens (RELATIONS)
        CREATE (l)-[:SE_TROUVE_DANS]->(q)
        CREATE (l)-[:CONSTRUIT_EN]->(e)
        """
        
        tx.run(query, quartier=quartier_nom, epoque=epoque_nom, 
               loyer=loyer, pieces=pieces, ville=ville_nom)

if __name__ == "__main__":
    etl = ETLGraph()
    try:
        etl.load_data()
    except Exception as e:
        print(f" Erreur : {e}")
    finally:
        etl.close()