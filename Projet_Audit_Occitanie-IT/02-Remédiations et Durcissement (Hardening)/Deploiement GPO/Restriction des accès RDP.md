# Restriction des accès RDP

> [!NOTE]
> **Contexte**
> 
> L'audit réseau (Pentest) a révélé que les accès via le protocole RDP (Remote Desktop Protocol) n'étaient pas techniquement restreints sur l'infrastructure. Par défaut, l'accès à distance est trop permissif. Ce document détaille la mise en place de stratégies de groupe (GPO) pour verrouiller ces accès, interdisant formellement aux comptes à hauts privilèges de s'exposer sur des machines de production standards (ce qui favoriserait le vol de session).

> [!NOTE]
> **Matrice des Autorisations RDP (Moindre Privilège)**
> 
> | Cible (OU) | Groupe Autorisé (Allow) | Groupes Interdits (Deny) |
> | :--- | :--- | :--- |
> | Serveurs | Admins du domaine | Utilisateurs du domaine |
> | Postes Clients | Administrateurs locaux (LAPS) | Admins du domaine (Prévention vol de session) |
> 
## 1. Création des Stratégies de Groupe (GPO)

Pour appliquer cette matrice, des GPO spécifiques sont créées et liées à chaque Unité d'Organisation correspondante. L'objectif est d'utiliser le paramètre "Attribution des droits utilisateur" (User Rights Assignment).

**Exemple de configuration pour l'OU Serveurs (GPO : Securite-RDP-Serveurs) :**

1. Ouvrir l'éditeur de GPO et naviguer vers :
`Configuration ordinateur -> Stratégies -> Paramètres Windows -> Paramètres de sécurité -> Stratégies locales -> Attribution des droits utilisateur`

2. Configurer **Autoriser l'ouverture de session par les services Bureau à distance** :
   * Ajouter le groupe : `occitanie\Admins du domaine`

3. Configurer **Interdire l'ouverture de session par les services Bureau à distance** :
   * Ajouter le groupe : `occitanie\Utilisateurs du domaine`

*(Cette logique est répliquée et inversée pour l'OU Postes Clients : on y interdit la connexion des Admins du domaine pour protéger leurs identifiants).*

> [!WARNING]
> **Règle de priorité Windows**
> 
> Dans l'architecture Windows, un droit "Interdire" (Deny) prend toujours le pas sur un droit "Autoriser" (Allow). 
> En cas de conflit d'appartenance à un groupe, l'utilisateur sera bloqué.

## 2. Durcissement du Pare-feu Windows (GPO Complémentaire)

Restreindre *qui* peut se connecter est essentiel, mais restreindre *depuis où* la connexion est initiée ajoute une couche de défense supplémentaire (Défense en profondeur).

Dans la GPO, le flux réseau du port 3389 (RDP) est filtré :
* Naviguer vers : `Configuration ordinateur -> Stratégies -> Paramètres Windows -> Paramètres de sécurité -> Pare-feu Windows Defender avec fonctions avancées`
* Règle entrante : Autoriser le port TCP 3389 **uniquement** depuis l'adresse IP du poste d'administration dédié (Machine d'audit/Admin).

## 3. Analyse des Risques (Le point de vue du Défenseur)

L'absence de restriction RDP est l'une des causes principales de compromission totale d'un annuaire lors d'une attaque.

**Explication de l'attaque contrecarrée :** Si un "Administrateur du domaine" utilise le RDP pour se connecter à un simple poste client afin de dépanner un utilisateur, ses identifiants et son ticket Kerberos (ou son hash NTLM) restent stockés dans la mémoire RAM du poste client (processus LSASS). 

Si ce poste client est déjà compromis par un attaquant, ce dernier peut extraire ces informations de la mémoire (via un outil comme Mimikatz) et récupérer les privilèges suprêmes du domaine. En interdisant techniquement (Deny RDP Logon) la connexion des administrateurs globaux sur les postes standards, on élimine totalement ce vecteur de vol d'identifiants à hauts privilèges.

> [!TIP]
> **Résultat final**
> 
> Le principe de moindre privilège est désormais techniquement forcé. Les mouvements latéraux via le protocole RDP pour usurper des comptes à hauts privilèges sont bloqués.

> [!NOTE]
> **Documents liés**
> 
> - [Gestion des Groupes et Moindre Privilège](Gestion%20des%20Groupes%20et%20Moindre%20Privilège.md) — Groupes de sécurité utilisés dans cette GPO.
> - [Matrice de Remediation](Matrice%20de%20Remediation.md) — Validation du plan d'action.