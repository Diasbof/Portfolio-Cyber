# Portfolio : Gestion de la Cybersécurité d'une Infrastructure Active Directory

Ce projet documente une intervention complète de sécurisation sur une infrastructure Windows Server 2019 intégrant Active Directory. Réalisé dans le cadre de la certification "Participer à la gestion de la cybersécurité" , ce travail illustre l'application d'un cycle complet de défense en profondeur (Blue Team) éprouvé par des tests d'intrusion ciblés (Red Team).

## Environnement Technique

- **Systèmes d'exploitation :** Windows Server 2019 (Cible), Windows 10, Debian 11 (Serveur SIEM), Kali Linux (Machine d'audit).
    
- **Audit et Administration :** PingCastle, PowerShell (Module Active Directory), Stratégies de Groupe (GPO), Microsoft LAPS.
    
- **Supervision (Blue Team) :** SIEM/XDR Wazuh, API VirusTotal.
    
- **Sécurité Offensive (Red Team) :** Nmap, Responder, Impacket, Hashcat / John The Ripper.
    

---

## Architecture du Projet

### 1. Audit de Sécurité et Évaluation

La première phase a consisté à cartographier la dette technique et la surface d'attaque du domaine selon une approche non intrusive (White Box).

- Évaluation de l'infrastructure avec l'outil PingCastle pour identifier les configurations par défaut dangereuses.
    
- Identification de vulnérabilités critiques telles que l'autorisation de mots de passe faibles, l'activation du protocole SMBv1 sur le contrôleur de domaine, et l'exposition aux requêtes de diffusion via LLMNR/NBT-NS.
    

### 2. Remédiations et Durcissement (Hardening)

Suite à l'audit, un plan d'action a été déployé pour réduire drastiquement la surface d'attaque.

- Désactivation des protocoles réseaux obsolètes (SMBv1, LLMNR, NBT-NS) via le déploiement de stratégies de groupe (GPO).
    
- Implémentation de la solution Microsoft LAPS pour automatiser la rotation sécurisée des mots de passe administrateurs locaux sur l'ensemble du parc.
    
- Application du principe de moindre privilège par la restriction des accès RDP et le durcissement de la politique globale des mots de passe (longueur minimale de 14 caractères).
    

### 3. Supervision et Réponse aux Incidents (SIEM Wazuh)

Pour garantir un maintien en condition de sécurité, une solution de détection centralisée a été mise en œuvre.

- Déploiement d'un Manager Wazuh sous Linux et automatisation de l'installation des agents sur les hôtes Windows par GPO.
    
- Collecte et analyse des journaux d'événements (EventChannels) ciblant l'authentification et les modifications de l'Active Directory.
    
- Configuration de la surveillance d'intégrité des fichiers (FIM) couplée à l'API VirusTotal pour une qualification instantanée des charges malveillantes.
    
- Création de règles de détection personnalisées et d'une réponse active (Active Response) bloquant dynamiquement les adresses IP lors d'attaques par force brute sur le port RDP.
    

### 4. Test d'Intrusion (Pentest)

Afin de valider la robustesse des défenses mises en place, une simulation d'attaque en boîte noire (Black-Box) a été exécutée selon la méthodologie PTES.

- Accès initial obtenu par empoisonnement du trafic réseau avec l'outil Responder.
    
- Élévation de privilèges par l'exploitation de faiblesses d'authentification Kerberos (attaques AS-REP Roasting et Kerberoasting).
    
- Compromission du contrôleur de domaine démontrée par une attaque DCSync, permettant l'exfiltration de la base des secrets NTDS.dit.
    
- Corrélation finale entre les vecteurs d'attaque utilisés et les alertes générées dans le tableau de bord Wazuh.


## 🗺️ Architecture et Pipeline de Sécurité

<p align="center">
  <img src="Diagramme-OccitanieLAN.drawio%201.png" alt="Schéma de l'infrastructure et pipeline de sécurité" width="100%">
</p>