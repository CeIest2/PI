// Analyse l'infrastructure d'hébergement pour un nom de domaine donné.
// PARAMETRES : $domainName (ex: 'service-public.fr'), $countryCode (ex: 'FR').
MATCH (d:DomainName {name: $domainName})
// Trouve les IPs vers lesquelles le domaine se résout
MATCH (d)-[:RESOLVES_TO]->(ip:IP)
// Trouve le préfixe et l'AS d'origine
MATCH (p:Prefix)-[:HAS_IP]->(ip)
MATCH (hostingAS:AS)-[:ORIGINATE]->(p)
// Récupère les informations sur l'AS d'hébergement (nom, pays)
OPTIONAL MATCH (hostingAS)-[:NAME]->(n:Name)
OPTIONAL MATCH (hostingAS)-[:COUNTRY]->(hostingCountry:Country)
RETURN DISTINCT
       hostingAS.asn AS hostingASN,
       n.name AS hostingASName,
       hostingCountry.country_code AS hostingASCountry,
       // Compare le pays de l'AS au pays analysé
       (hostingCountry.country_code = $countryCode) AS isHostedLocally
LIMIT 10;