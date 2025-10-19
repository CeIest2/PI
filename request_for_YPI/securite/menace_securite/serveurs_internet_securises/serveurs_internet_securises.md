### Analyse de l'Indicateur IRI

Cet indicateur du pilier "Sécurité" vise à mesurer la prévalence des serveurs Internet offrant des communications chiffrées (via TLS/SSL, le protocole derrière HTTPS) dans un pays. Un score élevé signifie qu'une plus grande partie des services hébergés localement protège les données en transit, renforçant ainsi la confidentialité et l'intégrité des échanges entre les utilisateurs et les services. Les entités techniques clés sont les serveurs (identifiés par leurs adresses `:IP`), les noms de domaine (`:DomainName`) qu'ils hébergent, les systèmes autonomes (`:AS`) auxquels ils appartiennent, et leur pays (`:Country`) de localisation.

### Pertinence YPI et Plan d'Analyse Technique

* **Évaluation de pertinence :** Cas B (Non-Pertinent).

L'analyse directe de cet indicateur n'est pas possible avec le schéma YPI fourni. La raison principale est que les sources de données intégrées dans YPI (BGPKIT, CAIDA, IHR, PeeringDB, etc.) sont axées sur la topologie du routage, les relations de peering, les dépendances de transit, la sécurité du routage (RPKI, MANRS) et les informations DNS.

Le schéma YPI ne contient pas de données qui qualifieraient l'état d'un service sur un serveur, comme la présence ou la validité d'un certificat TLS/SSL. Pour déterminer si un serveur est "sécurisé" au sens de cet indicateur, il faudrait des informations provenant de projets de scan à l'échelle d'Internet (par exemple, Shodan, Censys, ou des analyses de certificats) qui ne font pas partie des sources de données YPI décrites.

Tenter de créer des requêtes pour cet indicateur serait hautement spéculatif et ne produirait pas de résultats fiables. Par exemple, savoir qu'un domaine populaire est résolu vers une adresse IP dans un pays ne nous dit rien sur la configuration sécurisée du serveur web opérant sur cette adresse IP.

***Note :*** *Cet indicateur est très proche de "Adoption de HTTPS". Si les données pour ce dernier indicateur étaient disponibles dans YPI (par exemple, via Cloudflare Radar, au-delà de ce qui est décrit dans le schéma), on pourrait l'utiliser comme un proxy. Cependant, en l'état actuel du schéma fourni, l'analyse directe des "serveurs sécurisés" n'est pas réalisable.*