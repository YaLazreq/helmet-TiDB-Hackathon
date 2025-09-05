from mcp_init import mcp, db
from typing import Optional
import json
from datetime import datetime
import re

@mcp.tool()
def create_user(first_name: str, last_name: str, email: str, password: str, phone: Optional[str] = None, role: str = "worker", specialization: Optional[str] = None, is_active: bool = True) -> str:
    """
    Crée un nouvel utilisateur dans la base de données.
    
    PARAMÈTRES OBLIGATOIRES:
    - first_name: Prénom de l'utilisateur (string, non vide)
    - last_name: Nom de famille de l'utilisateur (string, non vide)  
    - email: Adresse email valide (string, unique dans la DB)
    - password: Mot de passe (string, non vide)
    
    PARAMÈTRES OPTIONNELS:
    - phone: Numéro de téléphone (string, optionnel)
    - role: Rôle dans l'entreprise (string, défaut: "worker")
      OPTIONS EXACTES: 'worker', 'chief', 'manager', 'admin'
    - specialization: Métier/spécialisation (string, optionnel)
      EXEMPLES: 'electrician', 'plumber', 'mason', 'painter', 'roofer', 'carpenter'
    - is_active: Statut actif (boolean, défaut: true)
    
    VALIDATIONS AUTOMATIQUES:
    - Email valide et unique
    - Rôle dans la liste autorisée
    - Noms non vides
    - Génération automatique d'un ID unique (AUTO_INCREMENT MySQL)
    - Horodatage automatique (created_at, updated_at)
    
    EXEMPLES D'UTILISATION:
    - Utilisateur simple: create_user("Jean", "Dupont", "jean.dupont@email.com", "motdepasse123")
    - Électricien complet: create_user("Marie", "Martin", "marie@email.com", "password456", phone="0123456789", role="worker", specialization="electrician")
    - Manager: create_user("Pierre", "Durand", "pierre@email.com", "admin789", role="manager")
    - Utilisateur inactif: create_user("Paul", "Bernard", "paul@email.com", "pass123", is_active=false)
    
    RETOUR:
    JSON avec les informations de l'utilisateur créé ou message d'erreur.
    """
    
    if not first_name or not first_name.strip():
        return "❌ Erreur: Le prénom est obligatoire et ne peut pas être vide."
    
    if not last_name or not last_name.strip():
        return "❌ Erreur: Le nom de famille est obligatoire et ne peut pas être vide."
    
    if not email or not email.strip():
        return "❌ Erreur: L'email est obligatoire et ne peut pas être vide."
    
    if not password or not password.strip():
        return "❌ Erreur: Le mot de passe est obligatoire et ne peut pas être vide."
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email.strip()):
        return "❌ Erreur: Format d'email invalide."
    
    valid_roles = ['worker', 'chief', 'manager', 'admin']
    if role not in valid_roles:
        return f"❌ Erreur: Rôle '{role}' invalide. Rôles possibles: {valid_roles}"
    
    first_name = first_name.strip()
    last_name = last_name.strip()
    email = email.strip().lower()
    password = password.strip()
    phone = phone.strip() if phone else None
    specialization = specialization.strip() if specialization else None
    
    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return f"❌ Erreur: Un utilisateur avec l'email '{email}' existe déjà."
        
        current_time = datetime.now()
        
        insert_query = """
        INSERT INTO users (
            first_name, last_name, email, password, phone, role, 
            specialization, is_active, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            first_name, last_name, email, password, phone, 
            role, specialization, is_active, current_time, current_time
        )
        
        cursor.execute(insert_query, params)
        user_id = cursor.lastrowid
        db.commit()
        
        cursor.execute("""
            SELECT id, first_name, last_name, email, phone, role, 
                   specialization, is_active, created_at, updated_at
            FROM users WHERE id = %s
        """, (user_id,))
        
        result = cursor.fetchone()
        if result:
            columns = [desc[0] for desc in cursor.description]
            user_dict = {}
            for i, value in enumerate(result):
                if isinstance(value, datetime):
                    user_dict[columns[i]] = value.isoformat()
                else:
                    user_dict[columns[i]] = value
            
            success_result = {
                "success": True,
                "message": f"✅ Utilisateur '{first_name} {last_name}' créé avec succès.",
                "user": user_dict
            }
            return json.dumps(success_result, indent=2, ensure_ascii=False)
        else:
            return "❌ Erreur: Utilisateur créé mais impossible de le récupérer."
            
    except Exception as e:
        db.rollback()
        return f"❌ Erreur base de données: {str(e)}"
    finally:
        cursor.close()