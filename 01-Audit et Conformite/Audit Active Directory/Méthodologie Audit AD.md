# Méthodologie Audit AD

> [!NOTE] 
> **Contexte**
> 
> Ce document définit le cadre méthodologique de l'audit de sécurité réalisé sur l'infrastructure Active Directory. Cette intervention s'inscrit dans les travaux d'évaluation pour le certificat de compétences professionnelles "Participer à la gestion de la cybersécurité". L'objectif est d'évaluer le niveau de sécurité d'un environnement Windows Server 2019, d'identifier les vulnérabilités de configuration, d'appliquer les remédiations nécessaires, et de préparer le terrain pour un maintien en condition de sécurité via le déploiement de Wazuh.

> [!NOTE] 
> **Périmètre Technique**
> 
> |**Machine**|**OS**|**Rôle dans l'audit**|
> |---|---|---|
> |SRV-AD01|Windows Server 2019|Cible (Contrôleur de domaine principal)|
> |Poste-Audit|Windows 10 / Linux|Exécution des outils d'analyse|

## 1. Objectifs de l'audit

L'analyse de l'environnement Active Directory vise à contrôler plusieurs points critiques de l'infrastructure :

- **Gestion des identités et des accès :** Vérification de la politique de mots de passe et de l'hygiène des comptes privilégiés.

- **Sécurité des configurations (GPO) :** Identification des stratégies obsolètes ou dangereuses (mots de passe en clair, partages non sécurisés).

- **Analyse des chemins de compromission :** Détection des mauvaises délégations de droits permettant une élévation de privilèges.

- **Protocoles réseau :** Détection des protocoles vulnérables actifs (LLMNR, NBT-NS, SMBv1).


## 2. Outils de diagnostic et de collecte

Afin de réaliser une évaluation standardisée et reconnue, les outils suivants sont utilisés depuis le poste d'audit connecté au domaine :

- **PingCastle :** Outil principal pour évaluer le niveau de risque de l'Active Directory, générer une cartographie des anomalies et fournir un score de santé.

- **Scripts PowerShell natifs (Module ActiveDirectory) :** Pour l'extraction manuelle d'informations spécifiques (comptes inactifs, groupes locaux).


## 3. Déroulement des opérations

### Phase de collecte (Mode non-intrusif)

L'audit est réalisé avec un compte utilisateur standard du domaine, démontrant la quantité d'informations accessibles sans privilèges administratifs (principe de l'assume breach).

PowerShell

```
REM Exemple de lancement de PingCastle depuis le poste d'audit
PingCastle.exe --healthcheck --server 10.10.10.10
```

### Phase d'analyse

Le rapport HTML généré est décortiqué pour classer les vulnérabilités selon leur impact (Score CVSS / Matrice MITRE ATT&CK) et leur facilité d'exploitation.

## 4. Livrables et plan de traitement

À l'issue de l'exécution de cette méthodologie, les résultats sont consolidés pour préparer la phase de sécurisation.

> [!TIP] 
> **Résultat attendu**
> 
> - Un état des lieux clair de la surface d'attaque du serveur Windows 2019.
>     
> - Une priorisation des failles critiques à traiter en urgence.
>     
> - L'établissement d'une feuille de route pour les remédiations (GPO, LAPS, désactivation de protocoles).
>     

> [!NOTE] 
> **Documents liés**
> 
> - [[Analyse PingCastle]] — Rapport détaillé des vulnérabilités découvertes.
>     
> - [[Synthèse des Vulnérabilités]] — Classification et criticité.
>     
> - [[Matrice de Remediation]] — Plan d'action des corrections à déployer.
>