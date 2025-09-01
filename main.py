from database.schema.users import User, UserQueries, UserRepository, UserCreate
from database.schema.tasks import Task, TaskQueries, TaskRepository, TaskCreate
from database.schema.sites import Site, SiteQueries, SiteRepository, SiteCreate
from database.schema.products import (
    Product,
    ProductQueries,
    ProductRepository,
    ProductCreate,
)
from database.schema.orders import Order, OrderQueries, OrderRepository, OrderCreate
from database.schema.suppliers import (
    Supplier,
    SupplierQueries,
    SupplierRepository,
    SupplierCreate,
)
from src.models.enums.enums import TaskStatus, OrderStatus
from src.mcp_server import connect_to_tidb
import datetime as dt

import database.schema.base as base


def main():
    """Fonction principale pour tester tout"""
    print("🚀 Démarrage du test TiDB simple\n")

    # 1. Se connecter
    conn = connect_to_tidb()
    if not conn:
        print("Impossible de continuer sans connexion")
        return

    try:
        # 2. Nettoyer toutes les tables existantes
        print("🧹 Nettoyage de la base de données...")
        base.drop_all_tables(conn)
        
        # 3. Créer toutes les tables
        print("\n📊 Création des tables...")
        base.create_table(conn, User.__tablename__, UserQueries.sql_create_table)
        base.create_table(
            conn, Supplier.__tablename__, SupplierQueries.sql_create_table
        )
        base.create_table(conn, Site.__tablename__, SiteQueries.sql_create_table)
        base.create_table(conn, Order.__tablename__, OrderQueries.sql_create_table)
        base.create_table(conn, Product.__tablename__, ProductQueries.sql_create_table)
        base.create_table(conn, Task.__tablename__, TaskQueries.sql_create_table)
        print("✅ Toutes les tables créées avec succès !")

        # 4. Créer 10 utilisateurs
        print("\n👥 Création de 10 utilisateurs...")
        users_data = [
            UserCreate(
                email="admin@company.com",
                password="password123",
                first_name="Admin",
                last_name="Principal",
                phone="0123456789",
                is_active=True,
                is_admin=True,
                role="admin",
                specialization="management",
            ),
            UserCreate(
                email="tech1@company.com",
                password="password123",
                first_name="Jean",
                last_name="Dupont",
                phone="0123456780",
                is_active=True,
                is_admin=False,
                role="technician",
                specialization="plumber",
            ),
            UserCreate(
                email="tech2@company.com",
                password="password123",
                first_name="Marie",
                last_name="Martin",
                phone="0123456781",
                is_active=True,
                is_admin=False,
                role="technician",
                specialization="electrician",
            ),
            UserCreate(
                email="supervisor@company.com",
                password="password123",
                first_name="Pierre",
                last_name="Bernard",
                phone="0123456782",
                is_active=True,
                is_admin=False,
                role="supervisor",
                specialization="general",
            ),
            UserCreate(
                email="client1@external.com",
                password="password123",
                first_name="Sophie",
                last_name="Dubois",
                phone="0123456783",
                is_active=True,
                is_admin=False,
                role="client",
                specialization="none",
            ),
            UserCreate(
                email="tech3@company.com",
                password="password123",
                first_name="Lucas",
                last_name="Moreau",
                phone="0123456784",
                is_active=True,
                is_admin=False,
                role="technician",
                specialization="hvac",
            ),
            UserCreate(
                email="manager@company.com",
                password="password123",
                first_name="Catherine",
                last_name="Rousseau",
                phone="0123456785",
                is_active=True,
                is_admin=False,
                role="manager",
                specialization="operations",
            ),
            UserCreate(
                email="client2@external.com",
                password="password123",
                first_name="Antoine",
                last_name="Leroy",
                phone="0123456786",
                is_active=True,
                is_admin=False,
                role="client",
                specialization="none",
            ),
            UserCreate(
                email="tech4@company.com",
                password="password123",
                first_name="Isabelle",
                last_name="Simon",
                phone="0123456787",
                is_active=True,
                is_admin=False,
                role="technician",
                specialization="maintenance",
            ),
            UserCreate(
                email="assistant@company.com",
                password="password123",
                first_name="Thomas",
                last_name="Michel",
                phone="0123456788",
                is_active=True,
                is_admin=False,
                role="assistant",
                specialization="general",
            ),
        ]

        created_users = []
        for user_data in users_data:
            user = UserRepository.create_user(conn, user_data)
            if user:
                created_users.append(user)

        # 5. Créer 10 fournisseurs
        print("\n🏪 Création de 10 fournisseurs...")
        suppliers_data = [
            SupplierCreate(
                name="TechSupply Pro",
                address="123 Tech Street, Paris 75001",
                phone="+33 1 23 45 67 89",
                email="contact@techsupply.com",
                type="Informatique",
            ),
            SupplierCreate(
                name="PlombExpert SA",
                address="456 Plumber Ave, Lyon 69000",
                phone="+33 4 78 90 12 34",
                email="commandes@plombexpert.fr",
                type="Plomberie",
            ),
            SupplierCreate(
                name="ElectricMax",
                address="789 Electric Blvd, Marseille 13000",
                phone="+33 4 91 23 45 67",
                email="orders@electricmax.com",
                type="Électricité",
            ),
            SupplierCreate(
                name="Bureau Plus",
                address="321 Office St, Toulouse 31000",
                phone="+33 5 61 12 34 56",
                email="ventes@bureauplus.fr",
                type="Fournitures Bureau",
            ),
            SupplierCreate(
                name="Climatech Services",
                address="654 Climate Way, Nice 06000",
                phone="+33 4 93 87 65 43",
                email="support@climatech.fr",
                type="Chauffage/Climatisation",
            ),
            SupplierCreate(
                name="Mobilier Pro",
                address="987 Furniture Rd, Nantes 44000",
                phone="+33 2 40 11 22 33",
                email="commandes@mobilierpro.com",
                type="Mobilier",
            ),
            SupplierCreate(
                name="Outils & Cie",
                address="147 Tools Street, Strasbourg 67000",
                phone="+33 3 88 44 55 66",
                email="info@outilsetcie.fr",
                type="Outillage",
            ),
            SupplierCreate(
                name="SecuriMax",
                address="258 Security Blvd, Bordeaux 33000",
                phone="+33 5 56 77 88 99",
                email="contact@securimax.fr",
                type="Sécurité",
            ),
            SupplierCreate(
                name="MaintenancePro",
                address="369 Service Ave, Rennes 35000",
                phone="+33 2 99 00 11 22",
                email="services@maintenancepro.com",
                type="Maintenance",
            ),
            SupplierCreate(
                name="GreenTech Solutions",
                address="741 Eco Street, Montpellier 34000",
                phone="+33 4 67 33 44 55",
                email="eco@greentech.fr",
                type="Écologie",
            ),
        ]

        for supplier_data in suppliers_data:
            SupplierRepository.create_supplier(conn, supplier_data)

        # 6. Créer 10 sites
        print("\n🏢 Création de 10 sites...")
        # Utiliser les vrais IDs des utilisateurs créés
        user_ids = [user.id for user in created_users] if created_users else [90002, 90003, 90004, 90005, 90006, 90007, 90008, 90009, 90010]
        
        sites_data = [
            SiteCreate(
                name="Siège Social Paris", location="Paris 8ème, 75008", created_by=user_ids[0]
            ),
            SiteCreate(
                name="Agence Lyon Centre", location="Lyon 2ème, 69002", created_by=user_ids[0]
            ),
            SiteCreate(
                name="Bureau Marseille", location="Marseille 1er, 13001", created_by=user_ids[0]
            ),
            SiteCreate(
                name="Antenne Toulouse", location="Toulouse Centre, 31000", created_by=user_ids[2] if len(user_ids) > 2 else user_ids[0]
            ),
            SiteCreate(
                name="Succursale Nice", location="Nice Centre, 06000", created_by=user_ids[2] if len(user_ids) > 2 else user_ids[0]
            ),
            SiteCreate(
                name="Point Nantes", location="Nantes Centre, 44000", created_by=user_ids[5] if len(user_ids) > 5 else user_ids[0]
            ),
            SiteCreate(
                name="Filiale Strasbourg",
                location="Strasbourg Centre, 67000",
                created_by=user_ids[5] if len(user_ids) > 5 else user_ids[0],
            ),
            SiteCreate(
                name="Bureau Bordeaux", location="Bordeaux Centre, 33000", created_by=user_ids[0]
            ),
            SiteCreate(
                name="Agence Rennes", location="Rennes Centre, 35000", created_by=user_ids[2] if len(user_ids) > 2 else user_ids[0]
            ),
            SiteCreate(
                name="Dépôt Montpellier",
                location="Montpellier Sud, 34000",
                created_by=user_ids[5] if len(user_ids) > 5 else user_ids[0],
            ),
        ]

        created_sites = []
        for site_data in sites_data:
            site = SiteRepository.create_site(conn, site_data)
            if site:
                created_sites.append(site)

        # 7. Créer 10 commandes
        print("\n📋 Création de 10 commandes...")
        orders_data = [
            OrderCreate(
                nbr_items=15,
                status=OrderStatus.PENDING.value,
                invoice_url="https://company.com/invoice/001.pdf",
                supplier_id=1,
                description="Matériel informatique pour nouveau bureau",
                price=2500.00,
                created_by=user_ids[0],
            ),
            OrderCreate(
                nbr_items=8,
                status=OrderStatus.PROCESSING.value,
                invoice_url="https://company.com/invoice/002.pdf",
                supplier_id=2,
                description="Équipements plomberie urgente",
                price=1200.50,
                created_by=user_ids[2] if len(user_ids) > 2 else user_ids[0],
            ),
            OrderCreate(
                nbr_items=25,
                status=OrderStatus.DELIVERED.value,
                invoice_url="https://company.com/invoice/003.pdf",
                supplier_id=3,
                description="Installation électrique complète",
                price=4500.75,
                created_by=user_ids[5] if len(user_ids) > 5 else user_ids[0],
            ),
            OrderCreate(
                nbr_items=50,
                status=OrderStatus.PENDING.value,
                invoice_url="https://company.com/invoice/004.pdf",
                supplier_id=4,
                description="Fournitures bureau trimestriel",
                price=800.25,
                created_by=user_ids[0],
            ),
            OrderCreate(
                nbr_items=3,
                status=OrderStatus.PROCESSING.value,
                invoice_url="https://company.com/invoice/005.pdf",
                supplier_id=5,
                description="Maintenance système climatisation",
                price=3200.00,
                created_by=user_ids[2] if len(user_ids) > 2 else user_ids[0],
            ),
            OrderCreate(
                nbr_items=12,
                status=OrderStatus.CANCELLED.value,
                invoice_url="https://company.com/invoice/006.pdf",
                supplier_id=6,
                description="Mobilier bureau - annulée",
                price=1800.00,
                created_by=user_ids[5] if len(user_ids) > 5 else user_ids[0],
            ),
            OrderCreate(
                nbr_items=35,
                status=OrderStatus.DELIVERED.value,
                invoice_url="https://company.com/invoice/007.pdf",
                supplier_id=7,
                description="Outillage professionnel",
                price=2100.80,
                created_by=user_ids[0],
            ),
            OrderCreate(
                nbr_items=5,
                status=OrderStatus.PENDING.value,
                invoice_url="https://company.com/invoice/008.pdf",
                supplier_id=8,
                description="Équipements sécurité",
                price=950.00,
                created_by=user_ids[2] if len(user_ids) > 2 else user_ids[0],
            ),
            OrderCreate(
                nbr_items=20,
                status=OrderStatus.PROCESSING.value,
                invoice_url="https://company.com/invoice/009.pdf",
                supplier_id=9,
                description="Contrat maintenance préventive",
                price=1500.00,
                created_by=user_ids[5] if len(user_ids) > 5 else user_ids[0],
            ),
            OrderCreate(
                nbr_items=10,
                status=OrderStatus.DELIVERED.value,
                invoice_url="https://company.com/invoice/010.pdf",
                supplier_id=10,
                description="Solutions écologiques",
                price=3500.50,
                created_by=user_ids[0],
            ),
        ]

        created_orders = []
        for order_data in orders_data:
            order = OrderRepository.create_order(conn, order_data)
            if order:
                created_orders.append(order)

        # 8. Créer 10 produits
        print("\n📦 Création de 10 produits...")
        products_data = [
            ProductCreate(
                name="MacBook Pro 16",
                brand="Apple",
                description="Ordinateur portable professionnel",
                price=2899.00,
                reference="MBP-16-M3-512",
                specifications={"cpu": "M3 Pro", "ram": "18GB", "storage": "512GB SSD"},
                supplier_id=1,
                order_id=1,
                stock_site_id=1,
            ),
            ProductCreate(
                name="Robinet Thermostatique",
                brand="Grohe",
                description="Robinet thermostatique haute qualité",
                price=245.50,
                reference="GRH-THERM-001",
                specifications={"material": "Laiton chromé", "warranty": "10 ans"},
                supplier_id=2,
                order_id=2,
                stock_site_id=2,
            ),
            ProductCreate(
                name="Tableau Électrique 4 Rangées",
                brand="Schneider",
                description="Tableau électrique modulaire",
                price=189.99,
                reference="SCH-TAB-4R",
                specifications={"modules": "52", "protection": "IP30"},
                supplier_id=3,
                order_id=3,
                stock_site_id=3,
            ),
            ProductCreate(
                name="Ramette Papier A4",
                brand="Clairefontaine",
                description="Papier blanc 80g/m²",
                price=4.99,
                reference="CF-A4-80G",
                specifications={"weight": "80g/m²", "sheets": "500", "format": "A4"},
                supplier_id=4,
                order_id=4,
                stock_site_id=4,
            ),
            ProductCreate(
                name="Climatiseur Réversible",
                brand="Daikin",
                description="Climatiseur split réversible",
                price=1299.00,
                reference="DAI-SPLIT-35",
                specifications={
                    "power": "3.5kW",
                    "energy_class": "A++",
                    "type": "Réversible",
                },
                supplier_id=5,
                order_id=5,
                stock_site_id=5,
            ),
            ProductCreate(
                name="Bureau Ergonomique",
                brand="Herman Miller",
                description="Bureau réglable en hauteur",
                price=899.00,
                reference="HM-DESK-ADJ",
                specifications={
                    "height_range": "65-130cm",
                    "material": "Chêne",
                    "electric": True,
                },
                supplier_id=6,
                order_id=6,
                stock_site_id=6,
            ),
            ProductCreate(
                name="Perceuse Visseuse",
                brand="Bosch",
                description="Perceuse sans fil 18V",
                price=159.99,
                reference="BSH-PSR-18",
                specifications={"voltage": "18V", "torque": "60Nm", "battery": "2Ah"},
                supplier_id=7,
                order_id=7,
                stock_site_id=7,
            ),
            ProductCreate(
                name="Caméra Surveillance IP",
                brand="Hikvision",
                description="Caméra IP extérieure 4K",
                price=289.00,
                reference="HIK-IP-4K",
                specifications={"resolution": "4K", "night_vision": True, "poe": True},
                supplier_id=8,
                order_id=8,
                stock_site_id=8,
            ),
            ProductCreate(
                name="Kit Maintenance HVAC",
                brand="Carrier",
                description="Kit complet maintenance climatisation",
                price=125.50,
                reference="CAR-MAINT-KIT",
                specifications={
                    "filters": "3",
                    "tools": "Professional",
                    "manual": True,
                },
                supplier_id=9,
                order_id=9,
                stock_site_id=9,
            ),
            ProductCreate(
                name="Panneau Solaire 400W",
                brand="SunPower",
                description="Panneau photovoltaïque haute efficacité",
                price=459.99,
                reference="SUN-PV-400",
                specifications={
                    "power": "400W",
                    "efficiency": "22.8%",
                    "warranty": "25 ans",
                },
                supplier_id=10,
                order_id=10,
                stock_site_id=10,
            ),
        ]

        created_products = []
        for product_data in products_data:
            product = ProductRepository.create_product(conn, product_data)
            if product:
                created_products.append(product)

        # 9. Créer 10 tâches
        print("\n✅ Création de 10 tâches...")
        tasks_data = [
            TaskCreate(
                title="Installation réseau informatique",
                description="Mise en place du réseau WiFi et câblé pour le nouveau bureau",
                assigned_to=user_ids[1] if len(user_ids) > 1 else user_ids[0],
                status=TaskStatus.IN_PROGRESS.value,
                priority=3,
                start_date=dt.datetime.now(),
                due_date=dt.datetime.now() + dt.timedelta(days=3),
                created_by=user_ids[0],
                completion_percentage=25,
                estimated_time=480,
            ),
            TaskCreate(
                title="Réparation fuite salle de bain",
                description="Intervention urgente pour fuite robinet principal",
                assigned_to=user_ids[1] if len(user_ids) > 1 else user_ids[0],
                status=TaskStatus.PENDING.value,
                priority=5,
                start_date=dt.datetime.now(),
                due_date=dt.datetime.now() + dt.timedelta(hours=4),
                created_by=user_ids[2] if len(user_ids) > 2 else user_ids[0],
                completion_percentage=0,
                estimated_time=120,
            ),
            TaskCreate(
                title="Maintenance tableau électrique",
                description="Contrôle et mise aux normes du tableau principal",
                assigned_to=user_ids[2] if len(user_ids) > 2 else user_ids[0],
                status=TaskStatus.COMPLETED.value,
                priority=4,
                start_date=dt.datetime.now() - dt.timedelta(days=2),
                due_date=dt.datetime.now() - dt.timedelta(days=1),
                created_by=user_ids[5] if len(user_ids) > 5 else user_ids[0],
                completion_percentage=100,
                estimated_time=240,
            ),
            TaskCreate(
                title="Commande fournitures bureau",
                description="Réapprovisionner les stocks de papeterie",
                assigned_to=user_ids[8] if len(user_ids) > 8 else user_ids[0],
                status=TaskStatus.PENDING.value,
                priority=2,
                start_date=dt.datetime.now() + dt.timedelta(days=1),
                due_date=dt.datetime.now() + dt.timedelta(days=5),
                created_by=user_ids[0],
                completion_percentage=0,
                estimated_time=60,
            ),
            TaskCreate(
                title="Révision climatisation",
                description="Maintenance préventive avant période estivale",
                assigned_to=user_ids[4] if len(user_ids) > 4 else user_ids[0],
                status=TaskStatus.IN_PROGRESS.value,
                priority=3,
                start_date=dt.datetime.now(),
                due_date=dt.datetime.now() + dt.timedelta(days=2),
                created_by=user_ids[2] if len(user_ids) > 2 else user_ids[0],
                completion_percentage=60,
                estimated_time=360,
            ),
            TaskCreate(
                title="Assemblage mobilier bureau",
                description="Montage des nouveaux postes de travail",
                assigned_to=user_ids[7] if len(user_ids) > 7 else user_ids[0],
                status=TaskStatus.CANCELLED.value,
                priority=2,
                start_date=dt.datetime.now() - dt.timedelta(days=1),
                due_date=dt.datetime.now() + dt.timedelta(days=1),
                created_by=user_ids[5] if len(user_ids) > 5 else user_ids[0],
                completion_percentage=0,
                estimated_time=180,
            ),
            TaskCreate(
                title="Installation caméras sécurité",
                description="Pose du système de vidéosurveillance",
                assigned_to=user_ids[1] if len(user_ids) > 1 else user_ids[0],
                status=TaskStatus.PENDING.value,
                priority=4,
                start_date=dt.datetime.now() + dt.timedelta(days=2),
                due_date=dt.datetime.now() + dt.timedelta(days=5),
                created_by=user_ids[0],
                completion_percentage=0,
                estimated_time=300,
            ),
            TaskCreate(
                title="Diagnostic performance énergétique",
                description="Audit énergétique complet du bâtiment",
                assigned_to=user_ids[4] if len(user_ids) > 4 else user_ids[0],
                status=TaskStatus.IN_PROGRESS.value,
                priority=3,
                start_date=dt.datetime.now() - dt.timedelta(days=1),
                due_date=dt.datetime.now() + dt.timedelta(days=4),
                created_by=user_ids[2] if len(user_ids) > 2 else user_ids[0],
                completion_percentage=40,
                estimated_time=420,
            ),
            TaskCreate(
                title="Formation utilisation outils",
                description="Formation équipe sur nouveaux équipements",
                assigned_to=user_ids[3] if len(user_ids) > 3 else user_ids[0],
                status=TaskStatus.PENDING.value,
                priority=2,
                start_date=dt.datetime.now() + dt.timedelta(days=7),
                due_date=dt.datetime.now() + dt.timedelta(days=8),
                created_by=user_ids[5] if len(user_ids) > 5 else user_ids[0],
                completion_percentage=0,
                estimated_time=240,
            ),
            TaskCreate(
                title="Installation panneaux solaires",
                description="Pose et raccordement système photovoltaïque",
                assigned_to=user_ids[2] if len(user_ids) > 2 else user_ids[0],
                status=TaskStatus.PENDING.value,
                priority=3,
                start_date=dt.datetime.now() + dt.timedelta(days=10),
                due_date=dt.datetime.now() + dt.timedelta(days=15),
                created_by=user_ids[0],
                completion_percentage=0,
                estimated_time=600,
            ),
        ]

        for task_data in tasks_data:
            TaskRepository.create_task(conn, task_data)

        print("\n🎉 Toutes les données ont été créées avec succès !")
        print("📊 Résumé :")
        print("   - 10 Utilisateurs")
        print("   - 10 Fournisseurs")
        print("   - 10 Sites")
        print("   - 10 Commandes")
        print("   - 10 Produits")
        print("   - 10 Tâches")

    except Exception as e:
        print(f"❌ Erreur dans le programme principal : {e}")

    finally:
        # 9. Fermer la connexion
        conn.close()
        print("\n🔒 Connexion fermée")


if __name__ == "__main__":
    main()
