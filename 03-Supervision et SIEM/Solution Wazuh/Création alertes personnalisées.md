# Création alertes personnalisées

> [!NOTE] 
> **Contexte**
> 
> Bien que Wazuh dispose d'un vaste ensemble de règles par défaut (basées sur Sigma et MITRE ATT&CK), une supervision efficace nécessite la création de règles spécifiques au contexte de l'entreprise. Ce document détaille la procédure de création d'une règle personnalisée visant à détecter instantanément toute modification suspecte des groupes à hauts privilèges de l'Active Directory (notamment le groupe "Admins du domaine", de niveau Tier 0).

> [!NOTE] 
> **Cible de Détection**
> 
> |**Scénario de Menace**|**Source**|**Event ID (Windows)**|**Niveau d'Alerte Wazuh**|
> |---|---|---|---|
> |Élévation de privilèges illégitime|SRV-AD01|4728 / 4732|12 (Critique)|

## 1. Comprendre la structure des règles Wazuh

Le moteur d'analyse de Wazuh fonctionne en deux étapes :

1. **Le Décodeur (Decoder) :** Il extrait les champs pertinents du journal brut (IP source, nom d'utilisateur, ID de l'événement). Pour les logs Windows au format JSON (`EventChannel`), le décodage est natif.
    
2. **La Règle (Rule) :** Elle évalue les champs extraits à l'aide d'expressions régulières (Regex) ou de correspondances exactes pour déterminer s'il y a une anomalie, et déclenche une alerte le cas échéant.
    

## 2. Création de la Règle Personnalisée (local_rules.xml)

Pour ne pas altérer les règles système qui sont écrasées lors des mises à jour, la règle personnalisée est ajoutée sur le serveur Wazuh (`SRV-WAZUH`) dans le fichier dédié aux configurations locales : `/var/ossec/etc/rules/local_rules.xml`.

L'objectif de cette règle est d'intercepter l'événement d'ajout à un groupe (Event ID 4728) et de filtrer spécifiquement si la cible est le groupe `Admins du domaine`.

XML

```
<group name="windows, active_directory, custom_alerts,">
  
  <rule id="100001" level="12">
    <if_sid>60106</if_sid> <field name="win.system.eventID">^4728$</field>
    <field name="win.eventdata.targetUserName">^Admins du domaine$</field>
    <description>ALERTE CRITIQUE : L'utilisateur $(win.eventdata.memberUid) a ete ajoute au groupe Tier 0 (Admins du domaine) par $(win.eventdata.subjectUserName).</description>
    <mitre>
      <id>T1098</id> </mitre>
    <group>privilege_escalation, gdpr_IV_35.7.d,</group>
  </rule>

</group>
```

_(Note : L'utilisation des variables de type `$(nom_du_champ)` permet d'afficher dynamiquement le nom de l'attaquant et de la cible directement dans le titre de l'alerte, facilitant ainsi le travail de l'analyste SOC)._

## 3. Application et Tests de Validation

Une fois le fichier sauvegardé, le service du Manager doit être redémarré pour compiler les nouvelles règles.

Bash

```
# Redémarrage du service Wazuh Manager
sudo systemctl restart wazuh-manager
```

**Procédure de test (Simulation d'attaque) :**

1. Sur le contrôleur de domaine (`SRV-AD01`), ouvrir la console _Utilisateurs et ordinateurs Active Directory_.
    
2. Créer un utilisateur fictif nommé `hacker_test`.
    
3. Ajouter `hacker_test` au groupe `Admins du domaine`.
    
4. Vérifier immédiatement le tableau de bord (Dashboard) Wazuh sous la section _Security events_.
    

## 4. Exploitation et Réponse à Incident (Le point de vue du Défenseur)

Le groupe "Admins du domaine" détient les clés de l'ensemble de l'infrastructure. Dans un environnement de production sain appliquant le modèle de Tiering, l'ajout d'un membre à ce groupe est un événement rarissime qui doit faire l'objet d'une procédure de validation stricte (Change Management).

Si cette alerte (Niveau 12 - Critique) se déclenche en dehors d'une fenêtre de maintenance planifiée, le centre d'opérations de sécurité (SOC) doit considérer qu'une compromission de type "Élévation de privilèges" (Privilege Escalation) est en cours.

L'action immédiate de remédiation consistera à isoler le poste source identifié dans l'alerte (`$(win.eventdata.subjectUserName)`) et à désactiver le compte nouvellement promu.

> [!TIP] 
> **Résultat final**
> 
> Le SIEM n'est plus un simple puits de logs passif. Il est désormais configuré pour rechercher activement des tactiques de compromission spécifiques à l'environnement Active Directory. La boucle de sécurité (Audit $\rightarrow$ Remédiation $\rightarrow$ Supervision) est bouclée.

> [!NOTE] 
> **Documents liés**
> 
> - [[Collecte des logs Active Directory]] — Prérequis : configuration de l'EventChannel sur le serveur cible.
>     
> - [[Gestion des Groupes et Moindre Privilège]] — Documentation justifiant la criticité du groupe "Admins du domaine".
>