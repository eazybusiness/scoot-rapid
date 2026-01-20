#!/usr/bin/env python3
"""
Simple script to show current scooters in the system
"""

import sys
import os

# Add the project directory to Python path
sys.path.insert(0, '/home/nop/Documents/cascade_projects/scoot_rapid')

try:
    from app import create_app, db
    from app.models.scooter import Scooter
    from app.models.user import User
    
    app = create_app()
    
    with app.app_context():
        print("🛴 AKUELLE SCOOTER IM SYSTEM")
        print("=" * 60)
        
        scooters = Scooter.query.all()
        
        if not scooters:
            print("❌ Keine Scooter im System gefunden")
            sys.exit(0)
        
        for i, scooter in enumerate(scooters, 1):
            provider = User.query.get(scooter.provider_id) if scooter.provider_id else None
            provider_name = provider.get_full_name() if provider else "Unbekannt"
            
            print(f"\n🛴 SCOOTER #{i}")
            print(f"   ID: {scooter.id}")
            print(f"   Identifier: {scooter.identifier}")
            print(f"   Kennzeichen: {scooter.license_plate or 'Nicht gesetzt'}")
            print(f"   Modell: {scooter.brand} {scooter.model}")
            print(f"   Status: {scooter.status}")
            print(f"   Provider: {provider_name} (ID: {scooter.provider_id})")
            print(f"   Batterie: {scooter.battery_level}%")
            print(f"   Standort: {scooter.address or 'Keine Adresse'}")
            print(f"   GPS: {scooter.latitude}, {scooter.longitude}")
            print(f"   QR Code: {scooter.qr_code}")
            print(f"   Erstellt: {scooter.created_at}")
            print("   " + "-" * 50)
        
        print(f"\n📊 GESAMT: {len(scooters)} Scooter im System")
        
        # Status summary
        status_count = {}
        for scooter in scooters:
            status_count[scooter.status] = status_count.get(scooter.status, 0) + 1
        
        print("\n📈 STATUS-ÜBERSICHT:")
        for status, count in status_count.items():
            print(f"   {status}: {count} Scooter")
            
except ImportError as e:
    print(f"❌ Import Fehler: {e}")
    print("Stellen Sie sicher, dass Sie im richtigen Verzeichnis sind und die Abhängigkeiten installiert sind.")
except Exception as e:
    print(f"❌ Fehler: {e}")
