# Déploiement des Agents Windows via GPO

> [!NOTE]
> **Contexte**
> 
> Pour garantir une couverture globale de la supervision, l'agent Wazuh doit être installé sur l'ensemble des postes et serveurs membres du domaine `occitanie.lan`. Un déploiement manuel étant inenvisageable à l'échelle d'un parc, ce document détaille l'automatisation de l'installation silencieuse via une Stratégie de Groupe (GPO).

> [!NOTE]
> **Cibles de Déploiement**
> 
> | Cible (OU) | Périmètre d'application | Méthode |
> | :--- | :--- | :--- |
> | Serveurs | Serveurs membres du domaine | Script de démarrage (GPO) |
> | Postes Clients | Ensemble des postes de travail | Script de démarrage (GPO) |

## 1. Création du point de distribution réseau

Le programme d'installation (`.msi`) et le script de déploiement doivent être accessibles par toutes les machines cibles sur le réseau avant même l'ouverture de session d'un utilisateur.

Un partage réseau en lecture seule pour le groupe "Ordinateurs du domaine" est créé sur le contrôleur de domaine (WIN-479952UTUH2) :
`\\10.0.2.10\Deploiements$\Wazuh`

## 2. Script de Déploiement Silencieux (Batch)

Un script d'exécution (`deploy_wazuh.bat`) est placé dans ce partage. Il vérifie d'abord si le service Wazuh est déjà présent pour éviter les réinstallations en boucle à chaque redémarrage, puis lance l'installation en pointant vers le Manager Debian.

```batch
@echo off
Vérification de la présence du service Wazuh
sc query WazuhSvc >nul
if %errorlevel% equ 0 goto END

Installation silencieuse de l'agent
msiexec.exe /i "\\10.0.2.10\Deploiements$\Wazuh\wazuh-agent.msi" /q WAZUH_MANAGER="10.0.2.100" WAZUH_REGISTRATION_SERVER="10.0.2.100"

Démarrage du service
net start WazuhSvc

:END
exit
```

## 3. Configuration de la Stratégie de Groupe (GPO)

Une GPO nommée **Deploy-Agent-Wazuh** est créée et liée aux Unités d'Organisation `Serveurs` et `Postes Clients`.

Chemin de configuration dans l'éditeur de GPO :
`Configuration ordinateur -> Stratégies -> Paramètres Windows -> Scripts (démarrage/arrêt) -> Démarrage`

Le script réseau `deploy_wazuh.bat` y est renseigné. Ainsi, chaque ordinateur exécutera ce script avec les privilèges "Système" locaux lors de son amorçage.

## 4. Vérification du déploiement

Pour valider l'application de la GPO, un redémarrage est forcé sur un poste du domaine. Une fois le poste redémarré, la commande PowerShell suivante permet de vérifier que l'agent est bien opérationnel :

```powershell
Get-Service -Name WazuhSvc
```

_Le statut retourné doit indiquer "Running"._

> [!NOTE] 
> **Architecture de Collecte** 
Le parc de machines du domaine `occitanie.lan` est désormais sous supervision automatisée et continue. Les agents communiquent activement avec le Manager, permettant de centraliser les journaux d'événements et de détecter les comportements suspects.