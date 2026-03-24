# Désactivation protocoles obsoletes

> [!NOTE] 
> **Contexte**
>  Le rapport d'audit PingCastle a mis en évidence l'activation par défaut des protocoles de résolution de noms de diffusion (LLMNR et NetBIOS sur TCP/IP). Ces protocoles historiques sont aujourd'hui considérés comme des vulnérabilités majeures (Vulnérabilité REM-02), car ils permettent à un attaquant de réaliser des attaques par empoisonnement (Poisoning) et des relais NTLM. Ce document détaille les procédures pour les éradiquer du domaine.

| Protocole | Vecteur de désactivation | Cible |
| :--- | :--- | :--- |
| LLMNR | GPO (Stratégie de groupe) | L'ensemble du domaine (`occitanie.lan`) |
| NBT-NS | Option DHCP / Script GPO | Postes clients et Serveurs |
| SMBv1 & NTLMv1 | GPO (Registre & Sécurité) | Serveurs et Contrôleur de domaine |

## 1. Désactivation de LLMNR (Link-Local Multicast Name Resolution)

La désactivation de LLMNR est nativement prise en charge par les modèles d'administration Windows. Une GPO globale est créée et liée à la racine du domaine (`occitanie.lan`), s'appliquant ainsi à tous les postes et serveurs.

**Chemin de configuration dans l'éditeur de GPO :**

1.Naviguer vers : `Configuration ordinateur` → `Stratégies` → `Modèles d'administration` → `Réseau` → `Client DNS`

2.Ouvrir le paramètre : **Désactiver la résolution de noms multidiffusion (LLMNR)**

3.Sélectionner : **Activé**


## 2. Désactivation de NBT-NS (NetBIOS over TCP/IP)

Contrairement à LLMNR, il n'existe pas de paramètre GPO natif simple pour désactiver complètement NetBIOS sur toutes les cartes réseau. Une approche hybride est donc nécessaire.

### Option A — Pour les postes clients (via le Serveur DHCP)

Si le serveur Windows gère le DHCP du réseau client, il est possible de pousser la désactivation directement via le bail IP.

1.Ouvrir la console **DHCP** (`dhcpmgmt.msc`).

2.Développer l'étendue IPv4 concernée → **Options d'étendue**.

3 Clic droit → **Configurer les options** → onglet **Avancé**.

4.Choisir la classe de fournisseur : `Options Microsoft standard`.

5.Cocher l'option **001 Option de désactivation NetBIOS de Microsoft**.

6.Définir la valeur sur : `0x2` (Désactiver NetBIOS sur TCP/IP).


### Option B — Pour les serveurs (IP Statiques via GPO / PowerShell)

Pour les serveurs (Tier 0 et Tier 1) configurés en IP statique, un script PowerShell de démarrage est déployé via une GPO (`Securite-Reseau-DesactiverNetBIOS-Serveurs`).

```PowerShell
# Script : disable_netbios.ps1
# Ce script parcourt toutes les cartes réseau actives et désactive NetBIOS
$adapters = Get-WmiObject Win32_NetworkAdapterConfiguration | Where-Object { $_.IPEnabled -eq $true }
foreach ($adapter in $adapters) {
    $adapter.SetTcpipNetbios(2) | Out-Null
}
```

_Note : Dans la méthode `SetTcpipNetbios`, la valeur `2` correspond à "Disable NetBIOS over TCP/IP"._

## 3. Désactivation de SMBv1 et NTLMv1 (Durcissement)

Conformément aux vulnérabilités critiques remontées lors de l'audit, deux protocoles historiques ont été désactivés via GPO pour empêcher la propagation de ransomwares (type WannaCry) et le cassage de hashs.

**A. Désactivation de SMBv1 (Serveurs) :**
Une GPO spécifique nommée **`Stratégie SEC_Disable_SMB1`** a été déployée. Plutôt que de désinstaller la fonctionnalité manuellement, la restriction est appliquée via les Préférences de Registre pour assurer une conformité continue.
* **Chemin :** `HKLM\System\CurrentControlSet\Services\LanmanServer\Parameters`
* **Clé :** `SMB1` (Type REG_DWORD) fixée à `0`.

**B. Forçage de NTLMv2 :**
Pour contrer les attaques de type "Man-in-the-Middle" et le relais d'authentification, la politique LAN Manager a été durcie.
* **Chemin GPO :** `Configuration ordinateur -> Stratégies -> Paramètres Windows -> Stratégies locales -> Options de sécurité`.
* **Paramètre :** `Sécurité réseau : niveau d'authentification LAN Manager`.
* **Valeur :** Forcer sur `Envoyer uniquement une réponse NTLM version 2. Refuser LM et NTLM`.

## 4. Vérification de l'application 

Pour valider que l'infrastructure n'est plus vulnérable, les vérifications suivantes sont effectuées sur un poste client du domaine fraîchement redémarré :

**Vérification de la GPO LLMNR via le Registre :**

```DOS
La valeur EnableMulticast doit être à 0
reg query "HKLM\Software\Policies\Microsoft\Windows NT\DNSClient" /v EnableMulticast
```

**Vérification de NetBIOS :**

```DOS
ipconfig /all
```

_Résultat attendu : La ligne `NetBIOS sur Tcpip` doit indiquer `Désactivé`._

## 5. Analyse des Risques et Défense en Profondeur

L'outil `Responder` est un standard dans l'arsenal des attaquants pour compromettre un annuaire Active Directory.

**Scénario d'attaque bloqué :** Lorsqu'un utilisateur tente d'accéder à un partage réseau inexistant (`\\serveur_fichiers_inconnu`), le poste client va d'abord interroger le serveur DNS. Sans réponse, par défaut, le poste va "crier" sur le réseau local via LLMNR et NBT-NS. L'attaquant, à l'écoute, répond et demande à l'utilisateur de s'authentifier, capturant ainsi son condensat de mot de passe (Hash NTLMv2). 

En appliquant ces remédiations, les requêtes de diffusion sont coupées à la source, rendant l'outil Responder totalement inefficace sur ce segment réseau.

> [!TIP]
> **Résultat final**
> 
> Les protocoles de diffusion réseau obsolètes sont totalement neutralisés sur le domaine `occitanie.lan`. Les communications réseau internes sont assainies, réduisant considérablement les risques de vol d'identifiants.

> [!NOTE]
> **Documents liés**
> 
> - [Analyse PingCastle](Analyse%20PingCastle.md) — Vulnérabilité identifiant l'activation de ces protocoles.
> - [Matrice de Remediation](Matrice%20de%20Remediation.md) — Validation du plan d'action (REM-02).