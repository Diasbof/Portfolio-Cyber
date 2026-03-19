# Déploiement des Agents Windows via GPO

> [!NOTE] 
> **Contexte**
> 
> Le Manager Wazuh étant opérationnel, il est nécessaire de déployer l'agent de collecte sur l'ensemble du parc Windows (Serveurs et Postes Clients). Pour automatiser cette tâche et garantir que toute nouvelle machine jointe au domaine soit immédiatement supervisée, le déploiement est réalisé via une Stratégie de Groupe (GPO) couplée à un script d'installation silencieuse.

> [!NOTE] 
> **Architecture de Déploiement**
> 
> |**Machine**|**Rôle**|**IP**|
> |---|---|---|
> |SRV-AD01|Hébergement du partage caché `Application$`|10.10.20.10|
> |SRV-WAZUH|Manager SIEM (Cible de l'enrôlement)|10.10.20.100|
> |Postes du domaine|Cibles du déploiement|DHCP / Statique|

## 1. Préparation des sources d'installation

L'installeur MSI de l'agent Wazuh et le script de déploiement doivent être accessibles par tous les ordinateurs du domaine avant même l'ouverture de session d'un utilisateur.

1. Téléchargement de l'agent Wazuh Windows (`wazuh-agent.msi`) depuis le site officiel.
    
2. Placement du fichier MSI dans le partage sécurisé existant : `C:\Application$\Wazuh-Agent\`.
    
3. Création du script d'installation batch (`install_wazuh_agent.bat`) dans ce même dossier.
    

**Contenu du script `install_wazuh_agent.bat` :**

```DOS
@echo off
REM Verifie si l'agent Wazuh est deja installe
if exist "C:\Program Files (x86)\ossec-agent\win32ui.exe" (
    exit /b 0
)

REM Installation silencieuse avec pointage direct vers le Manager
msiexec.exe /i "\\10.10.20.10\Application$\Wazuh-Agent\wazuh-agent.msi" /q WAZUH_MANAGER="10.10.20.100" WAZUH_REGISTRATION_SERVER="10.10.20.100"

REM Log d'installation local
mkdir C:\Logs 2>nul
echo %date% %time% - Wazuh Agent installe >> C:\Logs\wazuh-agent-install.log

REM Demarrage du service
net start WazuhSvc
```

## 2. Création et Configuration de la GPO

Une nouvelle stratégie de groupe nommée `Deploy-Wazuh-Agent` est créée dans la console `gpmc.msc` et liée à la racine du domaine (`fsec.lan`) ou aux Unités d'Organisation cibles (`Serveurs` et `Postes-Clients`).

**Configuration du script de démarrage :**

1. Clic droit sur `Deploy-Wazuh-Agent` $\rightarrow$ **Modifier**.
    
2. Naviguer vers : `Configuration ordinateur` $\rightarrow$ `Stratégies` $\rightarrow$ `Paramètres Windows` $\rightarrow$ `Scripts (démarrage/arrêt)`.
    
3.Double-cliquer sur **Démarrage** $\rightarrow$ **Ajouter**.

4.Dans **Nom du script**, renseigner le chemin réseau absolu :

`\\10.10.20.10\Application$\Wazuh-Agent\install_wazuh_agent.bat`

5.Valider et fermer l'éditeur.


## 3. Vérification de l'Enrôlement

Pour valider le bon fonctionnement de la GPO, un redémarrage est forcé sur un poste client de test (`PC-CLIENT01`).

**Sur le poste client (Vérification locale) :**

```DOS
REM Le service est-il en cours d'exécution ?
sc query WazuhSvc

REM Le log d'installation confirme-t-il l'action ?
type C:\Logs\wazuh-agent-install.log
```

**Sur le Manager Wazuh (Vérification centralisée) :**

Depuis l'interface web (Dashboard) de Wazuh, naviguer dans la section **Agents**. Le nouveau poste client doit apparaître avec le statut `Active`, confirmant que la communication chiffrée sur le port 1514 TCP est établie.

## 4. Bénéfice de l'Automatisation (Le point de vue de l'Auditeur)

Dans le cadre d'un audit de sécurité, la couverture de la supervision est un critère déterminant. Déployer un agent manuellement comporte le risque d'oublier des machines (Shadow IT ou nouveaux déploiements).

En liant l'installation de l'agent de sécurité au processus d'amorçage même de l'Active Directory via GPO, l'infrastructure devient "Secure by Default". Toute machine intégrant le domaine est automatiquement contrainte de remonter ses journaux d'événements au SIEM, garantissant une visibilité totale et continue (Maintien en Condition de Sécurité).

> [!TIP] 
> **Résultat final**
> 
> Le parc informatique est intégralement supervisé. Le déploiement par script permet une mise à l'échelle immédiate sans intervention manuelle supplémentaire.

> [!NOTE] 
> **Documents liés**
> 
> - [[Architecture et Déploiement du Manager]] — Serveur de destination des agents.
>     
> - [[Collecte des logs Active Directory]] — Configuration spécifique poussée sur le contrôleur de domaine après l'installation de cet agent.
>