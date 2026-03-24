# Déploiement LAPS

> [!NOTE] 
> **Contexte**
> 
> L'audit de sécurité a mis en évidence le partage d'un mot de passe administrateur local identique sur l'ensemble du parc informatique (Vulnérabilité REM-03). Ce document détaille l'implémentation de Microsoft LAPS pour générer, faire pivoter et stocker de manière sécurisée des mots de passe uniques pour chaque compte administrateur local directement dans l'Active Directory.

| Composant                | Rôle                                | Cible                          |
| :----------------------- | :---------------------------------- | :----------------------------- |
| Serveur d'Administration | Extension du schéma et gestion      | WIN-479952UTUH2 (DC01)         |
| Agent LAPS (Client)      | Application de la rotation          | OU=Postes Clients, OU=Serveurs |
| Active Directory         | Stockage sécurisé des mots de passe | Attribut `ms-Mcs-AdmPwd`       |
## 1. Préparation de l'Active Directory (PowerShell)

Avant de déployer la stratégie, l'Active Directory doit être préparé pour accueillir les nouveaux attributs de mots de passe. Depuis le contrôleur de domaine (WIN-479952UTUH2), dans une console PowerShell en tant qu'administrateur :

1. Importation du module LAPS:
```powershell
Import-Module AdmPwd.PS
```

2. Extension du schéma Active Directory (Ajout des attributs ms-Mcs-AdmPwd)
```powerShell
Update-AdmPwdADSchema
```
3. Autoriser les ordinateurs à modifier leur propre mot de passe:
```Powershell
Set-AdmPwdComputerSelfPermission -Identity "OU=Postes Clients,DC=occitanie,DC=lan"
Set-AdmPwdComputerSelfPermission -Identity "OU=Serveurs,DC=occitanie,DC=lan"
```
## 2. Déploiement de l'Agent LAPS via GPO

L'agent LAPS (fichier `.msi`) doit être installé sur toutes les machines cibles.

1. Création d'un partage réseau sécurisé sur le DC01 (ex: `\\10.0.2.10\Deploiements$\LAPS`).
    
2. Création d'une GPO nommée **`Stratégie SEC_LAPS`** liée aux OU cibles (Postes Clients et Serveurs).
    
3. Dans la GPO : `Configuration ordinateur -> Stratégies -> Paramètres logiciels -> Installation de logiciel`.
    
4. Ajout du package `LAPS.x64.msi` en mode **Attribué**

## 3. Configuration de la Stratégie de Sécurité LAPS

Cette même GPO **`Stratégie SEC_LAPS`** est utilisée pour définir les règles de rotation des mots de passe.

Chemin dans l'éditeur de stratégie :
`Configuration ordinateur -> Stratégies -> Modèles d'administration -> LAPS`

Paramètres appliqués (visibles sur le rapport d'audit) :
* **Enable local admin password management :** Activé.
* **Password Settings :** * Complexité : Lettres majuscules, minuscules, chiffres, caractères spéciaux.
  * Longueur : 14 caractères minimum.
  * Âge maximum : 30 jours.

## 4. Sécurisation de l'accès aux mots de passe (Moindre Privilège)

Par défaut, les utilisateurs ayant des droits étendus pourraient lire ces mots de passe en clair. Une restriction stricte des permissions de lecture (ACL) est donc configurée.

```powershell
REM Retirer les droits de lecture étendus aux groupes non autorisés
Remove-AdmPwdExtendedRights -Identity "OU=Postes Clients,DC=occitanie,DC=lan" -Principals "Utilisateurs du domaine"
````
## 5. Analyse des Risques (Le point de vue du Défenseur)

L'absence de LAPS est une aubaine pour un attaquant. Sans cette solution, la compromission d'un seul poste de travail (par exemple via un phishing) permet d'extraire le condensat (hash) du mot de passe administrateur local depuis la base SAM.

Si ce mot de passe est identique sur tout le parc, l'attaquant utilise la technique du **Pass-the-Hash (PtH)** pour se connecter de proche en proche à toutes les machines du domaine (Mouvement Latéral), jusqu'à atteindre un serveur critique. LAPS casse cette chaîne d'attaque en rendant chaque hash unique et éphémère.

> [!TIP] 
> **Vérification**
> 
> L'administrateur autorisé peut désormais utiliser l'interface graphique `LAPS UI` ou la commande PowerShell `Get-AdmPwdPassword -ComputerName PC-CLIENT01` pour récupérer le mot de passe local en cas de besoin (ex: perte de la relation d'approbation avec le domaine).

> [!NOTE]
>  > **Documents liés**
>  - [Matrice de Remediation](../../01-Audit%20et%20Conformite/Rapports%20et%20Plans%20d%20action/Matrice%20de%20Remediation.md) — Validation de la correction REM-03. 
>  - [Gestion des Groupes et Moindre Privilège](../Architecture%20Active%20Directory/Gestion%20des%20Groupes%20et%20Moindre%20Privilège.md) — Politique de restriction des comptes à privilèges.