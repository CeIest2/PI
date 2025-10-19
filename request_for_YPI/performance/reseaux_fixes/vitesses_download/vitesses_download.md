### Analyse de l'Indicateur IRI

Cet indicateur, rattaché au pilier **PERFORMANCE**, mesure directement la qualité de l'expérience utilisateur en quantifiant le débit descendant (download) disponible sur les réseaux fixes et mobiles d'un pays. Un score élevé signifie que les utilisateurs bénéficient de connexions rapides et fluides, essentielles pour les usages modernes (streaming, télétravail, etc.). Les entités techniques sous-jacentes sont les réseaux des fournisseurs d'accès (`:AS`), mais l'indicateur lui-même est une métrique de performance qui n'est pas une entité de topologie.

### Pertinence YPI et Plan d'Analyse Technique

* **Évaluation de pertinence :** Cas B (Non-Pertinent).

L'indicateur "Vitesses d'upload/download" ne peut pas être analysé directement avec le schéma YPI. La source de données spécifiée par l'IRI est **Ookla**, une entité externe qui collecte des données de performance via des tests de vitesse effectués par les utilisateurs.

Le graphe YPI est un modèle de la **topologie** et des **relations structurelles** de l'Internet (qui est connecté à qui, quelles ressources sont allouées, etc.). Il ne contient pas de données de **performance en temps réel** ou de **mesures de qualité d'expérience** telles que les débits montants ou descendants. Par conséquent, il n'existe aucune requête Cypher permettant d'extraire ou d'analyser cette information depuis YPI.