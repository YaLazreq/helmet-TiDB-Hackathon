#!/usr/bin/env python3
"""
Generate task vectors based on title, description, skill_requirements, and trade_category.
This script creates embeddings for all tasks in the dataset and updates them with vector representations.
"""

import sys
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import json

# Add parent directory to path to import mcp_init
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import the local modules
from mcp_init import mcp, get_db_connection
from tools.tasks.repositories.get_tasks import get_tasks
from tools.tasks.repositories.update_task import update_task

class TaskVectorGenerator:
    def __init__(self):
        """Initialize the vector generator with a sentence transformer model."""
        print("Loading sentence transformer model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Model loaded successfully!")
    
    def create_task_text(self, task_data):
        """
        Create a text representation of a task for embedding generation.
        
        Args:
            task_data: Task data dictionary
        
        Returns:
            str: Combined text representation
        """
        # Combine all relevant text fields
        components = []
        
        # Add title
        if 'title' in task_data and task_data['title']:
            components.append(f"Title: {task_data['title']}")
        
        # Add description
        if 'description' in task_data and task_data['description']:
            components.append(f"Description: {task_data['description']}")
        
        # Add skill requirements
        if 'skill_requirements' in task_data and task_data['skill_requirements']:
            if isinstance(task_data['skill_requirements'], list):
                skills = ", ".join(task_data['skill_requirements'])
            else:
                skills = str(task_data['skill_requirements'])
            components.append(f"Skills required: {skills}")
        
        # Add trade category
        if 'trade_category' in task_data and task_data['trade_category']:
            components.append(f"Trade category: {task_data['trade_category']}")
        
        return " | ".join(components)
    
    def generate_vector(self, text):
        """
        Generate embedding vector for given text.
        
        Args:
            text (str): Text to embed
        
        Returns:
            list: Embedding vector as list
        """
        embedding = self.model.encode([text])
        return embedding[0].tolist()
    
    def get_all_tasks_from_db(self):
        """
        Get all tasks directly from database.
        """
        db = get_db_connection()
        if not db:
            print("❌ Database connection failed")
            return []
        
        cursor = db.cursor(buffered=True)
        try:
            cursor.execute("""
                SELECT id, title, description, skill_requirements, trade_category
                FROM tasks
                ORDER BY id
            """)
            
            tasks = []
            for row in cursor.fetchall():
                task_dict = {
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'skill_requirements': json.loads(row[3]) if row[3] else [],
                    'trade_category': row[4]
                }
                tasks.append(task_dict)
            
            return tasks
            
        except Exception as e:
            print(f"Error fetching tasks: {e}")
            return []
        finally:
            cursor.close()
    
    def process_all_tasks(self):
        """
        Process all tasks to generate and update vectors.
        """
        print("Fetching all tasks from database...")
        tasks = self.get_all_tasks_from_db()
        
        if not tasks:
            print("No tasks found!")
            return
        
        print(f"Found {len(tasks)} tasks to process")
        
        successful_updates = 0
        failed_updates = 0
        
        for i, task in enumerate(tasks, 1):
            try:
                print(f"\nProcessing task {i}/{len(tasks)}: {task['title']}")
                
                # Create text representation
                task_text = self.create_task_text(task)
                print(f"Task text: {task_text[:100]}...")
                
                # Generate vector
                vector = self.generate_vector(task_text)
                print(f"Generated vector of dimension: {len(vector)}")
                
                # Update task with vector
                # Convert vector to string format for database storage
                vector_str = json.dumps(vector)
                
                result = update_task(
                    task_id=task['id'],
                    requirements_vector=vector_str
                )
                
                # Check if update was successful
                if result and "✅" in result:
                    print(f"✓ Successfully updated task {task['id']}")
                    successful_updates += 1
                else:
                    print(f"✗ Failed to update task {task['id']}: {result}")
                    failed_updates += 1
                    
            except Exception as e:
                print(f"✗ Error processing task {task['id'] if 'id' in task else 'unknown'}: {str(e)}")
                failed_updates += 1
        
        print(f"\n=== SUMMARY ===")
        print(f"Total tasks processed: {len(tasks)}")
        print(f"Successful updates: {successful_updates}")
        print(f"Failed updates: {failed_updates}")
        
        return successful_updates, failed_updates
    
    def save_sample_vectors(self, filename="sample_task_vectors.json"):
        """
        Generate sample vectors and save them to a JSON file for inspection.
        """
        print("Generating sample vectors...")
        tasks = self.get_all_tasks_from_db()
        
        if not tasks:
            print("No tasks found!")
            return
        
        samples = []
        for task in tasks[:5]:  # First 5 tasks as samples
            task_text = self.create_task_text(task)
            vector = self.generate_vector(task_text)
            
            samples.append({
                "task_id": task['id'],
                "title": task['title'],
                "task_text": task_text,
                "vector_dimension": len(vector),
                "vector_sample": vector[:10],  # First 10 dimensions
                "vector_norm": float(np.linalg.norm(vector))
            })
        
        with open(filename, 'w') as f:
            json.dump(samples, f, indent=2)
        
        print(f"Sample vectors saved to {filename}")


def main():
    """Main function to run the vector generation process."""
    print("=== Task Vector Generation Script ===")
    
    try:
        # Initialize generator
        generator = TaskVectorGenerator()
        
        # Generate sample vectors first (for inspection)
        generator.save_sample_vectors()
        
        # Process all tasks
        successful, failed = generator.process_all_tasks()
        
        if failed == 0:
            print("\n🎉 All tasks updated successfully!")
        else:
            print(f"\n⚠️  {failed} tasks failed to update. Check the logs above.")
            
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()