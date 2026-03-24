# Synthèse des Vulnérabilités

> [!NOTE] 
> **Contexte**:
> 
>  Ce document consolide les résultats bruts obtenus lors des phases d'analyse (notamment via PingCastle) pour en extraire une vision globale des risques pesant sur le système d'information. L'objectif est de classifier ces vulnérabilités par vecteur d'attaque afin de structurer et prioriser les futures remédiations.

> [!NOTE] 
> **Échelle de Criticité** :
> 
> La classification s'appuie sur le niveau d'impact potentiel sur la confidentialité, l'intégrité et la disponibilité (CIA) du domaine :
> 
> - **Critique :** Compromission totale du domaine possible à très court terme.
>     
> - **Haute :** Élévation de privilèges ou fuite de données d'authentification majeures.
>     
> - **Moyenne :** Configuration affaiblissant la posture de sécurité globale.
>     

## 1. Bilan de Santé de l'Infrastructure

L'audit révèle que l'infrastructure Windows Server 2019 présente une surface d'attaque interne importante, principalement due à des configurations héritées activées par défaut et à l'absence de durcissement (hardening) post-installation.

## 2. Classification par Vecteur de Menace

Les vulnérabilités identifiées ont été regroupées en trois vecteurs principaux pour structurer la réponse technique :

### A. Configurations Système et Services

Ce vecteur regroupe les risques liés aux services par défaut de Windows Server.

- **Spouleur d'impression actif sur le DC (Critique) :** Rend le contrôleur de domaine vulnérable à des attaques de type PrintNightmare, permettant l'exécution de code à distance avec les privilèges SYSTEM.


### B. Protocoles Réseaux Obsolètes

Ce vecteur concerne les protocoles d'authentification et de partage hérités, non sécurisés par défaut.

* **Protocole SMBv1 actif (Critique) :** Présent sur le contrôleur de domaine, il expose l'entreprise aux ransomwares exploitant la faille EternalBlue (type WannaCry), permettant une propagation latérale foudroyante.
* **Protocoles obsolètes NTLMv1 (Critique) :** L'autorisation de niveaux d'authentification permissifs permet le cassage rapide des hachages interceptés sur le réseau.
* **LLMNR et NBT-NS actifs (Haute) :** Ces protocoles de résolution de noms permettent à un attaquant positionné sur le réseau local d'usurper des ressources et de capturer des empreintes (hash) lors des requêtes de diffusion.

### C. Gestion des Identités et des Accès (IAM)

Ce vecteur cible les faiblesses dans la gestion des comptes et de l'authentification.

* **Politique de mots de passe très faible (Critique) :** La configuration par défaut accepte des mots de passe inférieurs à 8 caractères. Cela rend les attaques par force brute ou par dictionnaire triviales pour un attaquant.
* **Mots de passe Administrateur Local identiques (Élevée) :** L'absence de rotation automatisée (solution LAPS) des mots de passe locaux facilite grandement les mouvements latéraux : si un seul poste client est compromis, tout le parc l'est potentiellement.
* **Comptes à privilèges exposés (Élevée) :** Certains comptes administrateurs sensibles sont exposés à la délégation, ce qui les rend vulnérables au vol de session (Kerberoasting).


## 3. Analyse d'Impact Métier

La non-remédiation de ces vulnérabilités expose directement l'organisation à deux scénarios majeurs :

1.**Déploiement de Ransomware :** Propagation facilitée et accélérée par les mouvements latéraux permis par la mauvaise gestion des mots de passe locaux.

2.**Fuite de données critiques :** Usurpation d'identité et élévation de privilèges silencieuse via les protocoles de diffusion réseau.


> [!TIP] 
> **Prochaine étape**
>  Cette synthèse confirme la nécessité d'une intervention ciblée. Les éléments classifiés ici justifient le plan d'action détaillé dans la Matrice de Remédiation, clôturant ainsi la phase d'Audit et Conformité.

> [!NOTE]
> **Documents liés**
> 
> - [Analyse PingCastle](Analyse%20PingCastle.md) — Rapport technique détaillé et scores de risque.
> 
> - [Matrice de Remediation](Matrice%20de%20Remediation.md) — Plan d'action technique découlant de cette synthèse.