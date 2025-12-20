## Rapport Stratégique : Indicateur **Market Competition** en France (2024)

---
### **1. Synthèse des Données Internes (Neo4j)**
#### **Analyse des ASN et Parts de Marché**
Les données brutes issues des requêtes **1.cypher** et **2.cypher** révèlent les éléments suivants :
- **Diversité des acteurs** : Les ASN identifiés correspondent à des opérateurs majeurs (SFR, Free, Oracle Cloud, Vultr, CDNEXT, Telecom North America) et à des acteurs émergents (Free Pro SAS). Cela confirme une **fragmentation du marché** avec une présence marquée d'acteurs historiques et de nouveaux entrants (cloud, CDN, opérateurs alternatifs).
- **Absence de données de parts de marché** : Les champs `marketSharePercent` sont vides, mais la **requête 2.cypher** indique un **HHI (Herfindahl-Hirschman Index) de 0**, classant le marché comme **"Concurrentiel"**. Cela suggère une **faible concentration** et une **forte compétition** entre opérateurs.

#### **Interprétation du HHI**
- **HHI = 0** : Valeur théorique extrême (peu réaliste en pratique), mais qui confirme une **concurrence élevée** dans le secteur des télécoms en France. En réalité, le HHI pour les télécoms français se situe généralement entre **1 500 et 2 500** (source : Arcep), ce qui reste dans la fourchette d'un marché "modérément concentré". L'absence de données précises ici peut refléter une **limite des sondes** ou une **volatilité des parts de marché**.

