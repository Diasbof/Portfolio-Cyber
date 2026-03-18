# Stratégie de Mots de Passe fine FGPP

> [!NOTE] 
> **Contexte**
> 
> L'audit PingCastle a relevé une politique de mots de passe globale insuffisante pour protéger les comptes critiques (Vulnérabilité REM-05). Dans un annuaire Active Directory, il n'est possible de définir qu'une seule stratégie de mot de passe par défaut via GPO pour l'ensemble du domaine. Pour imposer des règles beaucoup plus strictes aux administrateurs sans pénaliser les utilisateurs standards, la fonctionnalité FGPP (Fine-Grained Password Policy) est déployée.

> [!NOTE] 
> **Cibles et Exigences de Sécurité**
> 
> |**Groupe Cible**|**Longueur minimale**|**Complexité**|**Expiration**|**Verrouillage (Lockout)**|
> |---|---|---|---|---|
> |`Admins du domaine` (Tier 0)|16 caractères|Requise|90 jours|3 échecs (30 min)|
> |`GRP-Admins-Serveurs` (Tier 1)|16 caractères|Requise|90 jours|3 échecs (30 min)|
> |`Utilisateurs du domaine`|12 caractères|Requise|180 jours|5 échecs (15 min) _(GPO par défaut)_|

## 1. Création de l'objet PSO (Password Settings Object)

Contrairement aux stratégies classiques, les FGPP ne se configurent pas via l'éditeur de GPO standard, mais directement dans la base de données Active Directory via le Centre d'administration Active Directory (ADAC) ou PowerShell.

L'approche par script est privilégiée pour assurer la traçabilité du déploiement. Sur le contrôleur de domaine (`SRV-AD01`), la commande suivante est exécutée en tant qu'administrateur :

PowerShell

```
REM Création de la stratégie stricte pour les administrateurs
New-ADFineGrainedPasswordPolicy -Name "FGPP-Admins-Tier0-Tier1" `
    -Precedence 10 `
    -ComplexityEnabled $true `
    -Description "Politique de mots de passe renforcee pour les comptes a privileges" `
    -DisplayName "FGPP Admins" `
    -LockoutDuration "00:30:00" `
    -LockoutObservationWindow "00:15:00" `
    -LockoutThreshold 3 `
    -MaxPasswordAge "90.00:00:00" `
    -MinPasswordAge "1.00:00:00" `
    -MinPasswordLength 16 `
    -PasswordHistoryCount 24 `
    -ReversibleEncryptionEnabled $false
```

_(Note : La précédence de 10 assure que cette stratégie s'appliquera en priorité si un utilisateur est soumis à plusieurs FGPP. Le chiffre le plus bas l'emporte)._

## 2. Application de la stratégie aux groupes de sécurité

Une fois l'objet PSO créé, il doit être lié aux groupes d'utilisateurs concernés. Il est fortement déconseillé de lier une FGPP directement à des utilisateurs individuels pour des raisons de maintenabilité.

PowerShell

```
REM Application de la FGPP aux groupes de niveau Tier 0 et Tier 1
Add-ADFineGrainedPasswordPolicySubject -Identity "FGPP-Admins-Tier0-Tier1" -Subjects "Admins du domaine", "GRP-Admins-Serveurs"
```

## 3. Vérification des stratégies effectives

Pour valider que la stratégie prend bien le pas sur la GPO du domaine par défaut (Default Domain Policy), il est possible d'interroger un compte administrateur spécifique.

PowerShell

```
REM Vérifier quelle politique de mot de passe s'applique réellement à l'utilisateur Administrateur
Get-ADUserResultantPasswordPolicy -Identity "Administrateur"
```

_Le résultat doit retourner l'objet `FGPP-Admins-Tier0-Tier1`._

## 4. Analyse des Risques et Défense en Profondeur

L'application d'une FGPP répond directement à la menace des attaques par force brute (Brute-force) et par pulvérisation de mots de passe (Password Spraying).

En exigeant 16 caractères minimum pour les comptes à privilèges, le temps de cassage hors-ligne d'un hash NTLM intercepté devient mathématiquement irréalisable avec les capacités de calcul actuelles. De plus, le seuil de verrouillage strict (3 échecs) neutralise les tentatives de devinette en ligne sur les services exposés (comme un VPN ou un portail d'administration).

> [!TIP] 
> **Résultat final**
> 
> Les comptes critiques du domaine sont désormais protégés par une politique d'authentification robuste, indépendante des contraintes imposées aux utilisateurs standards. La phase de remédiation des failles système et réseau est officiellement achevée.

> [!NOTE] 
> **Documents liés**
> 
> - [[Matrice de Remediation]] — Validation de l'action REM-05.
>     
> - [[Gestion des Groupes et Moindre Privilège]] — Groupes cibles de cette stratégie.
>