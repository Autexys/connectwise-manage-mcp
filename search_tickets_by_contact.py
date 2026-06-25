#!/usr/bin/env python3
"""
Script pour rechercher les tickets ouverts d'un contact ConnectWise
"""

import requests
import json
import base64
from dotenv import load_dotenv
import os

# Charger les variables d'environnement depuis .env
load_dotenv()

# Configuration
COMPANY_ID = os.getenv('CW_MANAGE_COMPANY_ID', 'Vocalys')
PUBLIC_KEY = os.getenv('CW_MANAGE_PUBLIC_KEY')
PRIVATE_KEY = os.getenv('CW_MANAGE_PRIVATE_KEY')
CLIENT_ID = os.getenv('CW_MANAGE_CLIENT_ID')
BASE_URL = os.getenv('CW_MANAGE_URL', 'https://na.myconnectwise.net')

# Construire l'authentification
auth_string = f"{COMPANY_ID}+{PUBLIC_KEY}:{PRIVATE_KEY}"
auth_bytes = auth_string.encode('utf-8')
auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')

headers = {
    'Authorization': f'Basic {auth_b64}',
    'ClientID': CLIENT_ID,
    'Content-Type': 'application/json'
}

def test_connection():
    """Tester la connexion à l'API ConnectWise"""
    print("🧪 Test de connexion à ConnectWise...")
    
    # Tenter plusieurs versions d'API
    test_urls = [
        f"{BASE_URL}/v4_6_release/apis/3.0/system/info",
        f"{BASE_URL}/apis/3.0/system/info",
        f"{BASE_URL}/v4_6_release/apis/1.0/system/info",
    ]
    
    for url in test_urls:
        try:
            print(f"  Essai : {url}")
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                print(f"✅ Connexion réussie !")
                return True
            elif response.status_code == 404:
                print(f"  ❌ 404 Not Found")
            elif response.status_code == 401:
                print(f"  ❌ 401 Unauthorized")
            else:
                print(f"  Status : {response.status_code}")
        except Exception as e:
            print(f"  Erreur : {e}")
    
    return False

def search_tickets_by_contact(contact_name):
    """Rechercher les tickets pour un contact spécifique"""
    
    print(f"\n🔍 Recherche des tickets pour : {contact_name}")
    print("-" * 60)
    
    try:
        # Étape 0 : Test de connexion
        if not test_connection():
            print("\n⚠️  Impossible de se connecter à ConnectWise.")
            print("Vérifiez vos credentials et l'URL du serveur.")
            return
        
        # Étape 1 : Rechercher directement les tickets avec le nom du contact
        print(f"\n📌 Recherche des tickets...")
        tickets_url = f"{BASE_URL}/v4_6_release/apis/3.0/service/tickets"
        
        # Chercher les tickets contenant le nom du contact
        params = {
            'pageSize': 100,
            'conditions': f'contact/name like "%{contact_name}%" AND status/name != "Closed"',
            'orderBy': 'id desc'
        }
        
        response = requests.get(tickets_url, headers=headers, params=params)
        response.raise_for_status()
        
        tickets = response.json()
        
        print(f"\n✅ Tickets trouvés : {len(tickets)}")
        
        if not tickets:
            print(f"   ℹ️ Aucun ticket ouvert pour {contact_name}")
            return
        
        # Afficher les tickets
        print("\n" + "=" * 60)
        print(f"📋 TICKETS OUVERTS DE {contact_name.upper()}")
        print("=" * 60)
        
        for idx, ticket in enumerate(tickets, 1):
            print(f"\n{idx}. Ticket #{ticket['id']}")
            print(f"   📌 Sujet : {ticket.get('summary', 'N/A')}")
            print(f"   🏢 Société : {ticket.get('company', {}).get('name', 'N/A')}")
            print(f"   👤 Contact : {ticket.get('contact', {}).get('name', 'N/A')}")
            print(f"   🏷️ Statut : {ticket.get('status', {}).get('name', 'N/A')}")
            print(f"   ⏱️ Priorité : {ticket.get('priority', {}).get('name', 'N/A')}")
            print(f"   👨‍💼 Assigné à : {ticket.get('owner', {}).get('name', 'N/A')}")
            print(f"   📅 Créé le : {ticket.get('dateEntered', 'N/A')}")
            print(f"   🔗 URL : {BASE_URL}/v4_6_release/service/tickets/{ticket['id']}")
        
        print("\n" + "=" * 60)
        print(f"✅ Total : {len(tickets)} ticket(s) ouvert(s)")
        print("=" * 60 + "\n")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion : {e}")
        return
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return

if __name__ == "__main__":
    search_tickets_by_contact("Guillaume Bourgeois")
