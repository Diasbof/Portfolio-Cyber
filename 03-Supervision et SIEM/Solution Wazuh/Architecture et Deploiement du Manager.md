> [!NOTE] 
> **Contexte**
> 
> Suite à l'audit et au durcissement de l'infrastructure Active Directory, il est impératif de mettre en place une solution de supervision continue. Wazuh a été sélectionné comme plateforme SIEM et XDR (Extended Detection and Response). Ce document détaille le déploiement du serveur central (Manager), qui aura pour rôle de collecter, d'indexer et d'analyser les journaux d'événements (logs) de l'ensemble du parc informatique.

> [!NOTE] 
> **Architecture de Déploiement (All-in-One)**
> 
> Pour cette infrastructure, un déploiement centralisé (All-in-One) a été privilégié. Le même serveur héberge le Manager (analyse), l'Indexer (stockage) et le Dashboard (interface visuelle).
> 
> |**Rôle**|**Nom d'hôte**|**OS**|**IP**|
> |---|---|---|---|
> |Serveur SIEM central|SRV-WAZUH|Linux Debian 11 (ou Ubuntu 22.04)|10.10.20.100|

## 1. Prérequis Système et Matrice des Flux Réseau

Avant l'installation, les ressources matérielles de la machine virtuelle ont été ajustées (minimum 4 vCPU et 8 Go de RAM) et les règles de pare-feu réseau ont été configurées pour permettre la communication avec les futurs agents.

|**Port**|**Protocole**|**Source**|**Destination**|**Usage**|
|---|---|---|---|---|
|**443**|TCP|VLAN Administration|SRV-WAZUH|Accès à l'interface web (Dashboard).|
|**1514**|TCP|Toutes zones (Agents)|SRV-WAZUH|Remontée des logs (Communication Agent-Manager).|
|**1515**|TCP|Toutes zones (Agents)|SRV-WAZUH|Enrôlement des nouveaux agents (Inscription).|

## 2. Processus d'Installation (Installation Assistant)

Le déploiement est réalisé en ligne de commande (CLI) directement sur le serveur Linux, en utilisant le script d'automatisation officiel de Wazuh, qui garantit la configuration des certificats de sécurité internes.

Bash

```
# 1. Mise à jour des dépôts du système
sudo apt-get update && sudo apt-get upgrade -y

# 2. Téléchargement de l'assistant d'installation
curl -sO https://packages.wazuh.com/4.x/wazuh-install.sh

# 3. Exécution du script en mode "All-in-One" (-a)
sudo bash wazuh-install.sh -a
```

À la fin de l'exécution, le script génère les identifiants d'accès administrateur par défaut, qui doivent être extraits et stockés de manière sécurisée (par exemple, dans un gestionnaire de mots de passe type KeePass ou Vaultwarden).

Bash

```
# Commande pour retrouver les mots de passe générés si nécessaire
sudo tar -O -xvf wazuh-install-files.tar wazuh-install-files/wazuh-passwords.txt
```

## 3. Configuration Initiale et Accès au Tableau de Bord

Une fois l'installation terminée, la plateforme est accessible via un navigateur web.

1. Connexion à l'adresse : `https://10.10.20.100`
    
2. Authentification avec l'utilisateur `admin` et le mot de passe généré.
    
3. **Mesure de sécurité immédiate :** Remplacement du mot de passe par défaut par un mot de passe complexe respectant la politique de sécurité (via l'onglet _Security_ $\rightarrow$ _Internal users_).
    

## 4. Objectif Défensif (Le point de vue du Défenseur)

Un serveur Windows Server 2019 génère nativement des milliers de journaux d'événements (Event Logs) par jour. Sans outil centralisé, il est humainement impossible de détecter une tentative d'intrusion subtile (comme la création discrète d'un compte caché ou une élévation de privilèges).

Le Manager Wazuh agit comme le "cerveau" de l'infrastructure de défense. Il ne se contente pas de stocker les logs : il les corrèle en temps réel avec des bases de données de menaces mondiales (Threat Intelligence) et avec la matrice **MITRE ATT&CK**, permettant de transformer une ligne de log illisible en une alerte de sécurité claire et exploitable.

> [!TIP] 
> **Bilan du Déploiement**
> 
> L'infrastructure de supervision centrale est en ligne, sécurisée et prête à recevoir les données. La prochaine étape consiste à déployer l'agent de collecte sur les cibles du réseau.

> [!NOTE] 
> **Documents liés**
> 
> - [[Deploiement des Agents Windows via GPO]] — Étape suivante : connecter le parc au Manager.
>