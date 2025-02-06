import ast
import difflib
import hashlib
import http.client
from dataclasses import dataclass, field
import json
import asyncio
import os
from typing import Dict, Optional, List
from datetime import datetime, timezone
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Create a logger with the name of the module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a formatter for log messages
formatter = logging.Formatter('[%(levelname)s]%(asctime)s||%(name)s: %(message)s', datefmt='%Y-%m-%d~%H:%M:%S%z')

# Create a console handler and add it to the logger
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Create a file handler and add it to the logger
logs_dir = Path(__file__).resolve().parent / 'logs'
logs_dir.mkdir(exist_ok=True)
file_handler = RotatingFileHandler(logs_dir / 'app.log', maxBytes=10485760, backupCount=10)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Log a message indicating that logging has been initialized
logger.info('Logging initialized from %s', __file__)

class OllamaClient:
    def __init__(self, host: str = "localhost", port: int = 11434):
        self.host = host
        self.port = port

    async def generate_embedding(self, text: str, model: str = "nomic-embed-text") -> Optional[List[float]]:
        try:
            conn = http.client.HTTPConnection(self.host, self.port)
            request_data = {
                "model": model,
                "prompt": text
            }
            headers = {'Content-Type': 'application/json'}
            
            conn.request("POST", "/api/embeddings", json.dumps(request_data), headers)
            response = conn.getresponse()
            result = json.loads(response.read().decode())
            return result['embedding']
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            return None
        finally:
            conn.close()

    async def generate_response(self, prompt: str, model: str = "gemma:2b") -> str:
        try:
            conn = http.client.HTTPConnection(self.host, self.port)
            request_data = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            headers = {'Content-Type': 'application/json'}
            
            conn.request("POST", "/api/generate", json.dumps(request_data), headers)
            response = conn.getresponse()
            result = json.loads(response.read().decode())
            return result.get('response', '')
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return f"Error generating response: {str(e)}"
        finally:
            conn.close()

class CodeAnalyzer:
    """Performs static and inference-based code analysis."""
    
    def __init__(self, ollama_client):
        self.ollama_client = ollama_client

    def static_analysis(self, code: str) -> Dict[str, List[str]]:
        """Static analysis using Python's AST module for structure and difflib for diffs."""
        result = {"functions": [], "classes": [], "diffs": []}

        # Parse AST and collect function/class definitions
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                result["functions"].append(node.name)
            elif isinstance(node, ast.ClassDef):
                result["classes"].append(node.name)

        # Example: Create a diff from a previous state (dummy example)
        previous_code = "def old_function(): pass\n"
        current_code = code
        result["diffs"] = list(difflib.unified_diff(previous_code.splitlines(), current_code.splitlines(), lineterm=''))

        return result

    async def inference_analysis(self, code: str) -> str:
        """Uses OllamaClient for context-aware code analysis."""
        prompt = f"Analyze this code for potential issues and give suggestions:\n\n{code}"
        return await self.ollama_client.generate_response(prompt)

class MerkleNode:
    """Tracks code state in a Merkle Tree-like structure for versioning and history tracking."""
    
    def __init__(self, data: str, children: set = None):
        self.data = data
        self.children = children or set()
        timestamp = datetime.now(timezone.utc).isoformat()
        self.uuid = hashlib.sha256(data.encode()).hexdigest()
        self.hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        hasher = hashlib.sha256()
        hasher.update(self.data.encode())
        for child in sorted(self.children, key=lambda x: x.hash):
            hasher.update(child.hash.encode())
        return hasher.hexdigest()

@dataclass
class Report:
    static_analysis: Dict[str, List[str]]
    inference_analysis: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self):
        # You could add custom initialization logic here if needed
        pass

class CIAnalyzer:
    """Core class for integrating the analyzer into CI/CD."""
    
    def __init__(self, analyzer: CodeAnalyzer):
        self.analyzer = analyzer

    async def run_analysis(self, code: str):
        """Runs both static and inference-based analysis on given code."""
        static_results = self.analyzer.static_analysis(code)
        inference_result = await self.analyzer.inference_analysis(code)

        # Create the report using the dataclass
        report = Report(static_analysis=static_results, inference_analysis=inference_result)
        return report

# Usage example:
async def main():
    ollama_client = OllamaClient()
    analyzer = CodeAnalyzer(ollama_client)
    ci_analyzer = CIAnalyzer(analyzer)

    code = """
class Example:
    def method(self):
        pass
    """
    
    report = await ci_analyzer.run_analysis(code)
    print(json.dumps(report.__dict__, indent=2))  # Convert dataclass to dict for JSON output

if __name__ == "__main__":
    asyncio.run(main())