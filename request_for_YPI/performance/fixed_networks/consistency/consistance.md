### Analyse de l'Indicateur IRI

Cet indicateur, rattaché au pilier "PERFORMANCE", mesure la **consistance** de la qualité du service Internet pour les réseaux fixes et mobiles. Il ne s'agit pas seulement de la vitesse de pointe, mais de la fiabilité et de la stabilité de la connexion, c'est-à-dire la probabilité pour un utilisateur d'atteindre un seuil de performance de base de manière constante. La source de cette donnée est **Ookla**.

Les entités techniques sous-jacentes qui influencent cette métrique sont l'ensemble de l'infrastructure de livraison : les réseaux d'accès, les points d'interconnexion (`:IXP`), et les systèmes autonomes (`:AS`) qui transportent le trafic. Cependant, l'indicateur lui-même est une mesure de performance de bout en bout, pas une simple description de la topologie.

### Pertinence YPI et Plan d'Analyse Technique

* **Évaluation de pertinence :** Cas B (Non-Pertinent).

L'indicateur de "Consistance" est une métrique de performance quantitative dérivée de tests de vitesse et de qualité de connexion effectués par les utilisateurs finaux (source : Ookla).

Le schéma de données YPI, bien que très riche, est un graphe de connaissances sur la **topologie, l'infrastructure et les relations structurelles** de l'Internet (relations de peering BGP, appartenance aux IXP, enregistrements RPKI, etc.). Il ne contient **aucune donnée de mesure de performance en temps réel ou agrégée** comme la latence, le jitter, les débits ou les scores de consistance provenant de plateformes comme Ookla.

Par conséquent, il est impossible de requêter directement le YPI pour analyser ou valider cet indicateur spécifique. Toute tentative de corrélation (par exemple, "les pays avec plus d'IXP ont-ils une meilleure consistance ?") serait une analyse indirecte et spéculative, ce qui va à l'encontre de l'objectif de comprendre les réalités techniques *directement* liées à l'indicateur.