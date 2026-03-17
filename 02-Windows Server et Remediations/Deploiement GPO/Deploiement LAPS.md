> [!INFO] Contexte
> 
> L'audit de sécurité a mis en évidence le partage d'un mot de passe administrateur local identique sur l'ensemble du parc informatique (Vulnérabilité REM-03). Ce document détaille l'implémentation de Microsoft LAPS pour générer, faire pivoter et stocker de manière sécurisée des mots de passe uniques pour chaque compte administrateur local directement dans l'Active Directory.

> [!NOTE] Architecture et Prérequis
> 
> |**Composant**|**Rôle**|**Cible**|
> |---|---|---|
> |Serveur d'Administration|Extension du schéma et gestion|SRV-AD01 (Tier 0)|
> |Agent LAPS (Client)|Application de la rotation|OU=Postes-Clients, OU=Serveurs|
> |Active Directory|Stockage sécurisé des mots de passe|Attribut `ms-Mcs-AdmPwd`|

## 1. Préparation de l'Active Directory (PowerShell)

Avant de déployer la stratégie, l'Active Directory doit être préparé pour accueillir les nouveaux attributs de mots de passe. Ces actions requièrent les privilèges d'Administrateur de l'Entreprise.

Depuis le contrôleur de domaine (SRV-AD01), dans une console PowerShell en tant qu'administrateur :

PowerShell

```
REM 1. Importation du module LAPS
Import-Module AdmPwd.PS

REM 2. Extension du schéma Active Directory
Update-AdmPwdADSchema

REM 3. Autoriser les ordinateurs à modifier leur propre mot de passe
Set-AdmPwdComputerSelfPermission -Identity "OU=Postes-Clients,DC=fsec,DC=lan"
Set-AdmPwdComputerSelfPermission -Identity "OU=Serveurs,DC=fsec,DC=lan"
```

## 2. Déploiement de l'Agent LAPS via GPO

L'agent LAPS (fichier `.msi`) doit être installé sur toutes les machines cibles. La méthodologie employée est similaire à celle utilisée pour le déploiement de l'agent GLPI.

1. Création d'un partage réseau sécurisé sur SRV-AD01 (ex: `\\10.10.20.10\Deploiement$\LAPS`).
    
2. Création d'une GPO nommée `Deploy-Agent-LAPS` liée aux OU `Postes-Clients` et `Serveurs`.
    
3. Dans la GPO : `Configuration ordinateur -> Stratégies -> Paramètres logiciels -> Installation de logiciel`.
    
4. Ajout du package `LAPS.x64.msi` en mode **Attribué**.
    

## 3. Configuration de la Stratégie de Sécurité LAPS

Une seconde GPO nommée `Securite-Configuration-LAPS` est créée pour définir les règles de rotation des mots de passe.

Chemin dans l'éditeur de stratégie :

`Configuration ordinateur -> Stratégies -> Modèles d'administration -> LAPS`

Paramètres appliqués :

- **Enable local admin password management :** Activé.
    
- **Password Settings :**
    
    - Complexité : Lettres majuscules, minuscules, chiffres, caractères spéciaux.
        
    - Longueur : 16 caractères.
        
    - Âge maximum : 30 jours.
        
- **Name of administrator account to manage :** `Administrateur` (ou le nom du compte local renommé si applicable).
    

## 4. Sécurisation de l'accès aux mots de passe (Moindre Privilège)

Par défaut, les utilisateurs ayant des droits étendus sur l'AD pourraient lire ces mots de passe en clair. Une restriction stricte des permissions de lecture (ACL) est donc configurée.

PowerShell

```
REM Retirer les droits de lecture étendus aux groupes non autorisés
Remove-AdmPwdExtendedRights -Identity "OU=Postes-Clients,DC=fsec,DC=lan" -Principals "Utilisateurs du domaine"

REM Autoriser uniquement le groupe dédié (Tier 2 Admins) à lire les mots de passe
Set-AdmPwdReadPasswordPermission -Identity "OU=Postes-Clients,DC=fsec,DC=lan" -AllowedPrincipals "GRP-Admins-Postes"
```

## 5. Analyse des Risques (Le point de vue du Défenseur)

L'absence de LAPS est une aubaine pour un attaquant. Sans cette solution, la compromission d'un seul poste de travail (par exemple via un phishing) permet d'extraire le condensat (hash) du mot de passe administrateur local depuis la base SAM.

Si ce mot de passe est identique sur tout le parc, l'attaquant utilise la technique du **Pass-the-Hash (PtH)** pour se connecter de proche en proche à toutes les machines du domaine (Mouvement Latéral), jusqu'à atteindre un serveur critique. LAPS casse cette chaîne d'attaque en rendant chaque hash unique et éphémère.

> [!SUCCESS] Vérification
> 
> L'administrateur autorisé peut désormais utiliser l'interface graphique `LAPS UI` ou la commande PowerShell `Get-AdmPwdPassword -ComputerName PC-CLIENT01` pour récupérer le mot de passe local en cas de besoin (ex: perte de la relation d'approbation avec le domaine).

> [!LINKS] Documents liés
> 
> - [[Matrice de Remediation]] — Validation de la correction REM-03.
>     
> - [[Gestion des Groupes et Moindre Privilege]] — Groupes autorisés à consulter les attributs LAPS.
>