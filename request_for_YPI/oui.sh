#!/bin/bash

# ==============================================================================
# Script pour créer l'arborescence de dossiers et de fichiers pour l'analyse IRI
# ==============================================================================

echo "🚀 Démarrage de la création de la structure de dossiers pour l'analyse IRI..."
echo ""

# --- PILIER 1 : INFRASTRUCTURE ---
echo "🏗️  Création de la structure pour [INFRASTRUCTURE]..."
mkdir -p infrastructure/ecosysteme_fibre/portee_fibre_10km
touch infrastructure/ecosysteme_fibre/portee_fibre_10km/portee_fibre_10km.md
touch infrastructure/ecosysteme_fibre/portee_fibre_10km/{1,2,3}.cypher

mkdir -p infrastructure/connectivite_mobile/couverture_reseau
touch infrastructure/connectivite_mobile/couverture_reseau/couverture_reseau.md
touch infrastructure/connectivite_mobile/couverture_reseau/{1,2,3}.cypher

mkdir -p infrastructure/connectivite_mobile/allocation_spectre
touch infrastructure/connectivite_mobile/allocation_spectre/allocation_spectre.md
touch infrastructure/connectivite_mobile/allocation_spectre/{1,2,3}.cypher

mkdir -p infrastructure/infrastructure_habilitante/couverture_centres_donnees
touch infrastructure/infrastructure_habilitante/couverture_centres_donnees/couverture_centres_donnees.md
touch infrastructure/infrastructure_habilitante/couverture_centres_donnees/{1,2,3}.cypher

mkdir -p infrastructure/infrastructure_habilitante/couverture_ixp
touch infrastructure/infrastructure_habilitante/couverture_ixp/couverture_ixp.md
touch infrastructure/infrastructure_habilitante/couverture_ixp/{1,2,3}.cypher

# --- PILIER 2 : PRÉPARATION DU MARCHÉ ---
echo "📈 Création de la structure pour [PREPARATION DU MARCHE]..."
mkdir -p preparation_marche/localisation_trafic/nombre_de_domaines
touch preparation_marche/localisation_trafic/nombre_de_domaines/nombre_de_domaines.md
touch preparation_marche/localisation_trafic/nombre_de_domaines/{1,2,3}.cypher

mkdir -p preparation_marche/localisation_trafic/score_indice_egouvernement
touch preparation_marche/localisation_trafic/score_indice_egouvernement/score_indice_egouvernement.md
touch preparation_marche/localisation_trafic/score_indice_egouvernement/{1,2,3}.cypher

mkdir -p preparation_marche/localisation_trafic/efficacite_peering
touch preparation_marche/localisation_trafic/efficacite_peering/efficacite_peering.md
touch preparation_marche/localisation_trafic/efficacite_peering/{1,2,3}.cypher

mkdir -p preparation_marche/structure_marche/abordabilite
touch preparation_marche/structure_marche/abordabilite/abordabilite.md
touch preparation_marche/structure_marche/abordabilite/{1,2,3}.cypher

mkdir -p preparation_marche/structure_marche/diversite_fournisseurs_amont
touch preparation_marche/structure_marche/diversite_fournisseurs_amont/diversite_fournisseurs_amont.md
touch preparation_marche/structure_marche/diversite_fournisseurs_amont/{1,2,3}.cypher

mkdir -p preparation_marche/structure_marche/concurrence_marche
touch preparation_marche/structure_marche/concurrence_marche/concurrence_marche.md
touch preparation_marche/structure_marche/concurrence_marche/{1,2,3}.cypher

# --- PILIER 3 : PERFORMANCE ---
echo "⚡ Création de la structure pour [PERFORMANCE]..."
mkdir -p performance/reseaux_fixes/reactivite
touch performance/reseaux_fixes/reactivite/reactivite.md
touch performance/reseaux_fixes/reactivite/{1,2,3}.cypher

mkdir -p performance/reseaux_fixes/vitesses_upload_download
touch performance/reseaux_fixes/vitesses_upload_download/vitesses_upload_download.md
touch performance/reseaux_fixes/vitesses_upload_download/{1,2,3}.cypher

mkdir -p performance/reseaux_fixes/consistance
touch performance/reseaux_fixes/consistance/consistance.md
touch performance/reseaux_fixes/consistance/{1,2,3}.cypher

mkdir -p performance/reseaux_mobiles/reactivite
touch performance/reseaux_mobiles/reactivite/reactivite.md
touch performance/reseaux_mobiles/reactivite/{1,2,3}.cypher

mkdir -p performance/reseaux_mobiles/vitesses_upload_download
touch performance/reseaux_mobiles/vitesses_upload_download/vitesses_upload_download.md
touch performance/reseaux_mobiles/vitesses_upload_download/{1,2,3}.cypher

mkdir -p performance/reseaux_mobiles/consistance
touch performance/reseaux_mobiles/consistance/consistance.md
touch performance/reseaux_mobiles/consistance/{1,2,3}.cypher

# --- PILIER 4 : SÉCURITÉ ---
echo "🛡️  Création de la structure pour [SECURITE]..."
mkdir -p securite/technologies_habilitantes/adoption_https
touch securite/technologies_habilitantes/adoption_https/adoption_https.md
touch securite/technologies_habilitantes/adoption_https/{1,2,3}.cypher

mkdir -p securite/technologies_habilitantes/adoption_ipv6
touch securite/technologies_habilitantes/adoption_ipv6/adoption_ipv6.md
touch securite/technologies_habilitantes/adoption_ipv6/{1,2,3}.cypher

mkdir -p securite/securite_dns/adoption_dnssec
touch securite/securite_dns/adoption_dnssec/adoption_dnssec.md
touch securite/securite_dns/adoption_dnssec/{1,2,3}.cypher

mkdir -p securite/securite_dns/validation_dnssec
touch securite/securite_dns/validation_dnssec/validation_dnssec.md
touch securite/securite_dns/validation_dnssec/{1,2,3}.cypher

mkdir -p securite/hygiene_routage/score_manrs
touch securite/hygiene_routage/score_manrs/score_manrs.md
touch securite/hygiene_routage/score_manrs/{1,2,3}.cypher

mkdir -p securite/hygiene_routage/connexions_amont
touch securite/hygiene_routage/connexions_amont/connexions_amont.md
touch securite/hygiene_routage/connexions_amont/{1,2,3}.cypher

mkdir -p securite/menace_securite/protection_ddos
touch securite/menace_securite/protection_ddos/protection_ddos.md
touch securite/menace_securite/protection_ddos/{1,2,3}.cypher

mkdir -p securite/menace_securite/serveurs_internet_securises
touch securite/menace_securite/serveurs_internet_securises/serveurs_internet_securises.md
touch securite/menace_securite/serveurs_internet_securises/{1,2,3}.cypher

mkdir -p securite/menace_securite/score_indice_cybersecurite
touch securite/menace_securite/score_indice_cybersecurite/score_indice_cybersecurite.md
touch securite/menace_securite/score_indice_cybersecurite/{1,2,3}.cypher

echo ""
echo "✅  Terminé ! L'arborescence de votre dépôt est prête."