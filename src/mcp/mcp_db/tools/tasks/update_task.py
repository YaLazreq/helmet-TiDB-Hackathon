from mcp_init import mcp, db
from typing import Optional
import json
from datetime import datetime

@mcp.tool()
def update_task(task_id: int, title: Optional[str] = None, description: Optional[str] = None, 
                assigned_to: Optional[int] = None, estimated_time: Optional[int] = None, 
                start_date: Optional[str] = None, due_date: Optional[str] = None, 
                priority: Optional[int] = None, status: Optional[str] = None, 
                completion_percentage: Optional[int] = None) -> str:
    """
    Modifie une tâche existante dans la base de données.
    
    PARAMÈTRES OBLIGATOIRES:
    - task_id: ID de la tâche à modifier (int, doit exister dans tasks)
    
    PARAMÈTRES OPTIONNELS (seuls les paramètres fournis seront modifiés):
    - title: Nouveau titre de la tâche (string, non vide si fourni)
    - description: Nouvelle description détaillée (string, non vide si fourni)
    - assigned_to: Nouvel ID de l'utilisateur assigné (int, doit exister dans users)
    - estimated_time: Nouveau temps estimé en minutes (int, positif ou null)
    - start_date: Nouvelle date/heure de début (string format: "YYYY-MM-DD HH:MM:SS" ou "YYYY-MM-DD", null pour supprimer)
    - due_date: Nouvelle date/heure d'échéance (string format: "YYYY-MM-DD HH:MM:SS" ou "YYYY-MM-DD", null pour supprimer)
    - priority: Nouveau niveau de priorité (int, 1=haute, 2=normale, 3=basse, 4=très basse, 5=critique)
    - status: Nouveau statut de la tâche (string)
      OPTIONS: 'pending', 'in_progress', 'completed', 'cancelled', 'on_hold'
    - completion_percentage: Nouveau pourcentage d'achèvement (int 0-100)
    
    VALIDATIONS AUTOMATIQUES:
    - task_id doit exister dans la base
    - Titre et description non vides si fournis
    - assigned_to doit exister dans users si fourni
    - Dates au format correct si fournies
    - Priorité entre 1 et 5 si fournie
    - Pourcentage entre 0 et 100 si fourni
    - Mise à jour automatique de updated_at
    
    EXEMPLES D'UTILISATION:
    - Changer titre: update_task(1, title="Nouveau titre")
    - Changer statut: update_task(1, status="in_progress", completion_percentage=50)
    - Modification complète: update_task(1, title="Nouveau titre", description="Nouvelle description", assigned_to=2, priority=1, status="in_progress")
    - Supprimer dates: update_task(1, start_date=None, due_date=None)
    - Mettre à jour dates: update_task(1, start_date="2024-12-02", due_date="2024-12-03 17:00:00")
    
    RETOUR:
    JSON avec les informations de la tâche modifiée ou message d'erreur.
    """
    
    if not isinstance(task_id, int) or task_id <= 0:
        return "❌ Erreur: task_id doit être un ID de tâche valide (entier positif)."
    
    update_params = [title, description, assigned_to, estimated_time, start_date, due_date, priority, status, completion_percentage]
    if all(param is None for param in update_params):
        return "❌ Erreur: Au moins un paramètre à modifier doit être fourni."
    
    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
        if not cursor.fetchone():
            return f"❌ Erreur: La tâche avec l'ID {task_id} n'existe pas."
        
        update_fields = []
        update_values = []
        
        if title is not None:
            if not title or not title.strip():
                return "❌ Erreur: Le titre ne peut pas être vide."
            update_fields.append("title = %s")
            update_values.append(title.strip())
        
        if description is not None:
            if not description or not description.strip():
                return "❌ Erreur: La description ne peut pas être vide."
            update_fields.append("description = %s")
            update_values.append(description.strip())
        
        if assigned_to is not None:
            if not isinstance(assigned_to, int) or assigned_to <= 0:
                return "❌ Erreur: assigned_to doit être un ID utilisateur valide (entier positif)."
            
            cursor.execute("SELECT id FROM users WHERE id = %s", (assigned_to,))
            if not cursor.fetchone():
                return f"❌ Erreur: L'utilisateur assigné (ID: {assigned_to}) n'existe pas."
            
            update_fields.append("assigned_to = %s")
            update_values.append(assigned_to)
        
        if estimated_time is not None:
            if not isinstance(estimated_time, int) or estimated_time <= 0:
                return "❌ Erreur: Le temps estimé doit être un nombre de minutes positif."
            update_fields.append("estimated_time = %s")
            update_values.append(estimated_time)
        
        if priority is not None:
            if priority not in [1, 2, 3, 4, 5]:
                return "❌ Erreur: La priorité doit être entre 1 (haute) et 5 (très basse)."
            update_fields.append("priority = %s")
            update_values.append(priority)
        
        if status is not None:
            valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled', 'on_hold']
            if status not in valid_statuses:
                return f"❌ Erreur: Statut '{status}' invalide. Statuts possibles: {valid_statuses}"
            update_fields.append("status = %s")
            update_values.append(status)
        
        if completion_percentage is not None:
            if not isinstance(completion_percentage, int) or completion_percentage < 0 or completion_percentage > 100:
                return "❌ Erreur: Le pourcentage d'achèvement doit être entre 0 et 100."
            update_fields.append("completion_percentage = %s")
            update_values.append(completion_percentage)
        
        if start_date is not None:
            if start_date == "":
                start_date = None
            
            if start_date is None:
                update_fields.append("start_date = %s")
                update_values.append(None)
            else:
                try:
                    if len(start_date) == 10:
                        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                    elif len(start_date) == 19:
                        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
                    else:
                        return "❌ Erreur: Format de start_date invalide. Utilisez 'YYYY-MM-DD' ou 'YYYY-MM-DD HH:MM:SS'."
                    update_fields.append("start_date = %s")
                    update_values.append(start_date_obj)
                except ValueError:
                    return "❌ Erreur: Format de start_date invalide. Utilisez 'YYYY-MM-DD' ou 'YYYY-MM-DD HH:MM:SS'."
        
        if due_date is not None:
            if due_date == "":
                due_date = None
            
            if due_date is None:
                update_fields.append("due_date = %s")
                update_values.append(None)
            else:
                try:
                    if len(due_date) == 10:
                        due_date_obj = datetime.strptime(due_date, "%Y-%m-%d")
                    elif len(due_date) == 19:
                        due_date_obj = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
                    else:
                        return "❌ Erreur: Format de due_date invalide. Utilisez 'YYYY-MM-DD' ou 'YYYY-MM-DD HH:MM:SS'."
                    update_fields.append("due_date = %s")
                    update_values.append(due_date_obj)
                except ValueError:
                    return "❌ Erreur: Format de due_date invalide. Utilisez 'YYYY-MM-DD' ou 'YYYY-MM-DD HH:MM:SS'."
        
        if start_date is not None and due_date is not None and start_date and due_date:
            current_start = None
            current_due = None
            
            if start_date is None:
                cursor.execute("SELECT start_date FROM tasks WHERE id = %s", (task_id,))
                result = cursor.fetchone()
                current_start = result[0] if result else None
            
            if due_date is None:
                cursor.execute("SELECT due_date FROM tasks WHERE id = %s", (task_id,))
                result = cursor.fetchone()
                current_due = result[0] if result else None
            
            check_start = start_date_obj if 'start_date_obj' in locals() else current_start
            check_due = due_date_obj if 'due_date_obj' in locals() else current_due
            
            if check_start and check_due and check_start >= check_due:
                return "❌ Erreur: La date de début doit être antérieure à la date d'échéance."
        
        if update_fields:
            update_fields.append("updated_at = %s")
            update_values.append(datetime.now())
            
            update_values.append(task_id)
            
            update_query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = %s"
            cursor.execute(update_query, update_values)
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
                    "message": f"✅ Tâche ID {task_id} modifiée avec succès.",
                    "task": task_dict,
                    "fields_updated": len(update_fields) - 1  # -1 pour ne pas compter updated_at
                }
                return json.dumps(success_result, indent=2, ensure_ascii=False)
            else:
                return "❌ Erreur: Tâche modifiée mais impossible de la récupérer."
        else:
            return "❌ Erreur: Aucun champ valide à mettre à jour."
            
    except Exception as e:
        db.rollback()
        return f"❌ Erreur base de données: {str(e)}"
    finally:
        cursor.close()
