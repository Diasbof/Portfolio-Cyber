# Matrice de Remediation

> [!NOTE] 
> **Contexte**
> 
> Ce document centralise le plan d'action de remédiation défini à l'issue de l'audit de l'infrastructure. Il a pour but de traduire chaque vulnérabilité identifiée (notamment via PingCastle) en une action technique concrète, mesurable et documentée. Le traitement de ces failles vise à élever le niveau de sécurité du domaine Windows Server 2019 en appliquant les principes de défense en profondeur et de moindre privilège.

> [!NOTE] 
> **Environnement d'application**
> 
> |**Cible**|**Périmètre d'application**|**Méthode de déploiement privilégiée**|
> |---|---|---|
> |SRV-AD01|Contrôleur de domaine (Tier 0)|GPO ciblant l'OU "Domain Controllers"|
> |Postes Clients / Serveurs Membres|Ensemble du domaine (Tier 1 & 2)|GPO ciblant l'OU racine ou groupes spécifiques|

## 1. Plan d'Action et Suivi des Remédiations

Le tableau ci-dessous répertorie les actions correctives par ordre de priorité. Les vulnérabilités critiques permettant une compromission directe de l'Active Directory sont traitées en premier.

|**ID**|**Vulnérabilité (Constat)**|**Niveau de Risque**|**Action de Remédiation (Solution technique)**|**Vecteur**|**Statut**|
|---|---|---|---|---|---|
|**REM-01**|Service Spooler actif sur le DC (PrintNightmare)|Critique|Désactivation du service "Spouleur d'impression" sur les contrôleurs de domaine.|GPO|⏳ À faire|
|**REM-02**|Résolution de noms multicast (LLMNR / NBT-NS)|Haute|Désactivation de LLMNR via stratégie locale et NBT-NS via les options DHCP/Carte réseau.|GPO|⏳ À faire|
|**REM-03**|Mots de passe Administrateur Local identiques|Haute|Installation et configuration de la solution Microsoft LAPS pour la rotation automatique.|GPO + MSI|⏳ À faire|
|**REM-04**|Accès RDP non restreint sur les serveurs|Moyenne|Limitation du groupe "Utilisateurs du Bureau à distance" aux seuls administrateurs autorisés.|GPO|⏳ À faire|
|**REM-05**|Politique de mots de passe globale insuffisante|Moyenne|Création d'une stratégie de mots de passe affinée (FGPP) pour les comptes à privilèges.|AD DS|⏳ À faire|

## 2. Méthodologie de Déploiement (Bonnes pratiques)

Afin d'éviter toute interruption de service lors de l'application de ces correctifs, la méthodologie suivante est appliquée pour chaque remédiation :

1. **Phase de Test :** Application de la GPO sur une Unité d'Organisation (OU) de test contenant une machine virtuelle représentative.
    
2. **Validation :** Vérification de la bonne application de la stratégie via la commande `gpresult /r` et test des processus métiers.
    
3. **Déploiement en Production :** Liaison de la GPO sur l'OU cible définitive.
    
4. **Documentation :** Rédaction de la fiche technique détaillant la configuration exacte.
    

> [!TIP] 
> **Objectif de Sécurisation**
> 
> La complétion de cette matrice permettra de réduire drastiquement la surface d'attaque interne. Une fois ces remédiations appliquées, l'infrastructure sera prête à accueillir le déploiement de l'agent Wazuh pour une supervision continue sur des bases saines.

> [!NOTE] 
> **Fiches techniques de déploiement**
> 
> Les détails d'implémentation de chaque ligne de cette matrice se trouvent dans les documents dédiés :
> 
> - [[Désactivation protocoles obsoletes]] _(Traite REM-01 et REM-02)_
>     
> - [[Déploiement LAPS]] _(Traite REM-03)_
>     
> - [[Restriction des accès RDP]] _(Traite REM-04)_
>     
> - [[Stratégie de Mots de Passe fine FGPP]] _(Traite REM-05)_
>