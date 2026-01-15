-- CREATION DE TABLE

CREATE TABLE utilisateurs (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(255) NOT NULL, 
    date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE produits (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    description TEXT,
    prix DECIMAL(10, 2) NOT NULL CHECK (prix >= 0),
    stock INT NOT NULL DEFAULT 0 CHECK (stock >= 0)
);

CREATE TABLE commandes (
    id SERIAL PRIMARY KEY,
    utilisateur_id INT REFERENCES utilisateurs(id) ON DELETE SET NULL,
    date_commande TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statut VARCHAR(20) DEFAULT 'EN_ATTENTE', 
    montant_total DECIMAL(10, 2) DEFAULT 0
);


CREATE TABLE lignes_commandes (
    id SERIAL PRIMARY KEY,
    commande_id INT REFERENCES commandes(id) ON DELETE CASCADE,
    produit_id INT REFERENCES produits(id),
    quantite INT NOT NULL CHECK (quantite > 0),
    prix_unitaire DECIMAL(10, 2) NOT NULL 
);


CREATE TABLE avis (
    id SERIAL PRIMARY KEY,
    utilisateur_id INT REFERENCES utilisateurs(id) ON DELETE CASCADE,
    produit_id INT REFERENCES produits(id) ON DELETE CASCADE,
    note INT CHECK (note BETWEEN 1 AND 5),
    commentaire TEXT,
    date_avis TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE journaux_activite (
    id SERIAL PRIMARY KEY,
    utilisateur_id INT REFERENCES utilisateurs(id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL,
    horodatage TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- INSERTION DES DONNEES


INSERT INTO utilisateurs (nom, email, mot_de_passe) VALUES
('Alice Dupont', 'alice@email.com', 'pass123'),
('Bob Martin', 'bob@email.com', 'pass456'),
('Charlie Durand', 'charlie@email.com', 'pass789');

INSERT INTO produits (nom, description, prix, stock) VALUES
('Smartphone X', 'Dernier modèle, 128Go', 699.99, 50),
('Casque Audio', 'Réduction de bruit active', 199.50, 100),
('Clavier Mécanique', 'Switchs bleus, RGB', 89.90, 20);

INSERT INTO commandes (utilisateur_id, statut, montant_total) VALUES
(1, 'PAYEE', 899.49); 
INSERT INTO lignes_commandes (commande_id, produit_id, quantite, prix_unitaire) VALUES
(1, 1, 1, 699.99),
(1, 2, 1, 199.50);
INSERT INTO avis (utilisateur_id, produit_id, note, commentaire) VALUES
(2, 2, 5, 'Son incroyable, je recommande !');

INSERT INTO journaux_activite (utilisateur_id, action) VALUES
(1, 'Connexion réussie'),
(1, 'Commande #1 validée');


-- JOINTURE 

SELECT 
    c.id as commande_id,
    u.nom as client,
    p.nom as produit,
    lc.quantite,
    lc.prix_unitaire
FROM commandes c
JOIN utilisateurs u ON c.utilisateur_id = u.id
JOIN lignes_commandes lc ON c.id = lc.commande_id
JOIN produits p ON lc.produit_id = p.id;
SELECT 
    p.nom,
    COUNT(a.id) as nombre_avis,
    ROUND(AVG(a.note), 1) as note_moyenne
FROM produits p
LEFT JOIN avis a ON p.id = a.produit_id
GROUP BY p.id, p.nom
ORDER BY note_moyenne DESC;

-- Début de la transaction
BEGIN;

INSERT INTO commandes (utilisateur_id, statut, montant_total) 
VALUES (2, 'PAYEE', 89.90);

INSERT INTO lignes_commandes (commande_id, produit_id, quantite, prix_unitaire) 
VALUES (2, 3, 1, 89.90);

UPDATE produits 
SET stock = stock - 1 
WHERE id = 3;

COMMIT;
