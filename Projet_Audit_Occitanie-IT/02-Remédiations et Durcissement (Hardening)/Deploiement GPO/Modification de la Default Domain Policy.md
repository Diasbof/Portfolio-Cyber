# Modification de la Default Domain Policy (Mots de passe)

> [!NOTE]
> **Contexte**
> 
> Lors de l'audit initial (PingCastle), la politique de mots de passe par défaut du domaine a été identifiée comme une vulnérabilité critique (mots de passe faibles autorisés, < 8 caractères). Pour élever le niveau de sécurité global de l'infrastructure de manière uniforme, la stratégie de sécurité de base du domaine a été durcie.

> [!NOTE]
> **Cible de Déploiement**
> 
> Contrairement aux GPO classiques qui ciblent des Unités d'Organisation (OU) spécifiques, la stratégie des mots de passe des comptes de l'annuaire doit impérativement être configurée au niveau de la racine du domaine via la **Default Domain Policy**.

## 1. Durcissement de la Stratégie de Mot de Passe

La modification est réalisée depuis la console de Gestion de stratégie de groupe (`gpmc.msc`) sur le contrôleur de domaine (WIN-479952UTUH2).

1. Édition de la GPO existante : **Default Domain Policy**.
2. Navigation vers le chemin de sécurité :
`Configuration ordinateur -> Stratégies -> Paramètres Windows -> Paramètres de sécurité -> Stratégies de comptes -> Stratégie de mot de passe`

**Paramètres appliqués :**
* **Longueur minimale du mot de passe :** Fixée à `14 caractères` (recommandation ANSSI).
* **Le mot de passe doit respecter des exigences de complexité :** `Activé` (impose l'utilisation de majuscules, minuscules, chiffres et caractères spéciaux).
* **Conserver l'historique des mots de passe :** `24` mots de passe mémorisés (empêche la réutilisation cyclique d'un même mot de passe).

## 2. Vérification de l'application

Pour valider que la nouvelle politique est bien active sur le domaine, la commande suivante peut être exécutée dans un invite de commande :

```cmd
net accounts
```

Le retour de la commande confirmera que la longueur minimale est bien passée à 14.

## 3. Analyse des Risques (Le point de vue du Défenseur)

Un mot de passe de 8 caractères (même complexe) peut aujourd'hui être cassé en quelques heures, voire quelques minutes, grâce à des attaques par force brute ou par dictionnaire optimisées par la puissance des cartes graphiques (GPU).

En imposant une longueur minimale de **14 caractères**, l'entropie du mot de passe augmente de manière exponentielle. Le temps nécessaire pour casser un tel condensat (Hash NTLM) hors-ligne devient irréaliste (plusieurs siècles avec la technologie actuelle), rendant les attaques par force brute inopérantes. 

> [!TIP]
> **Sensibilisation Utilisateur**
> 
> Pour accompagner ce changement technique, il est recommandé aux utilisateurs de ne plus penser en termes de "Mot de passe" mais de **"Phrase de passe"** 
> (ex: *MonChatAimeLePoissonRouge!*), beaucoup plus facile à mémoriser et mathématiquement plus robuste.

> [!NOTE]
> **Documents liés**
> 
> - [Analyse PingCastle](Analyse%20PingCastle.md) — Vulnérabilité initiale identifiée.
> - [Matrice de Remediation](Matrice%20de%20Remediation.md) — Validation de la ligne d'action REM-05.
