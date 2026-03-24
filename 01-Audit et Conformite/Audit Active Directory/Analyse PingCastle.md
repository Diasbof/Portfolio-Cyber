# Analyse PingCastle

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


```
Lancement interactif de PingCastle
PingCastle.exe

Sélectionner l'option 1 : Healthcheck
```

Le livrable généré est un fichier de rapport au format HTML (ex: `ad_hc_fsec_lan.html`).

## 2. Analyse du Score de Risque

PingCastle attribue un score de risque global calculé sur 100. Lors de l'audit initial de l'infrastructure `occitanie.lan`, le domaine a obtenu un score de risque de **57/100**. Ce résultat positionne l'infrastructure dans une zone de vulnérabilité critique, confirmant que la configuration "par défaut" n'a jamais été durcie.

> [!WARNING] 
> **Lecture du rapport**
> 
> Le rapport classe les risques en 4 grandes catégories : Privileged Accounts (Comptes à privilèges), Trusts (Approbations), Anomalies, et Stale Objects (Objets obsolètes). Pour cette phase de certification, la priorité de traitement est donnée aux "Anomalies" présentant un risque de compromission directe.

## 3. Principales Vulnérabilités Identifiées

Voici l'extraction des vulnérabilités critiques et majeures remontées par le rapport, qui feront l'objet d'un plan de remédiation immédiat via GPO :

| Domaine | Vulnérabilité Constatée | Criticité | Impact de Sécurité |
| :--- | :--- | :--- | :--- |
| **Identités** | Mots de passe faibles autorisés (< 8 caractères) | 🔴 Critique | Facilite les attaques par Force Brute au dictionnaire. |
| **Authentification** | Protocoles obsolètes (NTLMv1) / LAN Manager permissif | 🔴 Critique | Permet le cassage rapide des hachages d'authentification interceptés. |
| **Réseau** | Protocole SMBv1 actif sur le Contrôleur de Domaine | 🔴 Critique | Expose l'entreprise aux ransomwares (type WannaCry) permettant une propagation latérale. |
| **Surface d'attaque** | Service Spouleur d'impression accessible à distance | 🔴 Critique | Vulnérabilité majeure (PrintNightmare) permettant l'exécution de code arbitraire. |
| **Administration** | Absence de solution LAPS (Mots de passe locaux identiques) | 🟠 Élevé | Risque de mouvement latéral si un poste client est compromis. |
| **Configuration** | MachineAccountQuota par défaut (10) | 🟠 Élevé | Favorise le Shadow IT (ajout de machines pirates au domaine sans être admin). |
| **Privilèges** | Comptes à privilèges exposés à la délégation | 🟠 Élevé | Risque de vol de session (Kerberoasting) si un admin se connecte sur une machine compromise. |
| **Résilience** | Corbeille AD (Recycle Bin) désactivée | 🟡 Moyen | Restauration complexe en cas de suppression accidentelle d'une OU. |
## 4. Exploitation (Point de vue du Pentester)

## 4. Exploitation (Point de vue du Pentester)

Pour justifier techniquement la nécessité des remédiations, voici comment la faille liée aux protocoles d'authentification obsolètes et aux requêtes de diffusion (Broadcast) est concrètement exploitée lors de la phase d'accès initial :

1. L'attaquant se connecte au réseau local et écoute le trafic avec un outil comme `Responder`.
2. Un utilisateur tente d'accéder à un partage réseau inexistant ou mal orthographié (ex: `\\partage_fichiers`).
3. Le serveur DNS ne trouvant pas la ressource, le poste client demande au réseau local (en broadcast via LLMNR/NBT-NS) si une machine possède ce nom.
4. L'attaquant répond frauduleusement et exploite la permissivité des protocoles d'authentification pour capturer le hash NTLM de l'utilisateur. Il peut ensuite le casser hors-ligne très rapidement ou le relayer vers un autre serveur (Relay Attack).

> [!TIP]
> **Prochaine étape**
> 
> Les failles identifiées constituent le périmètre d'action strict pour la phase de sécurisation. Chaque ligne du tableau des vulnérabilités correspond désormais à une tâche d'administration à réaliser.

> [!NOTE]
> **Pages liées**
> 
> - [Méthodologie Audit AD](Méthodologie%20Audit%20AD.md) — Cadre global de l'évaluation.
> 
> - [Matrice de Remediation](../Rapports%20et%20Plans%20Actions/Matrice%20de%20Remediation.md) — Suivi du plan d'action.
> 
> - [Désactivation protocoles obsoletes](../../02-Windows%20Server%20et%20Remediations/Deploiement%20GPO/Désactivation%20protocoles%20obsoletes.md) — Procédure de correction pour la faille A-02.