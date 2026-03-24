# Gestion des Groupes et Moindre Privilège

> [!NOTE]
> **Contexte**
> 
> À la suite de l'audit de sécurité (PingCastle), une gestion permissive des droits élevés a été constatée (comptes sensibles exposés à la délégation, groupes critiques non surveillés). Ce document détaille les actions correctives menées pour assainir les groupes d'administration et appliquer le principe du moindre privilège, afin d'empêcher les élévations de privilèges et le vol de tickets (Kerberoasting).

## 1. Assainissement des Groupes Critiques

L'audit a révélé que l'hygiène des comptes d'administration n'était pas respectée. Certains comptes possédaient des droits permanents inutiles sur des groupes à très hauts privilèges.

Pour réduire la surface d'attaque, un nettoyage des groupes natifs a été opéré. Par exemple, le compte `Administrateur` a été retiré du groupe **Admins du schéma** (Schema Admins), ce groupe ne devant être utilisé que ponctuellement lors de modifications structurelles profondes de la forêt Active Directory.

```powershell
# Retrait de l'utilisateur Administrateur du groupe Admins du schéma
Remove-ADGroupMember -Identity "Admins du schéma" -Members "Administrateur" -Confirm:$false
```

## 2. Sécurisation via le groupe "Protected Users"

Pour prévenir le vol de session et la compromission d'identifiants en mémoire (Pass-the-Hash, extraction de tickets type Silver Ticket), les comptes administrateurs ont été intégrés au groupe de sécurité natif **Protected Users**.



```Powershell
# Ajout du compte Administrateur au groupe Protected Users
Add-ADGroupMember -Identity "Protected Users" -Members Administrateur
```

L'appartenance à ce groupe applique immédiatement des règles de sécurité strictes et non contournables à ces comptes sensibles :

- Désactivation de l'authentification NTLM (forçage de Kerberos).
    
- Interdiction de mettre les identifiants en cache (empêche les attaques si l'admin se connecte sur un poste client compromis).
    
- Impossibilité de déléguer les identifiants de ce compte.


>[!TIP]
> **Bilan de Sécurisation IAM**
> 
> L'hygiène des comptes à privilèges a été restaurée. Les comptes sensibles sont désormais protégés par le groupe `Protected Users` et la surface d'attaque liée aux groupes critiques a été réduite au strict minimum. La prochaine étape consiste à déployer la rotation automatique des mots de passe pour les administrateurs locaux via LAPS.

> [!NOTE]
> **Documents liés**
> 
> - [Déploiement AD DS Windows Server 2019](Déploiement%20AD%20DS%20Windows%20Server%202019.md) — Architecture des Unités d'Organisation.
> - [Restriction des accès RDP](../Deploiement%20GPO/Restriction%20des%20accès%20RDP.md) — GPO verrouillant les accès aux serveurs.
> - [Déploiement LAPS](../Deploiement%20GPO/Déploiement%20LAPS.md) — Gestion des comptes administrateurs locaux.
