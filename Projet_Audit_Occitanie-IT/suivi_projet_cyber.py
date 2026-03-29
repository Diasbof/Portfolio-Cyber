import json
import os

# Nom du fichier pour sauvegarder l'avancement localement
FICHIER_SAUVEGARDE = "suivi_projet_cyber.json"

# La liste des tâches structurée d'après votre audit et remédiation
TACHES_INITIALES = {
    "Phase 1 : Audit et Conformité": [
        {"nom": "Déploiement de l'environnement", "details": "Serveur Windows 2019 et Kali Linux", "statut": False},
        {"nom": "Création de l'architecture AD", "details": "OU spécifiques (Serveurs, Postes, Utilisateurs)", "statut": False},
        {"nom": "Audit PingCastle", "details": "Analyse de l'Active Directory et score de risque", "statut": False},
        {"nom": "Automatisation PowerShell", "details": "Script de détection des comptes inactifs", "statut": False}
    ],
    "Phase 2 : Remédiations et Durcissement": [
        {"nom": "Désactivation protocoles réseau", "details": "GPO : LLMNR, NBT-NS, SMBv1", "statut": False},
        {"nom": "Déploiement Microsoft LAPS", "details": "Rotation des mots de passe admin locaux", "statut": False},
        {"nom": "Restriction des accès RDP", "details": "GPO : Application du moindre privilège", "statut": False},
        {"nom": "Durcissement mots de passe", "details": "Default Domain Policy (14 caractères min)", "statut": False},
        {"nom": "Sécurisation des groupes critiques", "details": "Nettoyage et utilisation de Protected Users", "statut": False}
    ],
    "Phase 3 : Supervision et SIEM": [
        {"nom": "Déploiement Manager Wazuh", "details": "Installation centrale sur Debian 11", "statut": False},
        {"nom": "Déploiement Agents Windows", "details": "Installation silencieuse via script de démarrage GPO", "statut": False},
        {"nom": "Audit avancé AD", "details": "Collecte EventChannel (Event ID 4624, 4625, 4720, etc.)", "statut": False},
        {"nom": "Intégration FIM & VirusTotal", "details": "Détection d'altération et analyse de hashs", "statut": False},
        {"nom": "Active Response", "details": "Blocage IP dynamique via netsh sur alerte RDP", "statut": False}
    ],
    "Phase 4 : Audit Offensif (Pentest)": [
        {"nom": "Reconnaissance et Scan", "details": "Nmap : Détection OS et ports (53, 389, 88, 445)", "statut": False},
        {"nom": "Empoisonnement réseau", "details": "Responder : Capture NTLMv2", "statut": False},
        {"nom": "Exploitation Kerberos", "details": "AS-REP Roasting et Kerberoasting (Impacket)", "statut": False},
        {"nom": "Élévation et Post-Exploitation", "details": "Attaque DCSync (exfiltration NTDS.dit)", "statut": False},
        {"nom": "Validation Blue Team", "details": "Corrélation des alertes dans le dashboard Wazuh", "statut": False}
    ]
}

def charger_donnees():
    """Charge les données depuis le fichier JSON ou retourne la liste initiale."""
    if os.path.exists(FICHIER_SAUVEGARDE):
        try:
            with open(FICHIER_SAUVEGARDE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("\n[ERREUR] Fichier de sauvegarde corrompu. Chargement des valeurs par défaut.")
            return TACHES_INITIALES
    else:
        return TACHES_INITIALES

def sauvegarder_donnees(donnees):
    """Sauvegarde l'état actuel dans un fichier JSON."""
    with open(FICHIER_SAUVEGARDE, 'w', encoding='utf-8') as f:
        json.dump(donnees, f, indent=4, ensure_ascii=False)
    print(f"\n[INFO] Progression sauvegardée avec succès.")

def afficher_taches(donnees):
    """Affiche toutes les tâches formatées de manière lisible."""
    print("\n" + "="*70)
    print(" SUIVI DES TÂCHES : GESTION DE LA CYBERSÉCURITÉ (OCCITANIE-IT) ")
    print("="*70)
    
    index_global = 1
    mapping_index = {} # Dictionnaire pour retrouver la tâche via son numéro
    
    for categorie, liste_taches in donnees.items():
        print(f"\n--- {categorie.upper()} ---")
        for tache in liste_taches:
            etat = "[X]" if tache['statut'] else "[ ]"
            details = f" ({tache['details']})" if tache['details'] else ""
            print(f"  {index_global:02d}. {etat} {tache['nom']}{details}")
            
            # Sauvegarde de la référence
            mapping_index[index_global] = (categorie, tache)
            index_global += 1
            
    return mapping_index

def basculer_statut(donnees, mapping, choix):
    """Change le statut d'une tâche (Fait <-> Non fait)."""
    if choix in mapping:
        categorie, tache = mapping[choix]
        tache['statut'] = not tache['statut'] # Inverse le booléen
        nouveau_statut = "Terminée" if tache['statut'] else "À faire"
        print(f"\n[OK] Tâche '{tache['nom']}' mise à jour -> {nouveau_statut}.")
        sauvegarder_donnees(donnees)
    else:
        print("\n[ERREUR] Numéro invalide. Veuillez choisir un numéro dans la liste.")

def main():
    donnees = charger_donnees()
    
    while True:
        mapping = afficher_taches(donnees)
        
        print("\nOptions :")
        print("  - Entrez le numéro de la tâche pour modifier son statut (ex: 1)")
        print("  - Tapez 'q' pour quitter l'application")
        
        choix_user = input("\nVotre choix : ").strip().lower()
        
        if choix_user == 'q':
            print("\nFermeture du script. À bientôt !")
            break
        elif choix_user.isdigit():
            basculer_statut(donnees, mapping, int(choix_user))
        else:
            print("\n[ERREUR] Entrée non reconnue. Veuillez entrer un numéro ou 'q'.")

if __name__ == "__main__":
    main()