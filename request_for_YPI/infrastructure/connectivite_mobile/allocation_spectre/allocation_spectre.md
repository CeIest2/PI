### Analyse de l’Indicateur SRI (Spectre d’Allocation Réseau)

Cet indicateur du pilier « Infrastructure » évalue la capacité d’allocation du spectre Internet national, c’est-à-dire la portion d’adressage IP effectivement utilisée et annoncée par les opérateurs du pays.
L’objectif est de mesurer la densité d’utilisation du spectre d’adressage BGP par les Systèmes Autonomes (:AS) locaux, reflet direct du poids technique du pays dans l’espace Internet mondial.

Les entités techniques clés impliquées sont :

les :AS (Systèmes Autonomes opérant dans le pays),

les :BGPPrefix (préfixes IP annoncés publiquement via le protocole BGP),

et le :Country (pays d’appartenance des opérateurs).

### Pertinence YPI et Plan d’Analyse Technique

Évaluation de pertinence : Cas A (Très Pertinent).
Le schéma YPI intègre des relations :ORIGINATE entre les :AS et leurs :BGPPrefix, issues de jeux de données CAIDA et RIPE RIS.
Cela permet une évaluation fidèle du volume d’adresses IP actives et du niveau d’activité réseau des opérateurs nationaux.

Note sur la portée :
L’indicateur mesure la capacité d’allocation et d’utilisation du spectre IP sur la partie BGP — il ne couvre pas les bandes hertziennes ou spectres radio au sens télécom, mais se concentre sur le spectre logique de l’Internet routé.

Voici le plan d’analyse technique pour cet indicateur :

#### Requête 1 : Volume de Préfixes BGP Originés par les AS Locaux

Objectif de la requête :
Quantifier le nombre total de préfixes IP annoncés (originés) par les Systèmes Autonomes d’un pays.
Cela donne une mesure directe de la taille du spectre Internet utilisé par le pays dans le routage mondial.

Requête Cypher :
```
// Allocation du spectre : préfixes originés par les AS du pays.

MATCH (a:AS)-[:COUNTRY]->(c:Country {country_code: $countryCode})
MATCH (a)-[:ORIGINATE]->(p:BGPPrefix)
RETURN c.name AS Country,
       COUNT(DISTINCT p) AS Originated_Prefixes;
```
Interprétation :
Le nombre de Originated_Prefixes représente le volume d’adresses IP effectivement visibles dans le routage mondial pour ce pays.
Une valeur élevée traduit une capacité technique et économique forte, une bonne gestion du spectre IP, et un haut niveau d’activité réseau.
Une valeur faible suggère une sous-exploitation du spectre ou une dépendance à des opérateurs étrangers pour l’annonce des routes BGP nationales.

### Objectif Global de l’Analyse

L’exécution de cette requête permet de :

mesurer la taille réelle du spectre d’adressage IP routé par les acteurs nationaux,

évaluer la maturité du réseau à travers sa visibilité mondiale,

et identifier les disparités régionales (pays sous-annoncés ou concentrant l’adressage dans peu d’AS).

### Interprétation Stratégique
Situation observée	Interprétation possible
Grand nombre de préfixes originés	Pays à forte autonomie réseau et large spectre IP utilisé
Peu de préfixes originés	Couverture logique limitée, dépendance à l’international
Concentration sur peu d’AS	Risque de centralisation et de vulnérabilité du routage
Répartition équilibrée entre de nombreux AS	Écosystème résilient et bien distribué

### Recommandations d’Amélioration

Renforcement de la gestion du spectre IP :
Encourager les opérateurs locaux à obtenir et annoncer leurs propres préfixes, plutôt que de dépendre d’entités tierces.

Diversification des annonceurs BGP :
Réduire la concentration en favorisant plus d’AS actifs dans le routage national.

Optimisation de la visibilité mondiale :
Mettre en place des politiques nationales favorisant l’autonomie du routage, notamment via des IXP nationaux ou régionaux.

Surveillance continue :
Intégrer le suivi des préfixes originés dans une veille régulière de la topologie BGP, pour détecter rapidement toute perte de spectre (ex. hijack, retrait d’annonces).