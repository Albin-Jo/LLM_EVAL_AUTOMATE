import uuid
import random
from typing import Dict, Any, List, Optional
from faker import Faker

fake = Faker()


class DataGenerator:
    """Generate test data for API testing."""

    @staticmethod
    def generate_agent() -> Dict[str, Any]:
        """Generate data for an Agent."""
        return {
            "name": fake.company() + " Agent",
            "description": fake.text(max_nb_chars=200),
            "api_endpoint": fake.url(),
            "domain": random.choice(["healthcare", "finance", "education", "customer_service"]),
            "config": {"temperature": 0.7, "max_tokens": 1000},
            "is_active": True,
            "model_type": random.choice(["gpt-4", "claude-2", "llama-2-70b"]),
            "version": "1.0.0",
            "tags": [fake.word() for _ in range(3)]
        }

    @staticmethod
    def generate_dataset() -> Dict[str, Any]:
        """Generate data for a Dataset."""
        return {
            "name": f"Test Dataset {fake.word()}",
            "description": fake.text(max_nb_chars=100),
            "type": random.choice(["user_query", "context", "question_answer", "conversation", "custom"]),
            "is_public": random.choice([True, False]),
        }

    @staticmethod
    def generate_evaluation(agent_id: str, dataset_id: str, prompt_id: str) -> Dict[str, Any]:
        """Generate data for an Evaluation."""
        return {
            "name": f"Evaluation {fake.word()}",
            "description": fake.text(max_nb_chars=100),
            "method": random.choice(["ragas", "deepeval", "custom", "manual"]),
            "config": {"include_detailed_scores": True},
            "metrics": ["relevance", "coherence", "fluency"],
            "agent_id": agent_id,
            "dataset_id": dataset_id,
            "prompt_id": prompt_id
        }

    @staticmethod
    def generate_prompt() -> Dict[str, Any]:
        """Generate data for a Prompt."""
        return {
            "name": f"Prompt {fake.word()}",
            "description": fake.text(max_nb_chars=100),
            "content": fake.text(max_nb_chars=500),
            "parameters": {"system_message": fake.sentence()},
            "version": "1.0.0",
            "is_public": random.choice([True, False])
        }

    @staticmethod
    def generate_report(evaluation_id: str) -> Dict[str, Any]:
        """Generate data for a Report."""
        return {
            "name": f"Report {fake.word()}",
            "description": fake.text(max_nb_chars=100),
            "format": random.choice(["pdf", "html", "json"]),
            "is_public": random.choice([True, False]),
            "evaluation_id": evaluation_id,
            "include_executive_summary": True,
            "include_evaluation_details": True,
            "include_metrics_overview": True,
            "include_detailed_results": True,
            "include_agent_responses": True,
            "max_examples": 10
        }

    @staticmethod
    def generate_csv_content(rows: int = 10, dataset_type: str = "question_answer") -> str:
        """Generate CSV content for dataset upload."""
        header = ""
        content = []

        if dataset_type == "question_answer":
            header = "question,answer,ground_truth"
            for _ in range(rows):
                question = fake.sentence().replace(",", " ")
                answer = fake.text(max_nb_chars=100).replace(",", " ")
                ground_truth = fake.sentence().replace(",", " ")
                content.append(f"{question},{answer},{ground_truth}")
        elif dataset_type == "context":
            header = "context,metadata"
            for _ in range(rows):
                context = fake.text(max_nb_chars=200).replace(",", " ")
                metadata = f"{{\"source\": \"{fake.url()}\"}}"
                content.append(f"{context},{metadata}")

        return header + "\n" + "\n".join(content)