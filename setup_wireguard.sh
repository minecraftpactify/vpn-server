#!/bin/bash
# Script d'installation WireGuard pour le serveur VPN

echo "🔐 Installation de WireGuard..."

# Installation
apt-get update
apt-get install -y wireguard qrencode iptables

# Génération des clés du serveur
cd /etc/wireguard
wg genkey | tee server_private.key | wg pubkey > server_public.key
chmod 600 server_private.key

echo "✅ Clés générées"
cat server_private.key
echo "---"
cat server_public.key
