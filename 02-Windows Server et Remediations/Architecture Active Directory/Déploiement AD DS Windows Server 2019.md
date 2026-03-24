# Déploiement AD DS Windows Server 2019

> [!NOTE] 
> **Contexte**
> 
> Ce document détaille l'architecture logique de l'annuaire Active Directory (AD DS) déployé sur Windows Server 2019. Cette infrastructure sert de socle au réseau d'entreprise simulé dans le cadre de la certification. L'installation a été pensée dès le départ pour faciliter la ségrégation des objets (Serveurs, Postes, Utilisateurs) et l'application granulaire des stratégies de groupe (GPO) de sécurité.

| Rôle | Nom d'hôte | IP (Statique) | Nom de Domaine |
| :--- | :--- | :--- | :--- |
| Contrôleur de Domaine (DC01) | WIN-479952UTUH2 | 10.0.2.10 | occitanie.lan |
| Serveur de Bases de Données | Serveur SQL | (LAN) | occitanie.lan |

```mermaid
graph LR
    Root["Domaine : occitanie.lan"]
    Root --- GPO_Def["GPO : Default Domain Policy (Mots de passe 14 car.)"]
    
    Root --> OU_Serveurs["OU : Serveurs"]
    OU_Serveurs --- Note_Serv("DC01, Serveur SQL")
    OU_Serveurs --> GPO_SMB["GPO : SEC_Disable_SMB1 (Désactivation SMBv1)"]
    OU_Serveurs --> GPO_Audit["GPO : Stratégie d'Audit Avancée"]
    
    Root --> OU_Clients["OU : Postes Clients"]
    OU_Clients --- Note_LAN("Réseau LAN 10.0.2.0/24")
    OU_Clients --> GPO_LAPS["GPO : SEC_LAPS (Admin Local)"]
    
    Root --> OU_Users["OU : Utilisateurs"]
    OU_Users --- Note_Poles("Pôle SI, Dév, Services Supports")
    OU_Users --> Group_PU["Groupe Sécurité : Protected Users"]

    style Root fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style GPO_Def fill:#fff9c4,stroke:#fbc02d
    style GPO_SMB fill:#fff9c4,stroke:#fbc02d
    style GPO_Audit fill:#fff9c4,stroke:#fbc02d
    style GPO_LAPS fill:#fff9c4,stroke:#fbc02d
```
## 1. Prérequis et Configuration Initiale

Avant la promotion du serveur en contrôleur de domaine, les configurations systèmes suivantes ont été appliquées pour garantir la stabilité de l'annuaire :

- **Adressage IP statique :** Configuration de la carte réseau avec l'IP `10.0.2.10`.

- **DNS local :** Le serveur pointe vers lui-même (`127.0.0.1`) pour la résolution DNS primaire.

- **Nommage standardisé :** Renommage de la machine en `WIN-479952UTUH2` (rôle DC01) avant la promotion du domaine.

## 2. Structure Logique : Unités d'Organisation (OU)

Afin d'appliquer le principe de moindre privilège et de préparer les remédiations de sécurité, l'arborescence par défaut a été remplacée par une structure personnalisée en Unités d'Organisation (OU).

**Avantages Sécurité de cette architecture :**

1. **Ciblage GPO précis :** Il est possible d'appliquer une stratégie de sécurité très stricte (ex: blocage SMBv1) uniquement sur l'OU `Serveurs`, ou de déployer la rotation de mots de passe locaux (LAPS) uniquement sur l'OU `Postes Clients`.
2. **Isolement des privilèges :** Les utilisateurs standards, les équipes métiers (Développement) et le pôle SI sont séparés, ce qui permet de lier des stratégies de restrictions spécifiques sans impacter les administrateurs globaux (membres du groupe `Protected Users`).


