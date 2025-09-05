from mcp_init import mcp, db
from typing import Optional
import json
from datetime import datetime

@mcp.tool()
def update_user(user_id: str, first_name: Optional[str] = None, last_name: Optional[str] = None, 
                email: Optional[str] = None, phone: Optional[str] = None, role: Optional[str] = None, 
                specialization: Optional[str] = None, is_active: Optional[bool] = None) -> str:
    """
    Modifie un utilisateur existant dans la base de données.
    
    PARAMÈTRES OBLIGATOIRES:
    - user_id: ID de l'utilisateur à modifier (string, doit exister dans users)
    
    PARAMÈTRES OPTIONNELS (seuls les paramètres fournis seront modifiés):
    - first_name: Nouveau prénom (string, non vide si fourni)
    - last_name: Nouveau nom de famille (string, non vide si fourni)
    - email: Nouvelle adresse email (string, format email valide, unique)
    - phone: Nouveau numéro de téléphone (string)
    - role: Nouveau rôle dans l'entreprise (string)
      OPTIONS EXACTES: 'worker', 'chief', 'manager', 'admin'
    - specialization: Nouvelle spécialisation/métier (string)
      EXEMPLES: 'electrician', 'plumber', 'mason', 'painter', 'roofer', 'carpenter'
    - is_active: Nouveau statut actif/inactif (boolean: true/false)
    
    VALIDATIONS AUTOMATIQUES:
    - user_id doit exister dans la base
    - Prénom et nom non vides si fournis
    - Format email valide si fourni
    - Email unique dans la base si fourni
    - Rôle parmi les valeurs autorisées si fourni
    - Mise à jour automatique de updated_at
    
    EXEMPLES D'UTILISATION:
    - Changer nom: update_user("user123", first_name="Jean", last_name="Dupont")
    - Changer rôle: update_user("user123", role="manager")
    - Désactiver utilisateur: update_user("user123", is_active=false)
    - Changer spécialisation: update_user("user123", specialization="electrician")
    - Modification complète: update_user("user123", first_name="Pierre", email="pierre@email.com", role="chief", is_active=true)
    - Mettre à jour contact: update_user("user123", email="nouveau@email.com", phone="0123456789")
    
    RETOUR:
    JSON avec les informations de l'utilisateur modifié ou message d'erreur.
    """
    print(f"🔧 Modifying user '{user_id}' with params: first_name={first_name}, last_name={last_name}, email={email}, phone={phone}, role={role}, specialization={specialization}, is_active={is_active}")

    import re
    
    if not user_id or not user_id.strip():
        return "❌ Erreur: user_id est obligatoire et ne peut pas être vide."
    
    user_id = user_id.strip()
    
    update_params = [first_name, last_name, email, phone, role, specialization, is_active]
    if all(param is None for param in update_params):
        return "❌ Erreur: Au moins un paramètre à modifier doit être fourni."
    
    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            return f"❌ Erreur: L'utilisateur avec l'ID '{user_id}' n'existe pas."
        
        update_fields = []
        update_values = []
        
        if first_name is not None:
            if not first_name or not first_name.strip():
                return "❌ Erreur: Le prénom ne peut pas être vide."
            update_fields.append("first_name = %s")
            update_values.append(first_name.strip())
        
        if last_name is not None:
            if not last_name or not last_name.strip():
                return "❌ Erreur: Le nom de famille ne peut pas être vide."
            update_fields.append("last_name = %s")
            update_values.append(last_name.strip())
        
        if email is not None:
            if not email or not email.strip():
                return "❌ Erreur: L'email ne peut pas être vide."
            
            email = email.strip().lower()
            
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return "❌ Erreur: Format d'email invalide."
            
            cursor.execute("SELECT id FROM users WHERE email = %s AND id != %s", (email, user_id))
            if cursor.fetchone():
                return f"❌ Erreur: L'email '{email}' est déjà utilisé par un autre utilisateur."
            
            update_fields.append("email = %s")
            update_values.append(email)
        
        if phone is not None:
            phone_value = phone.strip() if phone else None
            update_fields.append("phone = %s")
            update_values.append(phone_value)
        
        if role is not None:
            valid_roles = ['worker', 'chief', 'manager', 'admin']
            if role not in valid_roles:
                return f"❌ Erreur: Rôle '{role}' invalide. Rôles possibles: {valid_roles}"
            update_fields.append("role = %s")
            update_values.append(role)
        
        if specialization is not None:
            spec_value = specialization.strip() if specialization else None
            update_fields.append("specialization = %s")
            update_values.append(spec_value)
        
        if is_active is not None:
            if not isinstance(is_active, bool):
                return "❌ Erreur: is_active doit être un booléen (true/false)."
            update_fields.append("is_active = %s")
            update_values.append(is_active)
        
        if update_fields:
            update_fields.append("updated_at = %s")
            update_values.append(datetime.now())
            
            update_values.append(user_id)
            
            update_query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
            cursor.execute(update_query, update_values)
            db.commit()
            
            cursor.execute("""
                SELECT id, first_name, last_name, email, phone, role, specialization,
                       created_at, updated_at, is_active
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
                    "message": f"✅ Utilisateur '{user_id}' modifié avec succès.",
                    "user": user_dict,
                    "fields_updated": len(update_fields) - 1
                }
                return json.dumps(success_result, indent=2, ensure_ascii=False)
            else:
                return "❌ Erreur: Utilisateur modifié mais impossible de le récupérer."
        else:
            return "❌ Erreur: Aucun champ valide à mettre à jour."
            
    except Exception as e:
        db.rollback()
        return f"❌ Erreur base de données: {str(e)}"
    finally:
        cursor.close()