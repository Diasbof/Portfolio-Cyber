# Automatisation et Scripts de Sécurisation

> [!NOTE]
> **Contexte**
> 
> Afin de standardiser les actions d'administration et de supervision sur le domaine `occitanie.lan`, l'utilisation de scripts PowerShell a été privilégiée. L'automatisation permet d'industrialiser les tâches de sécurité sur le Contrôleur de Domaine, d'éviter les erreurs humaines et de garantir une traçabilité des déploiements.

## 1. Déploiement automatisé de l'Agent Wazuh (PowerShell)

Afin d'assurer la remontée des journaux d'événements vers le SIEM de manière uniforme, l'installation de l'agent sur les serveurs Windows est scriptée. Cela permet un déploiement rapide et sans interaction humaine (mode silencieux).

```powershell
# 1. Téléchargement de l'agent Wazuh (Version Windows)
Invoke-WebRequest -Uri "[https://packages.wazuh.com/4.x/windows/wazuh-agent.msi](https://packages.wazuh.com/4.x/windows/wazuh-agent.msi)" -OutFile "C:\Temp\wazuh-agent.msi"

# 2. Installation silencieuse avec pointage vers le Manager
# (L'adresse IP correspond au serveur hébergeant le SIEM Wazuh)
msiexec.exe /i C:\Temp\wazuh-agent.msi /q WAZUH_MANAGER="10.0.2.X"

# 3. Démarrage du service de supervision
Start-Service -Name "WazuhSvc"
```

## 2. Audit et désactivation des comptes inactifs

La gestion du cycle de vie des identités est cruciale. Les comptes utilisateurs inactifs depuis longtemps constituent des cibles de choix pour un attaquant souhaitant établir une persistance discrète. Ce script automatise la détection et la désactivation de ces comptes.

```Powershell
# Recherche des comptes inactifs depuis plus de 90 jours
$InactiveAccounts = Search-ADAccount -AccountInactive -TimeSpan 90:00:00 | Where-Object {$_.Enabled -eq $true}

# Désactivation automatique et journalisation
foreach ($Account in $InactiveAccounts) {
    Disable-ADAccount -Identity $Account.ObjectGUID
    Write-Host "Le compte $($Account.SamAccountName) a été désactivé par mesure de sécurité."
}
```

> [!TIP] **Industrialisation**
> 
> Ces scripts PowerShell ont vocation à être intégrés dans des tâches planifiées (Task Scheduler) ou des outils de déploiement centralisés pour assurer un maintien en condition de sécurité (MCS) continu sur l'ensemble de l'infrastructure.