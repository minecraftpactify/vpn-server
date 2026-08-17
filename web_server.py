"""
🌍 Serveur VPN - WireGuard + API de contrôle
"""

from flask import Flask, jsonify, request
import os
import json
import subprocess
from datetime import datetime
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Stockage
clients_connectes = {}
statistiques = {
    "total_connexions": 0,
    "octets_transferes": 0,
    "demarre_le": datetime.now().isoformat(),
    "wireguard_actif": False
}

WG_CONFIG = """[Interface]
PrivateKey = SERVER_PRIVATE_KEY
Address = 10.0.0.1/24
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
ListenPort = 51820

[Peer]
PublicKey = CLIENT_PUBLIC_KEY
AllowedIPs = 10.0.0.2/32
"""


@app.route('/')
def accueil():
    return jsonify({
        "service": "VPN Shield - WireGuard",
        "version": "2.0",
        "statut": "en ligne",
        "serveur": "Render.com - Frankfurt",
        "wireguard": statistiques["wireguard_actif"],
        "heure_serveur": datetime.now().isoformat(),
        "ip_publique": request.host,
        "clients_connectes": len(clients_connectes)
    })


@app.route('/api/handshake', methods=['POST'])
def handshake():
    data = request.get_json() or {}
    client_id = data.get('client_id', 'inconnu')
    pays = data.get('pays', 'inconnu')
    client_public_key = data.get('public_key', None)
    
    clients_connectes[client_id] = {
        "pays": pays,
        "public_key": client_public_key,
        "connecte_le": datetime.now().isoformat(),
        "ip_source": request.remote_addr
    }
    
    statistiques["total_connexions"] += 1
    
    return jsonify({
        "status": "success",
        "message": "Handshake réussi",
        "server_time": datetime.now().isoformat(),
        "assigned_ip": "10.0.0.2",
        "dns": "1.1.1.1, 8.8.8.8",
        "info": "Pour le tunneling complet, configure WireGuard sur ton PC"
    })


@app.route('/api/config', methods=['GET'])
def get_config():
    """Retourne la config WireGuard client"""
    return jsonify({
        "config": WG_CONFIG,
        "note": "Remplace SERVER_PRIVATE_KEY par la vraie clé du serveur"
    })


@app.route('/api/stats')
def stats():
    return jsonify({
        "statistiques": statistiques,
        "clients_actifs": clients_connectes,
        "nombre_clients": len(clients_connectes)
    })


@app.route('/api/data', methods=['POST'])
def recevoir_data():
    data = request.get_json() or {}
    client_id = data.get('client_id', 'inconnu')
    size = data.get('size', 0)
    statistiques["octets_transferes"] += size
    return jsonify({"status": "received", "echo_size": size})


@app.route('/api/disconnect', methods=['POST'])
def deconnecter():
    data = request.get_json() or {}
    client_id = data.get('client_id', 'inconnu')
    if client_id in clients_connectes:
        del clients_connectes[client_id]
    return jsonify({"status": "disconnected"})


@app.route('/health')
def health():
    return "OK", 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
