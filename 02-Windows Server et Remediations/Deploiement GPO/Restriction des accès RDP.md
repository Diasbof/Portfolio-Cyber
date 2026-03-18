# Restriction des accès RDP

> [!NOTE] 
> **Contexte**
> 
> L'audit a révélé que les accès via le protocole RDP (Remote Desktop Protocol) n'étaient pas techniquement restreints (Vulnérabilité REM-04). Par défaut, le groupe "Administrateurs" local autorise l'accès RDP. Ce document détaille la mise en place de stratégies de groupe (GPO) pour verrouiller ces accès, interdisant formellement aux comptes à hauts privilèges (Tier 0) de s'exposer sur des machines de niveau inférieur (Tier 1 et Tier 2).

> [!NOTE] 
> **Matrice des Autorisations RDP (Tiering)**
> 
> |**Cible (OU)**|**Groupe Autorisé (Allow)**|**Groupes Interdits (Deny)**|
> |---|---|---|
> |**Domain Controllers** (Tier 0)|`Admins du domaine`|`Utilisateurs du domaine`|
> |**Serveurs** (Tier 1)|`GRP-Admins-Serveurs`|`Admins du domaine`, `Utilisateurs du domaine`|
> |**Postes-Clients** (Tier 2)|`GRP-Admins-Postes`|`Admins du domaine`, `GRP-Admins-Serveurs`|

## 1. Création des Stratégies de Groupe (GPO)

Pour appliquer cette matrice, des GPO spécifiques sont créées et liées à chaque Unité d'Organisation correspondante. L'objectif est d'utiliser le paramètre "Attribution des droits utilisateur" (User Rights Assignment).

**Exemple de configuration pour l'OU `Serveurs` (GPO : `Securite-RDP-Serveurs`) :**

1. Ouvrir l'éditeur de GPO et naviguer vers :
    
    `Configuration ordinateur` $\rightarrow$ `Stratégies` $\rightarrow$ `Paramètres Windows` $\rightarrow$ `Paramètres de sécurité` $\rightarrow$ `Stratégies locales` $\rightarrow$ `Attribution des droits utilisateur`
    
2. Configurer **Autoriser l'ouverture de session par les services Bureau à distance** :
    
    - Ajouter le groupe : `fsec\GRP-Admins-Serveurs`
        
3. Configurer **Interdire l'ouverture de session par les services Bureau à distance** :
    
    - Ajouter les groupes : `fsec\Admins du domaine`, `fsec\Utilisateurs du domaine`
        

_(Cette logique est répliquée avec les groupes correspondants pour les OU `Domain Controllers` et `Postes-Clients`)_.

> [!WARNING] 
> **Règle de priorité Windows**
> 
> Dans l'architecture Windows, un droit "Interdire" (Deny) prend toujours le pas sur un droit "Autoriser" (Allow). En cas de conflit d'appartenance à un groupe, l'utilisateur sera bloqué.

## 2. Durcissement du Pare-feu Windows (GPO Complémentaire)

Restreindre qui peut se connecter est essentiel, mais restreindre depuis où la connexion est initiée ajoute une couche de défense supplémentaire (Défense en profondeur).

Dans la même GPO, le flux réseau du port 3389 (RDP) est filtré :

- Naviguer vers : `Configuration ordinateur` $\rightarrow$ `Stratégies` $\rightarrow$ `Paramètres Windows` $\rightarrow$ `Paramètres de sécurité` $\rightarrow$ `Pare-feu Windows Defender avec fonctions avancées`
    
- Règle entrante : Autoriser le port TCP 3389 **uniquement** depuis les adresses IP du sous-réseau d'administration (VLAN_ADM) ou du serveur de rebond.
    

## 3. Analyse des Risques (Le point de vue du Défenseur)

L'absence de restriction RDP est la cause principale de la compromission totale d'un annuaire lors d'une cyberattaque.

**Explication de l'attaque contrecarrée :** Si un "Administrateur du domaine" (Tier 0) utilise le RDP pour se connecter à un simple poste client (Tier 2) afin de dépanner un utilisateur, ses identifiants et son ticket Kerberos (ou son hash NTLM) restent stockés dans la mémoire RAM du poste client (processus LSASS).

Si ce poste client est déjà compromis par un attaquant, ce dernier peut extraire ces informations de la mémoire (via l'outil Mimikatz) et récupérer les privilèges suprêmes du domaine.

En interdisant techniquement (Deny RDP Logon) la connexion des comptes Tier 0 sur les Tiers inférieurs, on élimine totalement ce vecteur de vol d'identifiants à hauts privilèges.

> [!TIP] 
> **Résultat final**
> 
> Le modèle de Tiering n'est plus seulement théorique, il est techniquement forcé. Les mouvements latéraux via le protocole RDP sont désormais impossibles hors des limites définies par le principe de moindre privilège.

> [!NOTE] 
> **Documents liés**
> 
> - [[Gestion des Groupes et Moindre Privilège]] — Groupes de sécurité utilisés dans cette GPO.
>     
> - [[Matrice de Remediation]] — Validation du plan d'action (REM-04).
>