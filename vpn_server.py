"""
🛡️ Serveur VPN éducatif (v2)
Accepte les handshakes, répond aux clients et déchiffre les messages
"""

import socket
import logging
import os
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s'
)
logger = logging.getLogger(__name__)


class VPNServer:
    def __init__(self, host='0.0.0.0', port=51820):
        self.host = host
        self.port = port
        self.clients = {}  # {addr: {nom, cle_session, paquets, messages}}
        self.running = False
        self.socket = None
    
    def dechiffrer(self, data, cle):
        """Déchiffre les données avec ChaCha20"""
        nonce = data[:16]
        ciphertext = data[16:]
        cipher = Cipher(algorithms.ChaCha20(cle, nonce), mode=None, backend=default_backend())
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext)
    
    def demarrer(self):
        """Démarre le serveur VPN"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        self.running = True
        
        print("\n" + "=" * 60)
        print("🛡️  SERVEUR VPN v2 - AVEC HANDSHAKE")
        print("=" * 60)
        logger.info(f"🚀 En écoute sur {self.host}:{self.port}")
        logger.info("⏳ En attente de connexions clients...")
        print()
        
        self._ecouter()
    
    def _ecouter(self):
        """Boucle principale"""
        try:
            while self.running:
                data, addr = self.socket.recvfrom(65535)
                self._traiter_paquet(data, addr)
        except KeyboardInterrupt:
            self.arreter()
    
    def _traiter_paquet(self, data, addr):
        """Traite un paquet reçu"""
        # === HANDSHAKE ===
        if data.startswith(b"HANDSHAKE:"):
            cle_session = data[10:]  # Récupère la clé après "HANDSHAKE:"
            self.clients[addr] = {
                'nom': f"client_{len(self.clients)+1}",
                'cle_session': cle_session,
                'connecte_depuis': datetime.now(),
                'paquets': 0,
                'messages': []
            }
            logger.info(f"🤝 Handshake reçu de {addr[0]}:{addr[1]}")
            logger.info(f"✅ Client enregistré : {self.clients[addr]['nom']}")
            
            # Répond OK au client
            self.socket.sendto(b"OK:HANDSHAKE_SUCCESS", addr)
            logger.info(f"📤 Réponse envoyée au client\n")
            return
        
        # === PAQUET CHIFFRÉ ===
        if addr in self.clients and self.clients[addr]['cle_session']:
            client = self.clients[addr]
            client['paquets'] += 1
            
            try:
                # Déchiffre le message
                message = self.dechiffrer(data, client['cle_session'])
                message_str = message.decode('utf-8', errors='replace')
                client['messages'].append(message_str)
                
                # Log tous les 5 paquets ou pour les 5 premiers
                if client['paquets'] <= 5 or client['paquets'] % 5 == 0:
                    logger.info(f"📥 {client['nom']} (paquet #{client['paquets']}) : {message_str}")
                
            except Exception as e:
                logger.error(f"❌ Erreur déchiffrement de {client['nom']} : {e}")
        else:
            logger.warning(f"⚠️  Paquet inconnu de {addr[0]}:{addr[1]}")
    
    def arreter(self):
        """Arrête le serveur"""
        self.running = False
        if self.socket:
            self.socket.close()
        
        # Affiche le résumé
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DE LA SESSION")
        print("=" * 60)
        for addr, client in self.clients.items():
            print(f"Client : {client['nom']} ({addr[0]}:{addr[1]})")
            print(f"  Paquets reçus : {client['paquets']}")
            print(f"  Dernier message : {client['messages'][-1] if client['messages'] else 'aucun'}")
            print()
        
        print("=" * 60)
        logger.info("🛑 Serveur arrêté")
        print("=" * 60)


if __name__ == "__main__":
    serveur = VPNServer()
    try:
        serveur.demarrer()
    except KeyboardInterrupt:
        serveur.arreter()
