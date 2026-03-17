> [!INFO] Contexte
> 
> Ce document détaille l'architecture logique de l'annuaire Active Directory (AD DS) déployé sur Windows Server 2019. Cette infrastructure sert de socle au réseau d'entreprise simulé dans le cadre de la certification. L'installation a été pensée dès le départ pour faciliter la ségrégation des droits (modèle de Tiering) et l'application granulaire des stratégies de groupe (GPO) de sécurité.

> [!NOTE] Topologie du Domaine
> 
> |**Rôle**|**Nom d'hôte**|**IP (Statique)**|**Nom de Domaine**|
> |---|---|---|---|
> |Contrôleur de Domaine (PDC)|SRV-AD01|10.10.20.10|fsec.lan|
> |Serveur Membre (Applicatif)|SRV-GLPI|10.10.20.50|fsec.lan|

## 1. Prérequis et Configuration Initiale

Avant la promotion du serveur en contrôleur de domaine, les configurations systèmes suivantes ont été appliquées pour garantir la stabilité de l'annuaire :

- **Adressage IP statique :** Configuration de la carte réseau avec l'IP `10.10.20.10`.
    
- **DNS local :** Le serveur pointe vers lui-même (`127.0.0.1`) pour la résolution DNS primaire.
    
- **Nommage standardisé :** Renommage de la machine en `SRV-AD01` avant la jonction au domaine.
    

## 2. Structure Logique : Unités d'Organisation (OU)

Afin d'appliquer le principe de moindre privilège et de préparer les remédiations de sécurité, l'arborescence par défaut a été remplacée par une structure personnalisée. Cette ségrégation permet de ne pas mélanger les comptes administrateurs (Tier 0) avec les utilisateurs standards.

Plaintext

```
fsec.lan
│
├── OU=Administration (Tier 0 - Ressources Critiques)
│   ├── Comptes-Admins-Domaine
│   └── Groupes-Securite-Critiques
│
├── OU=Serveurs (Tier 1 - Serveurs d'infrastructure et applicatifs)
│   └── SRV-GLPI
│
├── OU=Postes-Clients (Tier 2 - Flotte bureautique)
│   ├── PC-CLIENT01
│   └── PC-CLIENT02
│
└── OU=Utilisateurs (Comptes standards)
    ├── Direction
    ├── Informatique
    └── Ressources-Humaines
```

### Avantages Sécurité de cette architecture :

1. **Ciblage GPO précis :** Il est possible d'appliquer une stratégie de sécurité très stricte (ex: blocage RDP) uniquement sur l'OU `Postes-Clients` sans impacter les `Serveurs`.
    
2. **Délégation de contrôle :** Possibilité de donner à un technicien le droit de réinitialiser les mots de passe uniquement dans l'OU `Utilisateurs`, sans qu'il n'ait d'impact sur l'OU `Administration`.
    

## 3. Déploiement Automatisé (Scripting)

Pour simuler un environnement d'entreprise réaliste de manière efficace, la création des arborescences, des groupes et des comptes utilisateurs a été scriptée via PowerShell, démontrant une capacité d'automatisation des tâches d'administration.

PowerShell

```
REM Exemple de création d'une OU via le module ActiveDirectory
New-ADOrganizationalUnit -Name "Postes-Clients" -Path "DC=fsec,DC=lan" -ProtectedFromAccidentalDeletion $true
```

> [!SUCCESS] Bilan du Déploiement
> 
> L'Active Directory est fonctionnel, les machines clientes sont jointes au domaine et la structure des OU est prête à recevoir les GPO correctives identifiées lors de la phase d'audit. La protection contre la suppression accidentelle a été activée sur toutes les OU critiques.

> [!LINKS] Documents liés
> 
> - [[Gestion des Groupes et Moindre Privilege]] — Détail des groupes de sécurité et délégations.
>     
> - [[Matrice de Remediation]] — Plan d'action des GPO à appliquer sur cette architecture.
>