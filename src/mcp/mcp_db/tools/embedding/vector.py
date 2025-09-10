import os
from typing import List, Dict, Any
from dataclasses import dataclass

from tidb_vector.integrations import TiDBVectorClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv


@dataclass
class VectorSearchResult:
    """Result from vector search operation"""

    id: str
    text: str
    metadata: Dict[str, Any]
    distance: float


class TiDBVectorManager:
    """
    TiDB Vector Manager for creating and searching vectors in TiDB.
    Designed to work with tasks and users tables containing vector columns.
    """

    def __init__(
        self, model_name: str = "sentence-transformers/msmarco-MiniLM-L12-cos-v5"
    ):
        load_dotenv()

        # Initialize embedding model
        self.embed_model = SentenceTransformer(model_name, trust_remote_code=True)
        self.embed_model_dims = self.embed_model.get_sentence_embedding_dimension()

        # Initialize TiDB connection parameters
        self.connection_string = self._build_connection_string()

        # Vector clients for different tables
        self._tasks_vector_client = None
        self._users_vector_client = None

    def _build_connection_string(self) -> str:
        """Build TiDB connection string from environment variables"""
        host = os.getenv("TIDB_HOST")
        port = os.getenv("TIDB_PORT", "4000")
        user = os.getenv("TIDB_USER")
        password = os.getenv("TIDB_PASSWORD")
        database = os.getenv("TIDB_DATABASE")

        if not all([host, user, password, database]):
            raise ValueError(
                "Missing required TiDB connection parameters in environment variables"
            )

        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?ssl_verify_cert=true&ssl_verify_identity=false"

    def text_to_embedding(self, text: str) -> List[float]:
        """Generate vector embedding for given text"""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        embedding = self.embed_model.encode(text)
        return embedding.tolist()

    def get_tasks_vector_client(self) -> TiDBVectorClient:
        """Get or create vector client for tasks table"""
        if self._tasks_vector_client is None:
            self._tasks_vector_client = TiDBVectorClient(
                table_name="task_vectors",
                connection_string=self.connection_string,
                vector_dimension=self.embed_model_dims,
                drop_existing_table=False,
            )
        return self._tasks_vector_client

    def get_users_vector_client(self) -> TiDBVectorClient:
        """Get or create vector client for users table"""
        if self._users_vector_client is None:
            self._users_vector_client = TiDBVectorClient(
                table_name="user_vectors",
                connection_string=self.connection_string,
                vector_dimension=self.embed_model_dims,
                drop_existing_table=False,
            )
        return self._users_vector_client

    def create_task_vector(self, task_id: int, task_data: Dict[str, Any]) -> str:
        """
        Create vector embedding for a task based on its attributes
        """
        # Combine relevant task fields into searchable text
        searchable_text = self._build_task_searchable_text(task_data)

        # Generate embedding
        embedding = self.text_to_embedding(searchable_text)

        # Store in vector table
        vector_client = self.get_tasks_vector_client()

        # Use task_id as the document ID
        doc_id = f"task_{task_id}"

        vector_client.insert(
            ids=[doc_id],
            texts=[searchable_text],
            embeddings=[embedding],
            metadatas=[
                {
                    "task_id": task_id,
                    "title": task_data.get("title", ""),
                    "trade_category": task_data.get("trade_category", ""),
                    "priority": task_data.get("priority", 0),
                    "status": task_data.get("status", "pending"),
                }
            ],
        )

        return doc_id

    def create_user_vector(self, user_id: int, user_data: Dict[str, Any]) -> str:
        """
        Create vector embedding for a user based on their skills and attributes
        """
        # Combine relevant user fields into searchable text
        searchable_text = self._build_user_searchable_text(user_data)

        # Generate embedding
        embedding = self.text_to_embedding(searchable_text)

        # Store in vector table
        vector_client = self.get_users_vector_client()

        # Use user_id as the document ID
        doc_id = f"user_{user_id}"

        vector_client.insert(
            ids=[doc_id],
            texts=[searchable_text],
            embeddings=[embedding],
            metadatas=[
                {
                    "user_id": user_id,
                    "name": f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
                    "role": user_data.get("role", ""),
                    "primary_skills": user_data.get("primary_skills", []),
                    "trade_categories": user_data.get("trade_categories", []),
                    "experience_years": user_data.get("experience_years", 0),
                }
            ],
        )

        return doc_id

    def search_similar_tasks(self, query: str, k: int = 5) -> List[VectorSearchResult]:
        """
        Search for tasks similar to the query
        """
        query_embedding = self.text_to_embedding(query)
        vector_client = self.get_tasks_vector_client()

        results = vector_client.query(query_embedding, k=k)

        return [
            VectorSearchResult(
                id=result.id,
                text=result.document,
                metadata=result.metadata,
                distance=result.distance,
            )
            for result in results
        ]

    def search_similar_users(self, query: str, k: int = 5) -> List[VectorSearchResult]:
        """
        Search for users with skills similar to the query
        """
        query_embedding = self.text_to_embedding(query)
        vector_client = self.get_users_vector_client()

        results = vector_client.query(query_embedding, k=k)

        return [
            VectorSearchResult(
                id=result.id,
                text=result.document,
                metadata=result.metadata,
                distance=result.distance,
            )
            for result in results
        ]

    def find_best_workers_for_task(
        self, task_description: str, k: int = 3
    ) -> List[VectorSearchResult]:
        """
        Find the best workers for a given task description
        """
        return self.search_similar_users(task_description, k=k)

    def find_similar_tasks(
        self, task_description: str, k: int = 5
    ) -> List[VectorSearchResult]:
        """
        Find tasks similar to the given description
        """
        return self.search_similar_tasks(task_description, k=k)

    def _build_task_searchable_text(self, task_data: Dict[str, Any]) -> str:
        """Build searchable text from task data"""
        components = []

        # Title and description
        if title := task_data.get("title"):
            components.append(f"Title: {title}")
        if description := task_data.get("description"):
            components.append(f"Description: {description}")

        # Location info
        if room := task_data.get("room"):
            components.append(f"Room: {room}")
        if building_section := task_data.get("building_section"):
            components.append(f"Building: {building_section}")
        if zone_type := task_data.get("zone_type"):
            components.append(f"Zone: {zone_type}")

        # Skills and trade
        if trade_category := task_data.get("trade_category"):
            components.append(f"Trade: {trade_category}")
        if skill_requirements := task_data.get("skill_requirements"):
            if isinstance(skill_requirements, list):
                components.append(f"Skills needed: {', '.join(skill_requirements)}")
            elif isinstance(skill_requirements, str):
                components.append(f"Skills needed: {skill_requirements}")

        # Materials and equipment
        if required_materials := task_data.get("required_materials"):
            if isinstance(required_materials, list):
                materials = [
                    mat.get("nom", str(mat)) if isinstance(mat, dict) else str(mat)
                    for mat in required_materials
                ]
                components.append(f"Materials: {', '.join(materials)}")

        if required_equipment := task_data.get("required_equipment"):
            if isinstance(required_equipment, list):
                components.append(f"Equipment: {', '.join(required_equipment)}")

        # Additional context
        if notes := task_data.get("notes"):
            components.append(f"Notes: {notes}")

        return " | ".join(components)

    def _build_user_searchable_text(self, user_data: Dict[str, Any]) -> str:
        """Build searchable text from user data"""
        components = []

        # Basic info
        name_parts = []
        if first_name := user_data.get("first_name"):
            name_parts.append(first_name)
        if last_name := user_data.get("last_name"):
            name_parts.append(last_name)
        if name_parts:
            components.append(f"Name: {' '.join(name_parts)}")

        if role := user_data.get("role"):
            components.append(f"Role: {role}")

        # Skills and experience
        if primary_skills := user_data.get("primary_skills"):
            if isinstance(primary_skills, list):
                components.append(f"Primary skills: {', '.join(primary_skills)}")

        if secondary_skills := user_data.get("secondary_skills"):
            if isinstance(secondary_skills, list):
                components.append(f"Secondary skills: {', '.join(secondary_skills)}")

        if trade_categories := user_data.get("trade_categories"):
            if isinstance(trade_categories, list):
                components.append(f"Trade categories: {', '.join(trade_categories)}")

        if experience_years := user_data.get("experience_years"):
            components.append(f"Experience: {experience_years} years")

        if skill_levels := user_data.get("skill_levels"):
            if isinstance(skill_levels, dict):
                skill_descriptions = [
                    f"{skill} (level {level})" for skill, level in skill_levels.items()
                ]
                components.append(f"Skill levels: {', '.join(skill_descriptions)}")

        # Equipment and certifications
        if equipment_mastery := user_data.get("equipment_mastery"):
            if isinstance(equipment_mastery, list):
                components.append(f"Equipment mastery: {', '.join(equipment_mastery)}")

        if certifications := user_data.get("certifications"):
            if isinstance(certifications, list):
                components.append(f"Certifications: {', '.join(certifications)}")

        if project_experience := user_data.get("project_experience"):
            if isinstance(project_experience, list):
                components.append(
                    f"Project experience: {', '.join(project_experience)}"
                )

        return " | ".join(components)