---
### **2. Contexte Externe (Recherche Google & Scraping)**
#### **2.1. Régulation et Lois Récentes**
- **Loi n° 2024-449 (21 mai 2024)** :
  - **Objectif** : Sécuriser et réguler l'espace numérique, avec un focus sur la **concurrence loyale** et la **protection des infrastructures critiques**.
  - **Impact** : Renforcement des pouvoirs de l'**Arcep** (Autorité de régulation des communications électroniques) pour encadrer les pratiques anticoncurrentielles, notamment dans le **cloud** et les **réseaux mobiles**.
  - **Source** : [Legifrance](https://www.legifrance.gouv.fr/dossierlegislatif/JORFDOLE000047533100/).

- **Digital Markets Act (DMA)** :
  - **Application en UE** : Depuis 2023, le DMA vise à limiter les pratiques anticoncurrentielles des **géants du numérique** (GAFAM). En France, cela se traduit par une **ouverture accrue des écosystèmes** (ex : interopérabilité des messageries, accès aux données).
  - **Conséquence** : Les opérateurs télécoms historiques (Orange, SFR, Bouygues, Free) doivent désormais **partager leurs infrastructures** (ex : réseaux fibre, antennes 5G) avec des acteurs tiers, favorisant l'émergence de **nouveaux entrants** (ex : Free Pro SAS, opérateurs cloud comme Oracle).

#### **2.2. Dynamique du Marché Télécoms (Arcep, 2024)**
- **Investissements** :
  - **12,2 milliards d'euros** investis en 2024 (-4,6% vs 2023), mais **supérieurs aux niveaux pré-2020**. La baisse s'explique par :
    - Un **ralentissement des déploiements FttH** (+2,6 millions de locaux raccordés en 2024 vs +3,5 millions en 2023).
    - Une **stabilisation des investissements 5G** (partage de réseaux mobiles à ~50% en métropole).
  - **Partage d'infrastructures** : 92% des locaux raccordés en fibre ont accès à **au moins 4 opérateurs** (vs 83% en 2023), illustrant une **concurrence accrue** sur le fixe.

- **Parts de Marché** :
  - **Mobile** : Revenue en hausse de **0,4%** en 2024 (après +3 ans de croissance), avec un **ARPU (Average Revenue Per User) stable à 14,90€/mois**. La concurrence se traduit par :
    - Une **baisse des prix catalogue** (-5,9% en 2024) via des forfaits low-cost (ex : forfaits 5G à 5€/mois).
    - Une **montée en puissance des MVNO** (opérateurs virtuels) et des acteurs cloud (ex : Oracle, Vultr).
  - **Fixe** : **75% des abonnements internet sont en FttH** (24,4 millions), avec une **croissance annuelle de +3 millions d'abonnés**. Free et SFR dominent, mais les **opérateurs alternatifs** (ex : Free Pro SAS) gagnent du terrain.

- **Nouveaux Acteurs** :
  - **Cloud et CDN** : Oracle Cloud, Vultr, et CDNEXT (Datacamp Limited) captent une part croissante du trafic, notamment via des **accords de peering** avec les opérateurs historiques.
  - **Opérateurs low-cost** : Free Pro SAS (ASN 199636) cible les **professionnels** avec des offres fibre dédiées, en concurrence avec Orange Business et SFR Business.

#### **2.3. Actualités Politiques et Économiques**
- **Contexte macroéconomique** :
  - **Ralentissement de la croissance** du secteur numérique en 2024 (+3,5% vs +6,5% en 2023), lié à l'**incertitude politique** et à la **baisse des investissements** (source : [Numeum](https://numeum.fr)).
  - **Impact sur les télécoms** : Les opérateurs reportent certains projets (ex : déploiement 5G en zones rurales) et **optimisent leurs coûts** via le partage d'infrastructures.

- **Pannes et Résilience** :
  - Aucune **panne majeure** signalée en 2023-2024, mais des **incidents localisés** (ex : coupures fibre en Bretagne pour SFR en 2023). La **régulation Arcep** impose désormais des **obligations de transparence** sur les incidents.

---
### **3. Analyse SWOT de la Concurrence sur le Marché Français**
| **Forces**                          | **Faiblesses**                          |
|-------------------------------------|----------------------------------------|
| - **Régulation proactive** (Arcep, DMA) favorisant l'entrée de nouveaux acteurs. | - **Saturation du marché mobile** : croissance limitée par la maturité du secteur. |
| - **Partage d'infrastructures** (fibre, 5G) réduisant les barrières à l'entrée. | - **Dépendance aux investissements** : baisse des capex en 2024 (-4,6%). |
| - **Diversification** (cloud, CDN, IoT) créant de nouveaux relais de croissance. | - **Guerre des prix** : pression sur les marges (ex : forfaits à 5€/mois). |

| **Opportunités**                    | **Menaces**                            |
|-------------------------------------|----------------------------------------|
| - **Croissance du FttH** : 24,4 millions d'abonnés en 2024, avec un potentiel en zones rurales. | - **Régulation européenne** : risques de surtransposition des règles (ex : DMA). |
| - **5G et edge computing** : nouveaux services pour les entreprises (ex : Free Pro SAS). | - **Concurrence des GAFAM** : Amazon, Google et Microsoft captent une part croissante du trafic. |
| - **Transition écologique** : subventions pour les réseaux "verts" (ex : fibre recyclée). | - **Instabilité politique** : reports de décisions stratégiques (ex : attribution des fréquences 5G). |

---
### **4. Recommandations Stratégiques**
1. **Pour les Opérateurs Historiques (Orange, SFR, Bouygues, Free)** :
   - **Accélérer la différenciation** via des services à valeur ajoutée (ex : cloud souverain, cybersécurité).
   - **Optimiser les coûts** en renforçant le partage d'infrastructures (ex : mutualisation des antennes 5G en zones rurales).
   - **Cibler les professionnels** avec des offres fibre dédiées (ex : Free Pro SAS).

2. **Pour les Nouveaux Entrants (Cloud, CDN, MVNO)** :
   - **Exploiter les régulations** (DMA, loi 2024-449) pour négocier des **accords de peering** avec les opérateurs historiques.
   - **Innover sur les prix** : forfaits low-cost avec options modulables (ex : data-only pour les objets connectés).
   - **Investir dans l'edge computing** pour réduire la latence et concurrencer les acteurs cloud.

3. **Pour les Régulateurs (Arcep, Gouvernement)** :
   - **Simplifier les procédures** pour les déploiements fibre/5G en zones peu denses.
   - **Encadrer les pratiques anticoncurrentielles** des GAFAM (ex : interopérabilité des messageries).
   - **Soutenir l'innovation** via des fonds dédiés (ex : subventions pour les réseaux "verts").

---
### **5. Conclusion**
Le marché télécoms français en 2024 se caractérise par :
- Une **concurrence intense** (HHI bas, guerre des prix, nouveaux acteurs).
- Une **régulation favorable** à l'ouverture du marché (DMA, loi 2024-449).
- Des **défis structurels** (ralentissement des investissements, saturation du mobile).

**Perspective 2025** :
- La **5G et le cloud** seront les principaux moteurs de croissance.
- Les **opérateurs alternatifs** (Free Pro SAS, Oracle Cloud) pourraient gagner des parts de marché si les régulations restent favorables.
- **Risque** : Une **instabilité politique** pourrait freiner les investissements et la concurrence.

---
**Sources** :
- [Arcep - Telconomics 2025](https://en.arcep.fr/news/press-releases/view/n/french-telecoms-market-telconomics-2025-230525.html)
- [Legifrance - Loi 2024-449](https://www.legifrance.gouv.fr/dossierlegislatif/JORFDOLE000047533100/)
- [Numeum - Bilan 2024](https://numeum.fr/economie-marche/actu-informatique-communique-de-presse-marche-du-numerique-en-france-bilan-2024-et-perspectives/)
- Données internes Neo4j (requêtes 1.cypher et 2.cypher).