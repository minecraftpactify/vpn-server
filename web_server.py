"""
🌍 Serveur VPN déployable sur Render.com
API REST qui gère les connexions VPN
"""

from flask import Flask, jsonify, request
import os
import json
from datetime import datetime
import logging

app = Flask(__name__)

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Stockage en mémoire (pour la démo)
clients_connectes = {}
historique_connexions = []
statistiques = {
    "total_connexions": 0,
    "octets_transferes": 0,
    "demarre_le": datetime.now().isoformat()
}


@app.route('/')
def accueil():
    """Page d'accueil de l'API"""
    return jsonify({
        "service": "VPN Shield Server",
        "version": "1.0",
        "statut": "en ligne",
        "serveur": "Render.com",
        "heure_serveur": datetime.now().isoformat(),
        "clients_connectes": len(clients_connectes)
    })


@app.route('/api/handshake', methods=['POST'])
def handshake():
    """Endpoint pour le handshake VPN"""
    data = request.get_json()
    client_id = data.get('client_id', 'inconnu')
    pays = data.get('pays', 'inconnu')
    
    clients_connectes[client_id] = {
        "pays": pays,
        "connecte_le": datetime.now().isoformat(),
        "ip": request.remote_addr
    }
    
    statistiques["total_connexions"] += 1
    
    logger.info(f"🤝 Handshake de {client_id} depuis {pays}")
    
    return jsonify({
        "status": "success",
        "message": "Handshake réussi",
        "server_time": datetime.now().isoformat(),
        "assigned_ip": f"10.0.0.{len(clients_connectes) + 1}",
        "dns": "1.1.1.1, 8.8.8.8"
    })


@app.route('/api/data', methods=['POST'])
def recevoir_data():
    """Reçoit des données du client (chiffrées)"""
    data = request.get_json()
    client_id = data.get('client_id', 'inconnu')
    size = data.get('size', 0)
    encrypted = data.get('encrypted_payload', '')
    
    statistiques["octets_transferes"] += size
    
    logger.info(f"📦 Données de {client_id}: {size} octets")
    
    return jsonify({
        "status": "received",
        "echo_size": size
    })


@app.route('/api/disconnect', methods=['POST'])
def deconnecter():
    """Déconnecte un client"""
    data = request.get_json()
    client_id = data.get('client_id', 'inconnu')
    
    if client_id in clients_connectes:
        del clients_connectes[client_id]
    
    return jsonify({"status": "disconnected"})


@app.route('/api/stats')
def stats():
    """Statistiques du serveur"""
    return jsonify({
        "statistiques": statistiques,
        "clients_actifs": clients_connectes,
        "nombre_clients": len(clients_connectes)
    })


@app.route('/health')
def health():
    """Health check pour Render"""
    return "OK", 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
