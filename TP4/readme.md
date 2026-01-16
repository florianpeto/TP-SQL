TP Partie 4 : Architecture Graphe (Neo4j)

Objectif : Analyser les relations entre les logements, les quartiers et les époques.

Architecture mise en place :
1. Source : MongoDB (Collection `encadrement_loyers_clean`).
2. ETL : Script Python `scripts/mongo_to_neo4j.py` qui transforme les documents en graphe.
3. Destination : Neo4j Aura (Base orientée Graphe).

Modèle de données :
- Nœuds : `Logement`, `Quartier`, `Epoque`.
- Relations : 
  - `(Logement)-[:SE_TROUVE_DANS]->(Quartier)`
  - `(Logement)-[:CONSTRUIT_EN]->(Epoque)`