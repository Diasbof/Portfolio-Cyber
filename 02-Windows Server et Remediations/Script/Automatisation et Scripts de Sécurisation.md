# Automatisation et Scripts de Sécurisation

> [!NOTE]
> **Objectif**
> 
> L'industrialisation de la sécurité permet d'éviter les erreurs humaines et de garantir un déploiement homogène sur l'ensemble du parc. Ce document recense les scripts PowerShell utilisés pour le durcissement de l'infrastructure Occitanie-IT.

## 1. Désactivation des protocoles à risque (PowerShell)

Plutôt que de passer par l'interface graphique sur chaque serveur, ce script permet de désactiver les protocoles obsolètes (SMBv1) qui sont souvent le vecteur initial des ransomwares.

```powershell
# Désactivation de SMBv1
Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -NoRestart

# Vérification du statut de SMBv1
Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol
````

## 2. Audit des comptes inactifs

La sécurité passe aussi par le nettoyage. Ce script identifie les comptes utilisateurs qui ne se sont pas connectés depuis plus de 90 jours, afin de les désactiver.

```PowerShell
$90Days = (Get-Date).AddDays(-90)
Get-ADUser -Filter 'LastLogonDate -lt $90Days' -Properties LastLogonDate | 
Select-Object Name, LastLogonDate, Enabled | 
Export-Csv -Path "C:\Audit\ComptesInactifs.csv" -NoTypeInformation
```