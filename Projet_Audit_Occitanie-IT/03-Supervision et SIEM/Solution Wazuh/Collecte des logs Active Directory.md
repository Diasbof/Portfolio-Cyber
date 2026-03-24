# Collecte des logs Active Directory


> [!NOTE]
> **Contexte**
> 
> Le serveur central Wazuh étant opérationnel, l'objectif est désormais de remonter les événements de sécurité spécifiques du contrôleur de domaine (WIN-479952UTUH2). Par défaut, Windows Server génère un volume massif de journaux. Cette configuration vise à cibler précisément les événements liés à l'authentification, à la gestion des comptes (IAM) et aux modifications des stratégies de groupe, afin de détecter toute compromission de l'Active Directory.

> [!NOTE]
> **Architecture de Collecte**
> 
> | Source des logs | Canal (EventChannel) | Destination | Format de transmission |
> | :--- | :--- | :--- | :--- |
> | WIN-479952UTUH2 (DC01) | Security | Manager Wazuh | JSON (via l'agent local) |
> | WIN-479952UTUH2 (DC01) | System | Manager Wazuh | JSON |

## 1. Durcissement de la Stratégie d'Audit (GPO)

L'Active Directory ne journalise pas nativement toutes les actions critiques. Avant de configurer l'agent Wazuh, une stratégie de groupe nommée `Securite-Audit-Avance` est déployée sur l'OU `Domain Controllers` pour forcer la génération des événements nécessaires.

**Chemin dans l'éditeur de stratégie :**

`Configuration ordinateur -> Stratégies -> Paramètres Windows -> Paramètres de sécurité -> Stratégie d'audit avancée`

**Paramètres activés (Succès et Échec) :**

- _Ouverture de session/Fermeture de session :_ Audit de l'ouverture de session (Logon).
    
- _Gestion des comptes :_ Audit de la gestion des groupes de sécurité et des comptes d'utilisateurs.
    
- _Accès aux objets :_ Audit du service d'annuaire (Modifications AD).
    
- _Suivi des stratégies :_ Audit des modifications de stratégie (Modifications GPO).
    

## 2. Configuration de l'Agent Wazuh (ossec.conf)

Une fois les journaux générés par Windows, l'agent Wazuh installé sur le contrôleur de domaine doit être instruit de les lire et de les transmettre au Manager. Cette configuration s'effectue dans le fichier `C:\Program Files (x86)\ossec-agent\ossec.conf`.

Le bloc `<localfile>` est ajouté ou vérifié pour utiliser le format natif `EventChannel` de Windows, garantissant une remontée structurée et performante :

```XML
<localfile>
  <location>Security</location>
  <log_format>eventchannel</log_format>
  <query>Event/System[EventID != 5145 and EventID != 5156]</query>
</localfile>

<localfile>
  <location>System</location>
  <log_format>eventchannel</log_format>
  <query>Event/System[EventID=104 or EventID=105]</query>
</localfile>
```

_(Note technique : L'utilisation de balises `<query>` permet de filtrer le bruit à la source en excluant les ID d'événements trop bavards et non pertinents pour la sécurité, économisant ainsi la bande passante et l'espace de stockage du SIEM)._

## 3. Matrice des Événements Critiques Surveillés

La configuration mise en place permet désormais au SIEM d'indexer les identifiants d'événements (Event ID) suivants, essentiels pour la détection des menaces :

|**Event ID (Windows)**|**Description de l'action**|**Signification en Cybersécurité**|
|---|---|---|
|**4624 / 4625**|Ouverture de session (Succès / Échec)|Détection de force brute ou d'accès illégitime.|
|**4720**|Création d'un compte utilisateur|Création potentielle d'un compte de persistance (Backdoor).|
|**4728 / 4732**|Ajout d'un membre à un groupe de sécurité|Élévation de privilèges (ex: ajout d'un compte aux "Admins du domaine").|
|**4738**|Modification d'un compte utilisateur|Altération des droits ou réinitialisation d'un mot de passe par un attaquant.|

## 4. Analyse des Risques (Le point de vue du Défenseur)

Le recueil des logs via l'EventChannel est la pierre angulaire de la réaction à incident (DFIR).

Un attaquant qui parvient à contourner les protections initiales (via un 0-day ou un vol d'identifiant valide) cherchera immédiatement à élever ses privilèges et à maintenir son accès. Par exemple, s'il ajoute discrètement un compte compromis au groupe `Admins du domaine` (Event ID 4728), l'absence de journalisation centralisée lui garantirait l'invisibilité.

Grâce à cette collecte ciblée, le Manager Wazuh dispose de la matière première nécessaire pour déclencher une alerte instantanée, réduisant le temps de détection (MTTD - Mean Time To Detect) de plusieurs mois à quelques secondes.

> [!TIP] 
> **Résultat final**
> 
> Les journaux d'événements critiques de l'Active Directory sont audités localement et transmis en continu, de manière chiffrée, au serveur Wazuh. Le SIEM dispose désormais de la visibilité requise sur l'identité et les accès du réseau.

> [!NOTE] 
> **Documents liés**
> 
> - [[Architecture et Déploiement du Manager]] — Serveur central réceptionnant ces logs.
>     
> - [[Alertes personnalisées et Réponse Active]] — Étape suivante : traduire ces logs en notifications de sécurité actives.
>