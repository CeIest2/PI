// Trouve les réseaux internationaux les mieux classés présents sur les IXP d'un pays.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'SN', 'FR', 'JP').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(ixp:IXP)
// Trouve un membre qui n'est PAS du pays en question.
MATCH (foreign_as:AS)-[:MEMBER_OF]->(ixp)
WHERE NOT (foreign_as)-[:COUNTRY]->(c)
// Récupère son classement CAIDA pour mesurer son importance.
MATCH (foreign_as)-[r:RANK]->(:Ranking {name:'CAIDA ASRank'})
OPTIONAL MATCH (foreign_as)-[:NAME]->(as_name:Name)
RETURN  foreign_as.asn AS asn,
        as_name.name AS asName,
        toInteger(r.rank) AS caidaRank,
        collect(DISTINCT ixp.ix_id) as ix_ids //PeeringDB IX-ID
ORDER BY caidaRank ASC
LIMIT 15;