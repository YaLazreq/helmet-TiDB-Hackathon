from mcp_init import mcp, db
from typing import Optional
import json
from datetime import datetime

@mcp.tool()
def search_tasks(id: Optional[str] = None, title: Optional[str] = None, description: Optional[str] = None, assigned_to: Optional[str] = None, created_by: Optional[str] = None, priority: Optional[str] = None, status: Optional[str] = None, start_date: Optional[str] = None, due_date: Optional[str] = None, min_estimated_hours: Optional[float] = None, max_estimated_hours: Optional[float] = None, min_completion: Optional[int] = None, max_completion: Optional[int] = None, overdue_only: Optional[bool] = None, limit: Optional[int] = 20) -> str:
    """
    Recherche des tâches selon différents critères.
    
    PARAMÈTRES DISPONIBLES:
    
    IDENTIFICATION:
    - id: Identifiant unique de la tâche (string)
    - title: Titre de la tâche (string, recherche partielle possible)
    - description: Description de la tâche (string, recherche partielle possible)
    
    ASSIGNATION:
    - assigned_to: ID ou nom de l'utilisateur assigné (string)
    - created_by: ID ou nom de l'utilisateur créateur (string)
    
    PRIORITÉ:
    - priority: Niveau de priorité (1=Low, 2=Medium, 3=High)
    
    STATUT:
    - status: État d'avancement de la tâche (string)
      EXEMPLES: 'pending', 'in_progress', 'completed', 'cancelled'
    
    DATES:
    - start_date: Date de début (format: 'YYYY-MM-DD')
    - due_date: Date d'échéance (format: 'YYYY-MM-DD')
    - overdue_only: Uniquement les tâches en retard (boolean: true/false)
    
    ESTIMATION & AVANCEMENT:
    - min_estimated_hours: Durée estimée minimum (heures, calculée depuis estimated_time en minutes)
    - max_estimated_hours: Durée estimée maximum (heures, calculée depuis estimated_time en minutes)
    - min_completion: Pourcentage d'avancement minimum (0-100)
    - max_completion: Pourcentage d'avancement maximum (0-100)
    
    AUTRES:
    - limit: Nombre max de résultats (défaut: 20)
    
    EXEMPLES D'UTILISATION:
    - Tâches d'un utilisateur: search_tasks(assigned_to="1")
    - Tâches prioritaires: search_tasks(priority="3")
    - Tâches en cours: search_tasks(status="in_progress")
    - Tâches en retard: search_tasks(overdue_only=true)
    - Tâches presque finies: search_tasks(min_completion=80)
    - Grosses tâches: search_tasks(min_estimated_hours=10)
    - Recherche par titre: search_tasks(title="réparation")
    
    RETOUR:
    JSON avec la liste des tâches trouvées + leurs informations complètes.
    """
    
    if min_completion is not None and (min_completion < 0 or min_completion > 100):
        return f"Erreur. min_completion doit être entre 0 et 100, reçu: {min_completion}"
        
    if max_completion is not None and (max_completion < 0 or max_completion > 100):
        return f"Erreur. max_completion doit être entre 0 et 100, reçu: {max_completion}"
    
    conditions = []
    params = []
    
    if id:
        conditions.append("t.id = %s")
        params.append(id)
        
    if title:
        conditions.append("t.title LIKE %s")
        params.append(f"%{title}%")
        
    if description:
        conditions.append("t.description LIKE %s")
        params.append(f"%{description}%")
        
    if assigned_to:
        conditions.append("(CONCAT(u_assigned.first_name, ' ', u_assigned.last_name) LIKE %s OR t.assigned_to = %s)")
        params.extend([f"%{assigned_to}%", assigned_to])
        
    if created_by:
        conditions.append("(CONCAT(u_creator.first_name, ' ', u_creator.last_name) LIKE %s OR t.created_by = %s)")
        params.extend([f"%{created_by}%", created_by])
        
    if priority:
        conditions.append("t.priority = %s")
        params.append(priority)
        
    if status:
        conditions.append("t.status = %s")
        params.append(status)
        
    if start_date:
        conditions.append("DATE(t.start_date) = %s")
        params.append(start_date)
        
    if due_date:
        conditions.append("DATE(t.due_date) = %s")
        params.append(due_date)
        
    if min_estimated_hours is not None:
        conditions.append("t.estimated_time >= %s")
        params.append(min_estimated_hours * 60)  # Convertir heures en minutes
        
    if max_estimated_hours is not None:
        conditions.append("t.estimated_time <= %s")
        params.append(max_estimated_hours * 60)  # Convertir heures en minutes
        
    if min_completion is not None:
        conditions.append("t.completion_percentage >= %s")
        params.append(min_completion)
        
    if max_completion is not None:
        conditions.append("t.completion_percentage <= %s")
        params.append(max_completion)
        
    if overdue_only:
        conditions.append("t.due_date < NOW() AND t.status NOT IN ('completed', 'cancelled')")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = f"""
    SELECT 
        t.id,
        t.title,
        t.description,
        t.estimated_time,
        t.start_date,
        t.due_date,
        t.priority,
        t.status,
        t.completion_percentage,
        t.assigned_to,
        CONCAT(u_assigned.first_name, ' ', u_assigned.last_name) as assigned_to_name,
        u_assigned.email as assigned_to_email,
        t.created_by,
        CONCAT(u_creator.first_name, ' ', u_creator.last_name) as created_by_name,
        u_creator.email as created_by_email,
        t.created_at,
        t.updated_at
    FROM tasks t
    LEFT JOIN users u_assigned ON t.assigned_to = u_assigned.id
    LEFT JOIN users u_creator ON t.created_by = u_creator.id
    WHERE {where_clause}
    ORDER BY 
        CASE 
            WHEN t.priority = 3 THEN 1  -- High priority
            WHEN t.priority = 2 THEN 2  -- Medium priority
            WHEN t.priority = 1 THEN 3  -- Low priority
            ELSE 4
        END,
        t.due_date ASC,
        t.created_at DESC
    LIMIT {limit or 20}
    """

    cursor = db.cursor(buffered=True)
    try:
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        
        # Convertir en dictionnaires avec gestion des datetime
        tasks_list = []
        for row in results:
            task_dict = {}
            for i, value in enumerate(row):
                if isinstance(value, datetime):
                    task_dict[columns[i]] = value.isoformat()
                else:
                    task_dict[columns[i]] = value
            
            # Calculer les heures estimées depuis les minutes
            if 'estimated_time' in task_dict and task_dict['estimated_time']:
                task_dict['estimated_hours'] = round(task_dict['estimated_time'] / 60, 2)
            else:
                task_dict['estimated_hours'] = 0
                
            tasks_list.append(task_dict)
        
    except Exception as e:
        return f"Erreur base de données: {str(e)}"
    finally:
        cursor.close()
    
    if not tasks_list:
        return "❌ Aucune tâche trouvée avec ces critères."
    
    # Calculs de statistiques
    total_estimated_hours = sum(task.get("estimated_hours", 0) for task in tasks_list)
    avg_completion = sum(task.get("completion_percentage", 0) for task in tasks_list) / len(tasks_list)
    
    status_count = {}
    for task in tasks_list:
        status = task.get("status", "unknown")
        status_count[status] = status_count.get(status, 0) + 1
    
    result = {
        "summary": {
            "total_found": len(tasks_list),
            "total_estimated_hours": round(total_estimated_hours, 2),
            "average_completion": round(avg_completion, 1),
            "status_breakdown": status_count
        },
        "criteria_used": {k: v for k, v in {
            "id": id, "title": title, "description": description,
            "assigned_to": assigned_to, "created_by": created_by,
            "priority": priority, "status": status,
            "start_date": start_date, "due_date": due_date,
            "min_estimated_hours": min_estimated_hours,
            "max_estimated_hours": max_estimated_hours,
            "min_completion": min_completion, "max_completion": max_completion,
            "overdue_only": overdue_only
        }.items() if v is not None},
        "tasks": tasks_list
    }
    
    return json.dumps(result, indent=2, ensure_ascii=False)