> [!INFO] Contexte
> 
> À la suite de l'audit de sécurité, il a été constaté que la compromission d'un compte à privilèges constituait un risque majeur (mouvements latéraux et élévation de privilèges). Ce document détaille la refonte de la gestion des accès selon le principe du moindre privilège (Least Privilege) et l'implémentation du modèle de Tiering de Microsoft. L'objectif est de s'assurer qu'aucun administrateur de domaine ne se connecte sur une machine non sécurisée.

> [!NOTE] Modèle de Tiering (Ségrégation des privilèges)
> 
> L'infrastructure a été divisée en trois niveaux d'administration hermétiques :
> 
> |**Niveau**|**Périmètre technique**|**Groupes dédiés créés**|**Règle de sécurité stricte**|
> |---|---|---|---|
> |**Tier 0**|Contrôleurs de Domaine (DC), PKI|`Admins du domaine`|Interdiction de se connecter sur les Tier 1 et Tier 2.|
> |**Tier 1**|Serveurs membres (ex: SRV-GLPI)|`GRP-Admins-Serveurs`|Interdiction de se connecter sur le Tier 2.|
> |**Tier 2**|Postes de travail (ex: PC-CLIENT)|`GRP-Admins-Postes`|Limité à la gestion du parc bureautique.|

## 1. Implémentation des Groupes de Sécurité (RBAC)

Plutôt que d'attribuer des droits directement aux utilisateurs, une approche RBAC (Role-Based Access Control) a été déployée. Les utilisateurs sont membres de groupes globaux, eux-mêmes imbriqués dans des groupes locaux de domaine qui détiennent les permissions.

Groupes créés pour la gestion quotidienne :

- **`GRP-Helpdesk` :** Possède uniquement les droits de réinitialisation de mots de passe sur l'OU `Utilisateurs`.
    
- **`GRP-Lecteurs-Audit` :** Possède les droits de lecture sur les journaux d'événements des serveurs (préparation pour l'intégration Wazuh).
    

## 2. Délégation de Contrôle (Delegation of Control)

Afin d'éviter d'ajouter les techniciens support au groupe "Admins du domaine", l'Assistant de délégation de contrôle de l'Active Directory a été utilisé de manière granulaire.

**Exemple d'implémentation pour le groupe Helpdesk :**

1. Clic droit sur l'Unité d'Organisation `Utilisateurs` $\rightarrow$ **Délégation de contrôle**.
    
2. Ajout du groupe `GRP-Helpdesk`.
    
3. Sélection de la tâche personnalisée : _Réinitialiser les mots de passe des utilisateurs et forcer le changement au prochain d'ouverture de session_.
    

## 3. Sécurisation des Groupes Sensibles

Pour prévenir l'ajout non autorisé d'utilisateurs dans les groupes critiques (Admin du domaine, Admins de l'entreprise), une surveillance active des groupes natifs (Protected Users, Domain Admins) est mise en place.

PowerShell

```
REM Vérification régulière des membres du groupe Admins du domaine
Get-ADGroupMember -Identity "Admins du domaine" | Select-Object Name, objectClass
```

De plus, le groupe `Protected Users` natif de Windows Server a été exploité pour les comptes Tier 0, leur forçant l'utilisation de Kerberos (désactivation de NTLM) et empêchant la mise en cache de leurs identifiants.

> [!SUCCESS] Bilan de Sécurisation IAM
> 
> Le modèle de Tiering est logique et prêt à être renforcé techniquement. La prochaine étape consiste à déployer des Stratégies de Groupe (GPO) pour interdire matériellement (via les droits User Rights Assignment) la connexion interactive des comptes Tier 0 sur les machines Tier 1 et 2.

> [!LINKS] Documents liés
> 
> - [[Deploiement AD DS Windows Server 2019]] — Architecture des Unités d'Organisation.
>     
> - [[Restriction des acces RDP]] — GPO verrouillant techniquement ce modèle de Tiering.
>     
> - [[Deploiement LAPS]] — Gestion des comptes administrateurs locaux.
>