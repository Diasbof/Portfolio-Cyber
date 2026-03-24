# Surveillance d'Intégrité (FIM) et Intégration VirusTotal

> [!NOTE]
> **Contexte**
> 
> Le module Syscheck de Wazuh permet de réaliser une surveillance d'intégrité des fichiers (FIM - File Integrity Monitoring). Ce document détaille la configuration mise en place sur le contrôleur de domaine (WIN-479952UTUH2) pour surveiller un répertoire critique simulé contenant des données sensibles. L'objectif est de détecter toute altération de données et d'automatiser l'analyse de fichiers suspects via l'API VirusTotal.

> [!NOTE]
> **Périmètre de Surveillance**
> 
> | Cible | OS | Chemin Critique |
> | :--- | :--- | :--- |
> | WIN-479952UTUH2 (DC01) | Windows Server 2019 | `C:\DossierSecret` |

## 1. Configuration du File Integrity Monitoring (FIM)

Afin de valider la capacité de détection sur les ressources sensibles, un répertoire critique simulé a été créé sur le Contrôleur de Domaine (`C:\DossierSecret`).

L'agent Wazuh installé sur le serveur Windows a été configuré pour surveiller ce dossier spécifique. L'attribut `realtime="yes"` garantit qu'une alerte est générée à la seconde où un fichier est créé, modifié ou supprimé.

**Extrait de la configuration de l'agent (`ossec.conf`) :**

```
<syscheck>
  <directories check_all="yes" realtime="yes">C:\DossierSecret</directories>
  <disabled>no</disabled>
</syscheck>
```

Cette configuration permet de générer des événements critiques tels que le **Rule ID 550** (Fichier modifié) ou le **Rule ID 553** (Fichier supprimé).

## 2. Intégration de l'API VirusTotal

Pour qu'une alerte FIM prenne tout son sens en cas d'intrusion, le SIEM ne doit pas se contenter de signaler la création d'un fichier : il doit en évaluer la dangerosité.

Le Manager Wazuh (serveur Linux) a donc été interconnecté avec l'API de VirusTotal. À chaque fois que le module FIM détecte un nouveau fichier, le Manager extrait son condensat (Hash) et l'envoie à l'API pour vérification.

**Extrait de la configuration du Manager (`ossec.conf`) :**

```
<integration>
  <name>virustotal</name>
  <api_key>VOTRE_CLE_API_VIRUSTOTAL</api_key>
  <group>syscheck</group>
  <alert_format>json</alert_format>
</integration>
```

_(Note : La clé API réelle a été masquée pour des raisons de sécurité)._

## 3. Validation de la chaîne de détection (Test EICAR)

Pour certifier le bon fonctionnement de ce couplage sans introduire de véritable malware sur le réseau de production, un test standardisé a été réalisé.

1. **Action :** Création d'un fichier texte nommé `virus_test.txt` contenant la signature de test inoffensive **EICAR** dans le répertoire surveillé.

2. **Détection FIM :** L'agent repère immédiatement la création du fichier.

3. **Analyse VirusTotal :** Le Manager interroge l'API qui reconnaît la signature EICAR.

4. **Résultat :** Le système classe instantanément l'événement comme "Malicious", confirmant la capacité de qualification des menaces en temps réel.


> [!IMPORTANT] **Valeur ajoutée pour l'entreprise**
> 
> Cette configuration fait passer le SIEM d'un simple outil de journalisation à une plateforme de détection avancée. Occitanie-IT dispose désormais d'une levée de doute automatisée sur les fichiers suspects, réduisant drastiquement le temps de réaction face à une attaque par Ransomware ou un dépôt de charge malveillante.