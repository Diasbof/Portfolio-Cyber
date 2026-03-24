# Alertes personnalisées et Réponse Active

> [!NOTE]
> **Contexte**
> 
> Dans le cadre de la supervision de l'infrastructure Active Directory (`occitanie.lan`), le SIEM Wazuh est configuré pour détecter et bloquer les attaques visant le Contrôleur de Domaine (DC01). Ce document détaille la création de règles de détection sur-mesure et la mise en place d'une réponse active (Active Response) pour contrer les attaques par force brute sur le protocole RDP (Remote Desktop Protocol).

> [!NOTE]
> **Cible et Périmètre**
> 
> - **Cible de détection :** Contrôleur de domaine (WIN-479952UTUH2) sous Windows Server 2019.
> - **Vecteur surveillé :** Journaux d'événements de sécurité Windows (Event Logs - ID 4625).

## 1. Collecte des journaux de sécurité Windows

Pour que Wazuh puisse détecter les tentatives d'intrusion, l'agent déployé sur le serveur Windows doit être configuré pour intercepter les échecs d'authentification (Event ID 4625) générés dans l'observateur d'événements.

Configuration ajoutée dans le fichier `ossec.conf` de l'agent Windows (DC01) :

```xml
<localfile>
  <location>Security</location>
  <log_format>eventchannel</log_format>
  <query>Event/System[EventID=4625]</query>
</localfile>
```
## 2. Création de Règles de Détection Personnalisées (Wazuh)

Les règles natives de Wazuh sont enrichies sur le serveur Manager (Debian) en modifiant le fichier `/var/ossec/etc/rules/local_rules.xml`. L'objectif est de créer une alerte critique spécifique lorsque de multiples échecs d'authentification RDP sont détectés en un laps de temps très court.

```xml
<group name="windows, rdp, bruteforce, custom_rules">
  
  <rule id="100001" level="12" frequency="6" timeframe="120">
    <if_matched_sid>60122</if_matched_sid> <description>Alerte Critique : Attaque par Force Brute RDP détectée sur le DC01</description>
    <mitre>
      <id>T1110.001</id>
    </mitre>
  </rule>

</group>
````

_(Note : Cette règle déclenche une alerte de niveau 12 si 6 échecs de connexion surviennent en moins de 2 minutes)._

## 3. Configuration de la Réponse Active (Active Response)

Pour ne pas se contenter d'alerter, une Réponse Active est configurée sur le Manager. Lorsqu'une attaque est confirmée (Déclenchement de la règle `100001`), le Manager ordonne à l'agent Windows de bloquer l'adresse IP de l'attaquant au niveau de son pare-feu local en utilisant l'utilitaire Windows natif `netsh`.

Configuration ajoutée dans le `ossec.conf` du Wazuh Manager :

```xml
<command>
  <name>win_netsh_drop</name>
  <executable>netsh.cmd</executable>
  <timeout_allowed>yes</timeout_allowed>
</command>

<active-response>
  <command>win_netsh_drop</command>
  <location>local</location>
  <rules_id>100001</rules_id>
  <timeout>600</timeout> </active-response>
````
## 4. Tests et Validation (Offensif -> Défensif)

Pour valider l'efficacité de la chaîne de détection et de réaction, une attaque par dictionnaire (Force Brute) est lancée depuis la machine d'audit Kali Linux vers le contrôleur de domaine Windows.

```bash
# Simulation d'une attaque RDP (Outil Crowbar)
crowbar -b rdp -U users.txt -C passwords.txt -s 10.0.2.10/32
````

> [!TIP] **Résultat attendu**
> 
> Dès le 6ème échec consécutif, l'alerte de niveau 12 remonte sur le tableau de bord Wazuh. Instantanément, la réponse active s'enclenche : une règle de pare-feu Windows est dynamiquement créée sur le DC01, bloquant toute communication en provenance de l'IP de la machine Kali Linux pendant 10 minutes (600 secondes). L'attaque est techniquement stoppée.

> [!NOTE] **Documents liés**
> 
> - [Architecture et Déploiement Wazuh](https://www.google.com/search?q=Architecture%2520et%2520D%C3%A9ploiement%2520Wazuh.md) — Paramétrage initial de la solution.
>     
> - [Analyse Défensive et Pentest](https://www.google.com/search?q=../../04-Audit%2520Offensif%2520et%2520Pentest/Analyse%2520Defensive/Corr%C3%A9lation%2520des%2520%C3%89v%C3%A9nements.md) — Corrélation des logs pendant la phase offensive.
>