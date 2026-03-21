# Portfolio de Certification : Gestion de la Cybersécurité d'une Infrastructure Active Directory

> [!NOTE]
> **Contexte Professionnel**
> 
> Ce dépôt rassemble les travaux techniques réalisés dans le cadre de la certification "Participer à la gestion de la cybersécurité". Le projet simule une intervention complète de consultant en cybersécurité sur une infrastructure Windows Server 2019 avec Active Directory.

## Présentation du Projet

L'objectif de cette mission est d'évaluer, de sécuriser, puis d'éprouver une infrastructure d'entreprise. La démarche suit un cycle complet de cybersécurité (Blue Team & Red Team) : **Évaluation** $\rightarrow$ **Remédiation** $\rightarrow$ **Surveillance** $\rightarrow$ **Pentest**.

### Stack Technique Utilisée

* **Systèmes :** Windows Server 2019, Windows 10, Debian (Wazuh Manager), Kali Linux (Attaquant).
* **Audit & Défense :** PingCastle, PowerShell (AD Module), GPO, Microsoft LAPS.
* **Supervision (Blue Team) :** SIEM/XDR Wazuh, MITRE ATT&CK Mapping, VirusTotal API.
* **Audit Offensif (Red Team) :** Nmap, Responder, Impacket (GetNPUsers, GetUserSPNs, SecretsDump), Hashcat / John The Ripper.

---

## Architecture de la Documentation

Le portfolio est structuré en quatre piliers majeurs, démontrant la maîtrise du maintien en condition de sécurité et de l'évaluation des risques.

### 1. Audit et Conformité
Cette section documente la phase de découverte et l'analyse de la surface d'attaque initiale.
* Utilisation de PingCastle pour générer un score de risque.
* Synthèse des vulnérabilités prioritaires (Protocoles obsolètes, mauvaises délégations, mots de passe).
* Établissement d'une matrice de remédiation.

### 2. Remédiations et Durcissement (Hardening)
Mise en application concrète du principe de moindre privilège et sécurisation du système.
* **Modèle de Tiering et LAPS :** Gestion automatisée des mots de passe locaux.
* **Hygiène Réseau :** Désactivation de LLMNR, NBT-NS et SMBv1 via GPO.
* **Contrôle d'Accès :** Restriction RDP et mise en place de FGPP (Fine-Grained Password Policies).

### 3. Supervision et SIEM
Mise en place d'un maintien en condition de sécurité via une solution de détection et réponse.
* Déploiement centralisé du Manager Wazuh.
* Collecte des EventChannels de sécurité Windows.
* Création d'alertes personnalisées et blocage automatisé (Active Response).

### 4. Audit Offensif et Pentest
Validation technique des mesures de sécurité via un test d'intrusion en condition "Black-Box" (Méthodologie PTES).
* **Accès Initial :** Empoisonnement de flux (LLMNR/NBT-NS) et capture de hashs.
* **Attaques Kerberos :** Exploitation des comptes via AS-REP Roasting et Kerberoasting.
* **Post-Exploitation :** Prise de contrôle "Domain Admin" et exfiltration de la base `NTDS.dit` (DCSync).
* **Analyse de la Détection :** Corrélation des attaques avec les alertes remontées dans le SIEM Wazuh.

---

## Méthodologie Appliquée

> [!IMPORTANT]
> **Approche "Defense in Depth" et Réalisme**
> 
> La sécurité n'est pas traitée comme un produit, mais comme un processus continu. Les remédiations apportées ont été testées face à de véritables vecteurs d'attaque pour valider la robustesse de l'Active Directory, le tout dans le strict respect du cadre légal (Loi Godfrain) et d'une approche de laboratoire cloisonnée.

---

## Navigation dans le Portfolio

| Dossier | Contenu |
| :--- | :--- |
| `01-Audit et Conformite` | Rapports initiaux et plans d'actions de remédiation. |
| `02-Windows Server et Remediations` | Procédures techniques de durcissement GPO et LAPS. |
| `03-Supervision et SIEM` | Configuration du SIEM, détection d'incidents et réponse active. |
| `04-Audit Offensif et Pentest` | Démarche d'intrusion (PTES), exploitation de vulnérabilités et matrice des risques. |