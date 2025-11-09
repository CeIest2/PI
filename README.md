# Projet Industriel : Internet Society

## Installation

### Créer un environnement virtuel (venv)

Avant d'installer les dépendances, il est recommandé d'utiliser un environnement virtuel à la racine  du projet pour isoler l'application :

```bash
python -m venv venv
```


### Activer l'environnement virtuel

- **Windows** :
  ```bash
  venv\Scripts\activate
  ```
- **Linux/macOS** :
  ```bash
  source venv/bin/activate
  ```

### Installer les dépendances

Une fois le venv activé, installe les dépendances listées dans `requirements.txt` :

```bash
pip install -r requirements.txt
```

### Lancer neo4j
(à remplacer par un modèle plus souple)
```bash
./neo4j-desktop-<version>.AppImage
```
Ouvrir ensuite Neo4j Browser via “Open” (sur la base de données désirée)