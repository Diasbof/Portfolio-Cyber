# Analyse PingCastle

## Contexte
Évaluation du niveau de sécurité du domaine de l'entreprise Occitanie-IT via l'outil PingCastle. Cet utilitaire audite la configuration de l'Active Directory et génère un score de risque basé sur les vulnérabilités détectées. Les résultats de cette analyse servent de référence "avant travaux" et de feuille de route pour le déploiement des stratégies de groupe (GPO) de remédiation.

**Cible de l'audit :**
* **Rôle :** Contrôleur de Domaine (DC01)
* **Système d'exploitation :** Windows Server 2019

---

## 1. Analyse du Score de Risque

PingCastle attribue un score de risque global calculé sur 100. Lors de l'audit initial de l'infrastructure, le domaine a obtenu un score de risque de **57/100**. Ce résultat positionne l'infrastructure dans une zone de vulnérabilité critique, confirmant que la configuration "par défaut" (Out-of-the-box) n'a jamais été durcie.

L'analyse de la matrice des risques met en lumière trois axes critiques de faiblesse structurelle :

1. **Obsolescence (Stale Objects) :** L'indicateur "Old authentication protocols" confirme que le réseau traîne une dette technique dangereuse (SMBv1, NTLMv1), facilitant l'interception de données.
2. **Compromission de comptes (Privileged Accounts) :** La catégorie "Account take over" en alerte élevée indique que les comptes administrateurs sont mal protégés, exposant l'entreprise à une perte totale de contrôle du domaine en cas de vol d'identifiants.
3. **Mouvement Latéral (Anomalies) :** L'alerte sur "Pass-the-credential" signifie qu'une fois entré dans le réseau, un attaquant peut facilement voler des tickets d'authentification pour sauter de machine en machine jusqu'au Contrôleur de Domaine.

---

## 2. Principales Vulnérabilités Identifiées

Le tableau ci-dessous synthétise les failles structurelles qualifiées de prioritaires pour la phase de durcissement (Hardening).

| Domaine | Vulnérabilité Constatée | Criticité | Impact Technique et Métier |
| :--- | :--- | :--- | :--- |
| **Identités** | Mots de passe faibles autorisés (Politique par défaut acceptant < 8 caractères) | **Critique** | Facilite les attaques par Force Brute au dictionnaire. Un attaquant peut deviner un mot de passe utilisateur en quelques minutes. |
| **Authentification** | Protocoles obsolètes actifs (NTLMv1) / Niveau d'authentification LAN Manager trop permissif | **Critique** | Permet les attaques de type "Man-in-the-Middle" et le cassage rapide des hachages d'authentification interceptés. |
| **Réseau** | Protocole SMBv1 actif (Présent sur le Contrôleur de Domaine) | **Critique** | Expose l'entreprise aux ransomwares exploitant la faille EternalBlue (type WannaCry), permettant une propagation latérale foudroyante. |
| **Surface d'attaque** | Service Spouleur d'impression actif (Accessible à distance sur le Contrôleur de Domaine) | **Critique** | Vulnérabilité majeure (PrintNightmare) permettant à un utilisateur authentifié d'exécuter du code arbitraire sur le serveur et de devenir administrateur. |
| **Administration** | Absence de solution LAPS (Gestion des mots de passe administrateurs locaux non automatisée) | **Élevé** | Risque de mouvement latéral. Si le mot de passe admin local est identique sur tous les postes, compromettre un PC permet de compromettre tout le parc. |
| **Configuration** | MachineAccountQuota par défaut (10) (Tout utilisateur peut joindre 10 machines au domaine) | **Élevé** | Favorise le Shadow IT. Un attaquant ayant compromis un compte standard peut ajouter des machines pirates au réseau sans être admin. |
| **Privilèges** | Comptes à privilèges non protégés (Comptes admins sensibles exposés à la délégation) | **Élevé** | Risque de vol de session (Kerberoasting / Silver Ticket) si un administrateur se connecte sur une machine compromise. |
| **Résilience** | Corbeille AD désactivée (Fonctionnalité "Recycle Bin" non activée sur la forêt) | **Moyen** | En cas de suppression accidentelle ou malveillante d'une OU ou d'utilisateurs, la restauration est complexe et entraîne un arrêt de production prolongé. |

---

## 3. Exploitation (Point de vue du Pentester)

Pour justifier techniquement la nécessité des remédiations auprès de la direction, voici comment la faille liée aux protocoles d'authentification obsolètes et aux requêtes de diffusion (LLMNR/NBT-NS) est concrètement exploitée lors de la phase d'accès initial :

1. L'attaquant se connecte de manière furtive au réseau local (LAN) et écoute le trafic avec un outil d'empoisonnement comme **Responder**.
2. Un utilisateur légitime tente d'accéder à un partage réseau inexistant ou fait une faute de frappe (ex: `\\partage_fichiers`).
3. Le serveur DNS ne trouvant pas la ressource, le poste client demande "à la cantonade" sur le réseau local (en broadcast via LLMNR/NBT-NS) si une machine possède ce nom.
4. L'attaquant répond frauduleusement : "C'est moi, authentifie-toi". Il exploite alors la permissivité des protocoles d'authentification pour capturer l'empreinte (Hash NTLMv2) de l'utilisateur. Il peut ensuite casser ce hash hors-ligne très rapidement en raison de la faiblesse de la politique de mots de passe, ou le relayer vers un autre serveur (Relay Attack).

---

## 4. Plan de traitement et Prochaines étapes

La non-remédiation de ces vulnérabilités expose directement l'organisation à un déploiement massif de Ransomware et à la fuite de ses données critiques. 

> [!TIP]
> **💡 Prochaine étape :**
>Les failles identifiées constituent le périmètre d'action strict pour la phase de sécurisation. Chaque ligne du tableau des vulnérabilités correspond désormais à une tâche d'administration à réaliser.

> [!NOTE]
**Documents liés :**
>* ➡️ [Matrice de Remédiation](Lien_vers_fichier.md) : Suivi détaillé du plan d'action.
>* ➡️ [Désactivation protocoles obsolètes](Lien_vers_fichier.md) : Procédure de correction technique et GPO.