> [!NOTE] 
> **Contexte** 
> 
> Évaluation du niveau de sécurité du domaine via l'outil PingCastle. Cet utilitaire audite la configuration de l'Active Directory (Windows Server 2019) et génère un score de risque basé sur les vulnérabilités détectées. Les résultats de cette analyse serviront de feuille de route pour le déploiement des GPO de remédiation.

> [!NOTE] 
> **Cible de l'audit**
> 
> |**Rôle**|**Serveur**|**OS**|
> |---|---|---|
> |Contrôleur de Domaine|SRV-AD01|Windows Server 2019|

## 1. Exécution de l'audit

L'outil est exécuté depuis le poste d'audit (membre du domaine) avec un compte utilisateur standard, afin de cartographier les informations accessibles publiquement sur le réseau.

DOS

```
REM Lancement interactif de PingCastle
PingCastle.exe

REM Sélectionner l'option 1 : Healthcheck
```

Le livrable généré est un fichier de rapport au format HTML (ex: `ad_hc_fsec_lan.html`).

## 2. Analyse du Score de Risque

PingCastle attribue un score de risque global calculé sur 100. Plus le score est élevé, plus l'infrastructure est vulnérable.

> [!WARNING] 
> **Lecture du rapport**
> 
> Le rapport classe les risques en 4 grandes catégories : Privileged Accounts (Comptes à privilèges), Trusts (Approbations), Anomalies, et Stale Objects (Objets obsolètes). Pour cette phase de certification, la priorité de traitement est donnée aux "Anomalies" présentant un risque de compromission directe.

## 3. Principales Vulnérabilités Identifiées

Voici l'extraction des vulnérabilités critiques et majeures remontées par le rapport, qui feront l'objet d'une correction immédiate :

| **ID Règle** | **Vulnérabilité (Anomalie)**            | **Criticité** | **Impact de Sécurité**                                                                      | **Remédiation Prévue**                         |
| ------------ | --------------------------------------- | ------------- | ------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| A-01         | **Spooler Service activé sur le DC**    | Critique      | Risque de compromission totale du contrôleur de domaine (Faille PrintNightmare).            | Désactivation du service via GPO.              |
| A-02         | **Protocoles LLMNR / NBT-NS actifs**    | Haute         | Permet l'interception d'identifiants sur le réseau local (Poisoning / Responder).           | Désactivation via GPO.                         |
| A-03         | **Absence de LAPS**                     | Haute         | Mots de passe administrateurs locaux identiques sur les postes. Mouvement latéral facilité. | Déploiement de la solution LAPS.               |
| P-01         | **Mots de passe qui n'expirent jamais** | Moyenne       | Persistance d'accès pour un attaquant ayant compromis un compte utilisateur.                | Stratégie FGPP (Fine-Grained Password Policy). |

## 4. Exploitation (Point de vue du Pentester)

Pour justifier techniquement la nécessité des remédiations, voici comment un attaquant exploite la faille liée aux protocoles LLMNR/NBT-NS (Règle A-02) :

1. L'attaquant se connecte au réseau local et écoute le trafic avec un outil comme `Responder`.
    
2. Un utilisateur tente d'accéder à un partage réseau inexistant ou mal orthographié (ex: `\\partage_fichers`).
    
3. Le serveur DNS ne trouvant pas la ressource, le poste client demande au réseau local (en broadcast via LLMNR/NBT-NS) si une machine possède ce nom.
    
4. L'attaquant répond frauduleusement, capture le hash NTLMv2 de l'utilisateur, et peut tenter de le casser hors-ligne ou de le relayer vers un autre serveur (Relay Attack).
    

> [!TIP]
> **Prochaine étape**
> 
> Les failles identifiées constituent le périmètre d'action strict pour la phase de sécurisation. Chaque ligne du tableau des vulnérabilités correspond désormais à une tâche d'administration à réaliser.

> [!NOTE]
>  **Pages liées**
> 
> - [[Methodologie Audit AD]] — Cadre global de l'évaluation.
>     
> - [[Matrice de Remediation]] — Suivi du plan d'action.
>     
> - [[Desactivation protocoles obsoletes]] — Procédure de correction pour la faille A-02.
>