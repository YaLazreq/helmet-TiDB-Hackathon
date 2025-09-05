from mcp_init import mcp, db
from typing import Optional
import json
from datetime import datetime

@mcp.tool()
def create_task(title: str, description: str, assigned_to: int, created_by: int, estimated_time: Optional[int] = None, start_date: Optional[str] = None, due_date: Optional[str] = None, priority: int = 2, status: str = "pending", completion_percentage: int = 0) -> str:
    """
    Crée une nouvelle tâche dans la base de données.
    
    PARAMÈTRES OBLIGATOIRES:
    - title: Titre de la tâche (string, non vide)
    - description: Description détaillée de la tâche (string, non vide)
    - assigned_to: ID de l'utilisateur assigné (int, doit exister dans users)
    - created_by: ID de l'utilisateur créateur (int, doit exister dans users)
    
    PARAMÈTRES OPTIONNELS:
    - estimated_time: Temps estimé en minutes (int, optionnel)
    - start_date: Date/heure de début (string format: "YYYY-MM-DD HH:MM:SS" ou "YYYY-MM-DD", optionnel)
    - due_date: Date/heure d'échéance (string format: "YYYY-MM-DD HH:MM:SS" ou "YYYY-MM-DD", optionnel)
    - priority: Niveau de priorité (int, 1=haute, 2=normale, 3=basse, défaut: 2)
    - status: Statut de la tâche (string, défaut: "pending")
      OPTIONS: 'pending', 'in_progress', 'completed', 'cancelled', 'on_hold'
    - completion_percentage: Pourcentage d'achèvement (int 0-100, défaut: 0)
    
    VALIDATIONS AUTOMATIQUES:
    - Titre et description non vides
    - assigned_to et created_by existent dans la table users
    - Dates au format correct
    - Priorité entre 1 et 5
    - Pourcentage entre 0 et 100
    - Horodatage automatique (created_at, updated_at)
    
    EXEMPLES D'UTILISATION:
    - Tâche simple: create_task("Réparer robinet", "Changer le joint", assigned_to=3, created_by=1)
    - Tâche complète: create_task("Plomberie salle de bain", "Réparer fuite et changer robinet", assigned_to=3, created_by=1, estimated_time=240, start_date="2024-12-01 14:00:00", due_date="2024-12-01 18:00:00", priority=3)
    - Avec statut: create_task("Peinture salon", "Peindre les murs en blanc", assigned_to=5, created_by=2, status="in_progress", completion_percentage=25)
    
    RETOUR:
    JSON avec les informations de la tâche créée ou message d'erreur.
    """
    
    if not title or not title.strip():
        return "❌ Erreur: Le titre est obligatoire et ne peut pas être vide."
    
    if not description or not description.strip():
        return "❌ Erreur: La description est obligatoire et ne peut pas être vide."
    
    if not isinstance(assigned_to, int) or assigned_to <= 0:
        return "❌ Erreur: assigned_to doit être un ID utilisateur valide (entier positif)."
    
    if not isinstance(created_by, int) or created_by <= 0:
        return "❌ Erreur: created_by doit être un ID utilisateur valide (entier positif)."
    
    if priority not in [1, 2, 3, 4, 5]:
        return "❌ Erreur: La priorité doit être entre 1 (haute) et 5 (très basse)."
    
    valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled', 'on_hold']
    if status not in valid_statuses:
        return f"❌ Erreur: Statut '{status}' invalide. Statuts possibles: {valid_statuses}"
    
    if not isinstance(completion_percentage, int) or completion_percentage < 0 or completion_percentage > 100:
        return "❌ Erreur: Le pourcentage d'achèvement doit être entre 0 et 100."
    
    if estimated_time is not None and (not isinstance(estimated_time, int) or estimated_time <= 0):
        return "❌ Erreur: Le temps estimé doit être un nombre de minutes positif."
    
    start_date_obj = None
    due_date_obj = None
    
    if start_date:
        try:
            if len(start_date) == 10:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            elif len(start_date) == 19:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            else:
                return "❌ Erreur: Format de start_date invalide. Utilisez 'YYYY-MM-DD' ou 'YYYY-MM-DD HH:MM:SS'."
        except ValueError:
            return "❌ Erreur: Format de start_date invalide. Utilisez 'YYYY-MM-DD' ou 'YYYY-MM-DD HH:MM:SS'."
    
    if due_date:
        try:
            if len(due_date) == 10:
                due_date_obj = datetime.strptime(due_date, "%Y-%m-%d")
            elif len(due_date) == 19:
                due_date_obj = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
            else:
                return "❌ Erreur: Format de due_date invalide. Utilisez 'YYYY-MM-DD' ou 'YYYY-MM-DD HH:MM:SS'."
        except ValueError:
            return "❌ Erreur: Format de due_date invalide. Utilisez 'YYYY-MM-DD' ou 'YYYY-MM-DD HH:MM:SS'."
    
    if start_date_obj and due_date_obj and start_date_obj >= due_date_obj:
        return "❌ Erreur: La date de début doit être antérieure à la date d'échéance."
    
    title = title.strip()
    description = description.strip()
    
    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("SELECT id FROM users WHERE id = %s", (assigned_to,))
        if not cursor.fetchone():
            return f"❌ Erreur: L'utilisateur assigné (ID: {assigned_to}) n'existe pas."
        
        cursor.execute("SELECT id FROM users WHERE id = %s", (created_by,))
        if not cursor.fetchone():
            return f"❌ Erreur: L'utilisateur créateur (ID: {created_by}) n'existe pas."
        
        current_time = datetime.now()
        
        insert_query = """
        INSERT INTO tasks (
            title, description, estimated_time, start_date, due_date, 
            priority, status, completion_percentage, assigned_to, created_by,
            created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            title, description, estimated_time, start_date_obj, due_date_obj,
            priority, status, completion_percentage, assigned_to, created_by,
            current_time, current_time
        )
        
        cursor.execute(insert_query, params)
        task_id = cursor.lastrowid
        db.commit()
        
        cursor.execute("""
            SELECT id, title, description, estimated_time, start_date, due_date,
                   priority, status, completion_percentage, assigned_to, created_by,
                   created_at, updated_at
            FROM tasks WHERE id = %s
        """, (task_id,))
        
        result = cursor.fetchone()
        if result:
            columns = [desc[0] for desc in cursor.description]
            task_dict = {}
            for i, value in enumerate(result):
                if isinstance(value, datetime):
                    task_dict[columns[i]] = value.isoformat()
                else:
                    task_dict[columns[i]] = value
            
            success_result = {
                "success": True,
                "message": f"✅ Tâche '{title}' créée avec succès (ID: {task_id}).",
                "task": task_dict
            }
            return json.dumps(success_result, indent=2, ensure_ascii=False)
        else:
            return "❌ Erreur: Tâche créée mais impossible de la récupérer."
            
    except Exception as e:
        db.rollback()
        return f"❌ Erreur base de données: {str(e)}"
    finally:
        cursor.close()
