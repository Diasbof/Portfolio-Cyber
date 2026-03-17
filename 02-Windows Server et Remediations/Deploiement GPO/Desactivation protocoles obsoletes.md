> [!NOTE] 
> **Contexte**
>  Le rapport d'audit PingCastle a mis en évidence l'activation par défaut des protocoles de résolution de noms de diffusion (LLMNR et NetBIOS sur TCP/IP). Ces protocoles historiques sont aujourd'hui considérés comme des vulnérabilités majeures (Vulnérabilité REM-02), car ils permettent à un attaquant de réaliser des attaques par empoisonnement (Poisoning) et des relais NTLM. Ce document détaille les procédures pour les éradiquer du domaine.

> [!NOTE] 
> **Périmètre d'application**
> 
> |Protocole|Vecteur de désactivation|Cible|
> |---|---|---|
> |**LLMNR**|GPO (Stratégie de groupe)|L'ensemble du domaine (`fsec.lan`)|
> |**NBT-NS**|Option DHCP|Postes clients (Adresses IP dynamiques)|
> |**NBT-NS**|Script PowerShell (GPO)|Serveurs (Adresses IP statiques)|

## 1. Désactivation de LLMNR (Link-Local Multicast Name Resolution)

La désactivation de LLMNR est nativement prise en charge par les modèles d'administration Windows. Une GPO globale nommée `Securite-Reseau-DesactiverLLMNR` est créée et liée à la racine du domaine (`fsec.lan`), s'appliquant ainsi à tous les postes et serveurs.

**Chemin de configuration dans l'éditeur de GPO :**

1. Naviguer vers : `Configuration ordinateur` → `Stratégies` → `Modèles d'administration` → `Réseau` → `Client DNS`
    
2. Ouvrir le paramètre : **Désactiver la résolution de noms multidiffusion (LLMNR)**
    
3. Sélectionner : **Activé**
    

## 2. Désactivation de NBT-NS (NetBIOS over TCP/IP)

Contrairement à LLMNR, il n'existe pas de paramètre GPO natif simple pour désactiver complètement NetBIOS sur toutes les cartes réseau. Une approche hybride est donc nécessaire.

### Option A — Pour les postes clients (via le Serveur DHCP)

Si le serveur Windows gère le DHCP du réseau client, il est possible de pousser la désactivation directement via le bail IP.

1. Ouvrir la console **DHCP** (`dhcpmgmt.msc`).
    
2. Développer l'étendue IPv4 concernée → **Options d'étendue**.
    
3. Clic droit → **Configurer les options** → onglet **Avancé**.
    
4. Choisir la classe de fournisseur : `Options Microsoft standard`.
    
5. Cocher l'option **001 Option de désactivation NetBIOS de Microsoft**.
    
6. Définir la valeur sur : `0x2` (Désactiver NetBIOS sur TCP/IP).
    

### Option B — Pour les serveurs (IP Statiques via GPO / PowerShell)

Pour les serveurs (Tier 0 et Tier 1) configurés en IP statique, un script PowerShell de démarrage est déployé via une GPO (`Securite-Reseau-DesactiverNetBIOS-Serveurs`).

PowerShell

```
# Script : disable_netbios.ps1
# Ce script parcourt toutes les cartes réseau actives et désactive NetBIOS
$adapters = Get-WmiObject Win32_NetworkAdapterConfiguration | Where-Object { $_.IPEnabled -eq $true }
foreach ($adapter in $adapters) {
    $adapter.SetTcpipNetbios(2) | Out-Null
}
```

_Note : Dans la méthode `SetTcpipNetbios`, la valeur `2` correspond à "Disable NetBIOS over TCP/IP"._

## 3. Vérification de l'application

Pour valider que l'infrastructure n'est plus vulnérable, les vérifications suivantes sont effectuées sur un poste client de test (`PC-CLIENT01`) :

**Vérification de la GPO LLMNR via le Registre :**

DOS

```
REM La valeur EnableMulticast doit être à 0
reg query "HKLM\Software\Policies\Microsoft\Windows NT\DNSClient" /v EnableMulticast
```

**Vérification de NetBIOS :**

DOS

```
ipconfig /all
```

_Résultat attendu : La ligne `NetBIOS sur Tcpip` doit indiquer `Désactivé`._

## 4. Analyse des Risques et Défense en Profondeur (Le point de vue du Défenseur)

L'outil **Responder** est un standard dans l'arsenal des attaquants pour compromettre un annuaire Active Directory.

**Scénario d'attaque bloqué :** Lorsqu'un utilisateur tente d'accéder à un partage réseau inexistant (`\\serveur_fichiers_inconnu`), le poste client va d'abord interroger le serveur DNS. Sans réponse, par défaut, le poste va "crier" sur le réseau local via LLMNR et NBT-NS pour demander : _"Quelqu'un connait-il cette machine ?"_. L'attaquant, à l'écoute, répond _"C'est moi !"_ et demande à l'utilisateur de s'authentifier, capturant ainsi son condensat de mot de passe (Hash NTLMv2).

En appliquant ces remédiations, les postes Windows s'en tiennent strictement à la résolution DNS classique. Les requêtes de diffusion sont coupées à la source, rendant l'outil Responder totalement inefficace sur ce segment réseau.

> [!TIP] 
> **Résultat final** 
> Les protocoles de diffusion réseau obsolètes sont totalement neutralisés sur le domaine `fsec.lan`. Les communications réseau internes sont assainies, réduisant considérablement les risques de vol d'identifiants.

> [!NOTE] 
> **Documents liés**
> 
> - [[Analyse PingCastle]] — Vulnérabilité A-02 identifiant l'activation de ces protocoles.
>     
> - [[Matrice de Remediation]] — Validation du plan d'action (REM-02).
>