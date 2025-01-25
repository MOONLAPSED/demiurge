import os
import sys
import math
import time
import json
import time
import uuid
import heapq
import queue
import struct
import logging
import asyncio
import pathlib
import hashlib
import threading
import http.client
import urllib.parse
import importlib.util
from array import array
from pathlib import Path
from struct import calcsize
from collections import deque
from collections import OrderedDict
from contextlib import contextmanager
from functools import lru_cache, partial
from dataclasses import dataclass, field
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Dict, Optional, Tuple, List, Callable, Deque, Any, Set

class Task:
    def __init__(self, task_id: int, func: Callable, args=(), kwargs=None):
        self.task_id = task_id
        self.func = func
        self.args = args
        self.kwargs = kwargs if kwargs else {}
        self.result = None

    def run(self):
        logging.info(f"Running task {self.task_id}")
        try:
            self.result = self.func(*self.args, **self.kwargs)
            logging.info(f"Task {self.task_id} completed with result: {self.result}")
        except Exception as e:
            logging.error(f"Task {self.task_id} failed with error: {e}")
        return self.result

class Arena:
    def __init__(self, name: str):
        self.name = name
        self.lock = threading.Lock()
        self.local_data = {}

    def allocate(self, key: str, value: Any):
        with self.lock:
            self.local_data[key] = value
            logging.info(f"Arena {self.name}: Allocated {key} = {value}")

    def deallocate(self, key: str):
        with self.lock:
            value = self.local_data.pop(key, None)
            logging.info(f"Arena {self.name}: Deallocated {key}, value was {value}")

    def get(self, key: str):
        with self.lock:
            return self.local_data.get(key)

class SpeculativeKernel:
    def __init__(self, num_arenas: int):
        self.arenas = {i: Arena(f"Arena_{i}") for i in range(num_arenas)}
        self.task_queue = queue.Queue()
        self.task_id_counter = 0
        self.executor = ThreadPoolExecutor(max_workers=num_arenas)
        self.running = False

    def submit_task(self, func: Callable, args=(), kwargs=None) -> int:
        task_id = self.task_id_counter
        self.task_id_counter += 1
        task = Task(task_id, func, args, kwargs)
        self.task_queue.put(task)
        logging.info(f"Submitted task {task_id}")
        return task_id

    def run(self):
        self.running = True
        for i in range(len(self.arenas)):
            self.executor.submit(self._worker, i)
        logging.info("Kernel is running")

    def stop(self):
        self.running = False
        self.executor.shutdown(wait=True)
        logging.info("Kernel has stopped")

    def _worker(self, arena_id: int):
        arena = self.arenas[arena_id]
        while self.running:
            try:
                task = self.task_queue.get(timeout=1)
                logging.info(f"Worker {arena_id} picked up task {task.task_id}")
                with self._arena_context(arena, "current_task", task):
                    task.run()
            except queue.Empty:
                continue

    @contextmanager
    def _arena_context(self, arena: Arena, key: str, value: Any):
        arena.allocate(key, value)
        try:
            yield
        finally:
            arena.deallocate(key)

    def handle_fail_state(self, arena_id: int):
        arena = self.arenas[arena_id]
        with arena.lock:
            logging.error(f"Handling fail state in {arena.name}")
            arena.local_data.clear()

    def save_state(self, filename: str):
        state = {arena.name: arena.local_data for arena in self.arenas.values()}
        with open(filename, "w") as f:
            json.dump(state, f)
        logging.info(f"State saved to {filename}")

    def load_state(self, filename: str):
        with open(filename, "r") as f:
            state = json.load(f)
        for arena_name, local_data in state.items():
            arena_id = int(arena_name.split("_")[1])
            self.arenas[arena_id].local_data = local_data
        logging.info(f"State loaded from {filename}")

@dataclass
class MemoryCell:
    value: bytes = b'\x00'

@dataclass
class MemorySegment:
    cells: Dict [int, MemoryCell] = field(default_factory=dict)

    def read(self, address: int) -> bytes:
        if address in self.cells:
            return self.cells[address].value
        return b'\x00'

    def write(self, address: int, value: bytes):
        self.cells[address] = MemoryCell(value)

class VirtualMemoryFS:
    WORD_SIZE = 2
    CELL_SIZE = 1
    BASE_DIR = "./app/"

    def __init__(self):
        self.base_path = pathlib.Path(self.BASE_DIR)
        self._init_filesystem()
        self._memory_cache: Dict[int, MemoryCell] = {}
        self._segments: Dict[int, MemorySegment] = {addr: MemorySegment() for addr in range(0x100)}

    def _init_filesystem(self):
        self.base_path.mkdir(parents=True, exist_ok=True)
        for dir_addr in range(0x100):
            dir_path = self.base_path / f"{dir_addr:02x}"
            dir_path.mkdir(exist_ok=True)
            init_content = f"""
# Auto-generated __init__.py for virtual memory directory 0x{dir_addr:02x}
from dataclasses import dataclass, field
import array

@dataclass
class MemorySegment:
    data: array.array = field(default_factory=lambda: array.array('B', [0] * 256))
"""
            (dir_path / "__init__.py").write_text(init_content)
            for file_addr in range(0x100):
                file_path = dir_path / f"{file_addr:02x}"
                if not file_path.exists():
                    file_path.write_bytes(b'\x00')

    def _address_to_path(self, address: int) -> pathlib.Path:
        if not 0 <= address <= 0xFFFF:
            raise ValueError(f"Address {address:04x} out of range")
        dir_addr = (address >> 8) & 0xFF
        file_addr = address & 0xFF
        return self.base_path / f"{dir_addr:02x}" / f"{file_addr:02x}"

    async def read(self, address: int) -> bytes:
        if address in self._memory_cache:
            return self._memory_cache[address].value
        path = self._address_to_path(address)
        loop = asyncio.get_event_loop()
        value = await loop.run_in_executor(None, path.read_bytes)
        self._memory_cache[address] = MemoryCell(value)
        return value

    async def write(self, address: int, value: bytes):
        if len(value) != self.CELL_SIZE:
            raise ValueError(f"Value must be {self.CELL_SIZE} byte")
        path = self._address_to_path(address)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, path.write_bytes, value)
        self._memory_cache[address] = MemoryCell(value)
        segment_index = (address >> 8) & 0xFF
        self._segments[segment_index].write(address & 0xFF, value)

class MemoryHead:
    def __init__(self, vmem: VirtualMemoryFS):
        self.vmem = vmem
        self.wavefront = MemoryWavefront()
        self.module_cache: Dict[Tuple[int, int], object] = {}

    def _load_segment_module(self, segment_addr: int) -> object:
        dir_path = self.vmem.base_path / f"{segment_addr:02x}"
        module_path = dir_path / "__init__.py"
        cache_key = (segment_addr, module_path.stat().st_mtime)
        if cache_key in self.module_cache:
            return self.module_cache[cache_key]
        spec = importlib.util.spec_from_file_location(
            f"vmem.seg_{segment_addr:02x}",
            module_path
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        self.module_cache[cache_key] = module
        return module

    def propagate(self, target_addr: int, max_steps: Optional[int] = None) -> List[int]:
        path = []
        steps = 0
        while self.wavefront.position != target_addr:
            if max_steps and steps >= max_steps:
                break
            current_addr = self.wavefront.position
            path.append(current_addr)
            self.wavefront.visited.add(current_addr)
            self.wavefront.timestamps[current_addr] = time.time()
            segment_addr = (current_addr >> 8) & 0xFF
            module = self._load_segment_module(segment_addr)
            if segment_addr not in self.vmem._segments:
                self.vmem._segments[segment_addr] = module.MemorySegment()
            if current_addr < target_addr:
                self.wavefront.position += 1
            else:
                self.wavefront.position -= 1
            steps += 1
        return path

    def read(self, address: int) -> bytes:
        self.propagate(address)
        return self.vmem.read(address)

    async def write(self, address: int, value: bytes):
        self.propagate(address)
        await self.vmem.write(address, value)

    async def get_wavefront_info(self) -> dict:
        return {
            'position': f"0x{self.wavefront.position:04x}",
            'visited_count': len(self.wavefront.visited),
            'current_segment': f"0x{(self.wavefront.position >> 8):02x}",
            'loaded_modules': len(self.module_cache)
        }

@dataclass
class MemoryWavefront:
    position: int = 0x0000
    visited: Set[int] = field(default_factory=set)
    timestamps: Dict[int, float] = field(default_factory=dict)
    namespace_cache: Dict[str, object] = field(default_factory=dict)

@dataclass
class Document:
    content: str
    embedding: Optional[array] = None
    metadata: Dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict:
        return {
            'content': self.content,
            'embedding': list(self.embedding) if self.embedding else None,
            'metadata': self.metadata,
            'timestamp': self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Document':
        doc = cls(content=data['content'], metadata=data.get('metadata', {}))
        if data.get('embedding'):
            doc.embedding = array('f', data['embedding'])
        doc.timestamp = data.get('timestamp', time.time())
        return doc

class ConnectionPool:
    def __init__(self, host: str, port: int, pool_size: int = 5):
        self.host = host
        self.port = port
        self.pool: Deque[http.client.HTTPConnection] = deque(maxlen=pool_size)
        self.lock = threading.Lock()

    def get_connection(self) -> http.client.HTTPConnection:
        with self.lock:
            if not self.pool:
                return http.client.HTTPConnection(self.host, self.port)
            return self.pool.popleft()

    def return_connection(self, conn: http.client.HTTPConnection):
        with self.lock:
            try:
                conn.close()
                conn = http.client.HTTPConnection(self.host, self.port)
                self.pool.append(conn)
            except:
                pass


class InferenceHead(MemoryHead):
    def __init__(self, vmem: VirtualMemoryFS, ollama_host: str = "localhost", ollama_port: int = 11434):
        super().__init__(vmem)
        self.ollama_host = ollama_host
        self.ollama_port = ollama_port
        self._init_embedding_segments()

    def _init_embedding_segments(self):
        for addr in range(0x100):
            self.vmem._segments[addr] = EmbeddingSegment()


    async def generate_embedding(self, text: str, model: str = "nomic-embed-text") -> array:
        conn = http.client.HTTPConnection(self.ollama_host, self.ollama_port)
        request_data = {"model": model, "prompt": text}
        headers = {'Content-Type': 'application/json'}
        conn.request("POST", "/api/embeddings", json.dumps(request_data), headers)
        response = conn.getresponse()
        result = json.loads(response.read().decode())
        conn.close()
        return array('f', result['embedding'])


    async def infer(self, prompt: str, model: str = "gemma2", context: Optional[List[bytes]] = None) -> str:
        context_text = ""
        if context:
            context_text = "\n".join([bytes.decode('utf-8', errors='ignore') for bytes in context])
        full_prompt = f"{context_text}\n{prompt}" if context_text else prompt
        conn = http.client.HTTPConnection(self.ollama_host, self.ollama_port)
        request_data = {"model": model, "prompt": full_prompt}
        headers = {'Content-Type': 'application/json'}
        conn.request("POST", "/api/generate", json.dumps(request_data), headers)
        response = conn.getresponse()
        result = json.loads(response.read().decode())
        conn.close()
        return result['response']


    async def write_with_embedding(self, address: int, value: bytes, text: Optional[str] = None):
        if text:
            embedding = await self.generate_embedding(text)
        else:
            embedding = await self.generate_embedding(value.decode('utf-8', errors='ignore'))
        segment_addr = (address >> 8) & 0xFF
        segment = self.vmem._segments[segment_addr]
        if isinstance(segment, EmbeddingSegment):
            segment.write(address & 0xFF, value, embedding)
        else:
            segment.write(address & 0xFF, value)

    async def search_similar_across_segments(self, query_text: str, top_k: int = 5) -> List[tuple]:
        query_embedding = await self.generate_embedding(query_text)
        results = []
        for segment_addr, segment in self.vmem._segments.items():
            if isinstance(segment, EmbeddingSegment):
                segment_results = segment.search_similar(query_embedding, top_k)
                results.extend([(segment_addr, addr, sim) for addr, sim in segment_results])
        return sorted(results, key=lambda x: x[2], reverse=True)[:top_k]

@dataclass
class EmbeddingCell(MemoryCell):
    embedding: Optional[array] = None
    metadata: Dict = field(default_factory=dict)

    def serialize(self) -> bytes:
        data = {
            'value': self.value.hex(),
            'embedding': list(self.embedding) if self.embedding is not None else None,
            'metadata': self.metadata
        }
        return json.dumps(data).encode()

    @classmethod
    def deserialize(cls, data: bytes) -> 'EmbeddingCell':
        parsed = json.loads(data)
        cell = cls(bytes.fromhex(parsed['value']))
        if parsed['embedding']:
            cell.embedding = array('f', parsed['embedding'])
        cell.metadata = parsed['metadata']
        return cell

class EmbeddingSegment(MemorySegment):
    def __init__(self):
        super().__init__()
        self.embedding_index: Dict[int, array] = {}

    def write(self, address: int, value: bytes, embedding: Optional[array] = None):
        cell = EmbeddingCell(value, embedding)
        self.cells[address] = cell
        if embedding is not None:
            self.embedding_index[address] = embedding

    def search_similar(self, query_embedding: array, top_k: int = 5) -> List[tuple]:
        if not self.embedding_index:
            return []

        def cosine_similarity(a: array, b: array) -> float:
            dot_product = sum (x * y for x, y in zip(a, b))
            norm_a = math.sqrt(sum(x * x for x in a))
            norm_b = math.sqrt(sum(x * x for x in b))
            return dot_product / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0
        similarities = []
        for addr, emb in self.embedding_index.items():
            similarity = cosine_similarity(query_embedding, emb)
            similarities.append((addr, similarity))
        return sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]

class LocalRAGSystem:
    def __init__(self, host: str = "localhost", port: int = 11434, persistence_path: str = "rag_storage"):
        self.host = host
        self.port = port
        self.documents: List[Document] = []
        self.persistence_path = Path(persistence_path)
        self.persistence_path.mkdir(exist_ok=True)
        self.load_state()

    def save_state(self):
        documents_data = [doc.to_dict() for doc in self.documents]
        with open(self.persistence_path / "documents.json", "w") as f:
            json.dump(documents_data, f)

    def load_state(self):
        try:
            with open(self.persistence_path / "documents.json", "r") as f:
                documents_data = json.load(f)
                self.documents = [Document.from_dict(data) for data in documents_data]
        except FileNotFoundError:
            self.documents = []

    async def generate_embedding(self, text: str, model: str = "nomic-embed-text") -> array:
        conn = http.client.HTTPConnection(self.host, self.port)
        request_data = {"model": model, "prompt": text}
        headers = {'Content-Type': 'application/json'}
        conn.request("POST", "/api/embeddings", json.dumps(request_data), headers)
        response = conn.getresponse()
        result = json.loads(response.read().decode())
        conn.close()
        return array('f', result['embedding'])

    async def batch_generate_embeddings(self, texts: List[str]) -> List[array]:
        tasks = [self.generate_embedding(text) for text in texts]
        return await asyncio.gather(*tasks)

    def calculate_similarity(self, emb1: array, emb2: array) -> float:
        try:
            dot_product = sum(a * b for a, b in zip(emb1, emb2))
            norm1 = math.sqrt(sum(a * a for a in emb1))
            norm2 = math.sqrt(sum(b * b for b in emb2))
            return dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0
        except Exception:
            return 0.0

    async def add_documents(self, documents: List[Tuple[str, Dict]]):
        contents = [doc[0] for doc in documents]
        embeddings = await self.batch_generate_embeddings(contents)
        for (content, metadata), embedding in zip(documents, embeddings):
            doc = Document(content=content, embedding=embedding, metadata=metadata)
            self.documents.append(doc)
        self.save_state()

    async def search_similar(self, query: str, top_k: int = 3, metadata_filter: Optional[Dict] = None) -> List[tuple]:
        query_embedding = await self.generate_embedding(query)
        similarities = []
        for doc in self.documents:
            if metadata_filter and not all(doc.metadata.get(k) == v for k, v in metadata_filter.items()):
                continue
            if doc.embedding is not None:
                score = self.calculate_similarity(query_embedding, doc.embedding)
                similarities.append((doc, score))
        return sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]

    async def generate_response(self, query: str, context_docs: List[Document], model: str = "gemma2", temperature: float = 0.7) -> str:
        context = "\n".join([doc.content for doc in context_docs])
        prompt = f"Context:\n{context}\n\nQuery: {query}\n\nResponse:"
        conn = http.client.HTTPConnection(self.host, self.port)
        request_data = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": False
        }
        headers = {'Content-Type': 'application/json'}
        conn.request("POST", "/api/generate", json.dumps(request_data), headers)
        response = conn.getresponse()
        response_text = response.read().decode()
        conn.close()
        try:
            result = json.loads(response_text)
            return result.get('response', '')
        except json.JSONDecodeError:
            return "Error: Unable to generate response"

    async def query(self, query: str, top_k: int = 3, metadata_filter: Optional[Dict ] = None, temperature: float = 0.7) -> Dict:
        similar_docs = await self.search_similar(query, top_k, metadata_filter)
        context_docs = [doc for doc, _ in similar_docs]
        response = await self.generate_response(query, context_docs, temperature=temperature)
        return {
            'query': query,
            'response': response,
            'similar_documents': [
                {
                    'content': doc.content,
                    'similarity': score,
                    'metadata': doc.metadata,
                    'timestamp': doc.timestamp
                }
                for doc, score in similar_docs
            ],
            'metadata_filter_applied': bool(metadata_filter)
        }

class EnhancedLocalRAGSystem(LocalRAGSystem):
    def __init__(self, host: str = "localhost", port: int = 11434, persistence_path: str = "rag_storage", connection_pool_size: int = 5):
        super().__init__(host, port, persistence_path)
        self.conn_pool = ConnectionPool(host, port, connection_pool_size)
        self.embedding_cache = {}
        self.cache_lock = threading.Lock()

    @lru_cache(maxsize=1000)
    def calculate_similarity(self, emb1: tuple, emb2: tuple) -> float:
        try:
            dot_product = sum(a * b for a, b in zip(emb1, emb2))
            norm1 = math.sqrt(sum(a * a for a in emb1))
            norm2 = math.sqrt(sum(b * b for b in emb2))
            return dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0
        except Exception:
            return 0.0

    async def search_similar(self, query: str, top_k: int = 3, metadata_filter: Optional[Dict] = None) -> List[tuple]:
        query_embedding = await self.generate_embedding(query)
        query_emb_tuple = tuple(query_embedding)
        heap = []
        for doc in self.documents:
            if metadata_filter and not all(doc.metadata.get(k) == v for k, v in metadata_filter.items()):
                continue
            if doc.embedding is not None:
                doc_emb_tuple = tuple(doc.embedding)
                score = self.calculate_similarity(query_emb_tuple, doc_emb_tuple)
                if len(heap) < top_k:
                    heapq.heappush(heap, (score, doc))
                elif score > heap[0][0]:
                    heapq.heapreplace(heap, (score, doc))
        return [(doc, score) for score, doc in sorted(heap, key=lambda x: x[0], reverse=True)]

    async def generate_embedding(self, text: str, model: str = "nomic-embed-text") -> array:
        cache_key = f"{text}:{model}"
        with self.cache_lock:
            if cache_key in self.embedding_cache:
                return self.embedding_cache[cache_key]
        conn = self.conn_pool.get_connection()
        try:
            request_data = {"model": model, "prompt": text}
            headers = {'Content-Type': 'application/json'}
            conn.request("POST", "/api/embeddings", json.dumps(request_data), headers)
            response = conn.getresponse()
            result = json.loads(response.read().decode())
            embedding = array('f', result['embedding'])
            with self.cache_lock:
                self.embedding_cache[cache_key] = embedding
            return embedding
        finally:
            self.conn_pool.return_connection(conn)

    def prune_cache(self, max_age: float = 3600):
        with self.cache_lock:
            current_time = time.time()
            self.embedding_cache = {
                k: v for k, v in self.embedding_cache.items()
                if current_time - self.cache_timestamps.get(k, 0) < max_age
            }

class EnhancedInferenceHead(InferenceHead):
    def __init__(self, vmem: VirtualMemoryFS, ollama_host: str = "localhost", ollama_port: int = 11434):
        super().__init__(vmem, ollama_host, ollama_port)
        self.embedding_cache = CacheSegment(maxsize=10000, ttl=3600)
        self.similarity_cache = CacheSegment(maxsize=5000, ttl=1800)
        self._setup_caching()

    def _setup_caching(self):
        self.cached_generate_embedding = self._segment_aware_cache(
            self.generate_embedding,
            maxsize=1000,
            cache_key_fn=lambda text, model: (text, model)
        )
        @lru_cache(maxsize=10000)
        def cached_cosine_similarity(emb1: Tuple[float, ...], emb2: Tuple[float, ...]) -> float:
            dot_product = sum(x * y for x, y in zip(emb1, emb2))
            norm1 = math.sqrt(sum(x * x for x in emb1))
            norm2 = math.sqrt(sum(x * x for x in emb2))
            return dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0
        self.cached_cosine_similarity = cached_cosine_similarity

    def _segment_aware_cache(self, func: Callable, maxsize: int = 128, cache_key_fn: Callable = lambda *args, **kwargs: (args, tuple(sorted(kwargs.items())))):
        cache = CacheSegment(maxsize=maxsize)
        async def wrapper(*args, **kwargs):
            cache_key = cache_key_fn(*args, **kwargs)
            result = cache.get(cache_key)
            if result is None:
                result = await func(*args, **kwargs)
                cache.put(cache_key, result)
            return result
        return wrapper

    async def search_similar_across_segments(self, query_text: str, top_k: int = 5) -> List[tuple]:
        cache_key = (query_text, top_k)
        cached_result = self.similarity_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        query_embedding = await self.cached_generate_embedding(query_text)
        query_embedding_tuple = tuple(query_embedding)
        results = []
        for segment_addr, segment in self.vmem._segments.items():
            if isinstance(segment, EmbeddingSegment):
                for addr, emb in segment.embedding_index.items():
                    emb_tuple = tuple(emb)
                    similarity = self.cached_cosine_similarity(query_embedding_tuple, emb_tuple)
                    results.append((segment_addr, addr, similarity))
        sorted_results = sorted(results, key=lambda x: x[2], reverse=True)[:top_k]
        self.similarity_cache.put(cache_key, sorted_results)
        return sorted_results

    async def write_with_embedding(self, address: int, value: bytes, text: Optional[str] = None):
        if text:
            embedding = await self.cached_generate_embedding(text)
        else:
            decoded_text = value.decode('utf-8', errors='ignore')
            embedding = await self.cached_generate_embedding(decoded_text)
        segment_addr = (address >> 8) & 0xFF
        segment = self.vmem._segments[segment_addr]
        if isinstance(segment, EmbeddingSegment):
            segment.write(address & 0xFF, value, embedding)
            self.similarity_cache = CacheSegment(maxsize=self.similarity_cache.maxsize, ttl=self.similarity_cache.ttl)
        else:
            segment.write(address & 0xFF, value)

class CacheSegment:
    def __init__(self, maxsize: int = 1024, ttl: float = 3600):
        self.maxsize = maxsize
        self.ttl = ttl
        self.cache: OrderedDict[Tuple, Tuple[any, float]] = OrderedDict()

    def get(self, key: Tuple) -> Optional[any]:
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                self.cache.move_to_end(key)
                return value
            else:
                del self.cache[key]
        return None

    def put(self, key: Tuple, value: any):
        self.cache[key] = (value, time.time())
        self.cache.move_to_end(key)
        while len(self.cache) > self.maxsize:
            self.cache.popitem(last=False)

class RAGEvaluator:
    def __init__(self, rag_system: LocalRAGSystem):
        self.rag = rag_system

    async def evaluate_retrieval(self, query: str, relevant_doc_ids: Set[str]) -> Dict[str, float]:
        results = await self.rag.search_similar(query)
        retrieved_ids = {doc.id for doc, _ in results}
        precision = len(retrieved_ids & relevant_doc_ids) / len(retrieved_ids)
        recall = len(retrieved_ids & relevant_doc_ids) / len(relevant_doc_ids)
        f1 = 2 * (precision * recall) / (precision + recall) if precision + recall > 0 else 0
        return {
            "precision": precision,
            "recall": recall,
            "f1": f1
        }

class ConversationalRAG(LocalRAGSystem):
    def __init__(self):
        super().__init__()
        self.conversations: Dict[str, Conversation] = {}

    async def chat(self, conversation_id: str, query: str) -> Dict:
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = Conversation()
        conv = self.conversations[conversation_id]
        conv.add_message("user", query)
        similar_docs = await self.search_similar(query)
        context_docs = [doc for doc, _ in similar_docs]
        response = await self.generate_response(query, context_docs)
        conv.add_message("assistant", response)
        return {"response": response, "similar_docs": similar_docs}

class DocumentChunk:
    def __init__(self, chunk_id: str, content: str, embedding: Optional[array] = None, metadata: Dict = None, start_idx: int = 0, end_idx: int = 0):
        self.chunk_id = chunk_id
        self.content = content
        self.embedding = embedding
        self.metadata = metadata
        self.start_idx = start_idx
        self.end_idx = end_idx

class PersistentRAGSystem(LocalRAGSystem):
    def __init__(self, storage_path: str, chunk_size: int = 512):
        super().__init__()
        self.storage_path = Path(storage_path)
        self.chunk_size = chunk_size
        self.storage_path.mkdir(exist_ok=True)

    async def add_document_with_chunks(self, content: str, metadata: Dict = None):
        chunks = self._create_chunks(content)
        chunk_docs = []
        for i, chunk in enumerate(chunks):
            chunk_id = f"{uuid.uuid4()}"
            embedding = await self.generate_embedding(chunk)
            chunk_doc = DocumentChunk(
                chunk_id=chunk_id,
                content=chunk,
                embedding=embedding,
                metadata=metadata,
                start_idx=i * self.chunk_size,
                end_idx=min((i + 1) * self.chunk_size, len(content))
            )
            self._save_chunk(chunk_doc)
            chunk_docs.append(chunk_doc)
        return chunk_docs

    def _create_chunks(self, content: str):
        return [content[i:i + self.chunk_size] for i in range(0, len(content), self.chunk_size)]

    def _save_chunk(self, chunk_doc: DocumentChunk):
        with open(self.storage_path / f"{chunk_doc.chunk_id}.json", "w") as f:
            json.dump({
                "chunk_id": chunk_doc.chunk_id,
                "content": chunk_doc.content,
                "embedding": list(chunk_doc.embedding) if chunk_doc.embedding else None,
                "metadata": chunk_doc.metadata,
                "start_idx": chunk_doc.start_idx,
                "end_idx": chunk_doc.end_idx
            }, f)

class EmbeddingCache:
    def __init__(self, cache_path: str):
        self.cache_path = Path(cache_path)
        self.cache_path.mkdir(exist_ok=True)

    def get(self, text: str, model: str) -> Optional[array]:
        cache_key = hashlib.md5(f"{text}:{model}".encode()).hexdigest()
        cache_file = self.cache_path / f"{cache_key}.emb"
        if cache_file.exists():
            return array('f', cache_file.read_bytes())
        return None

    def set(self, text: str, model: str, embedding: array):
        cache_key = hashlib.md5(f"{text}:{ model}".encode()).hexdigest()
        cache_file = self.cache_path / f"{cache_key}.emb"
        cache_file.write_bytes(embedding.tobytes())

class Conversation:
    def __init__(self):
        self.messages = []

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def get_context(self, window: int = 5) -> str:
        recent = self.messages[-window:] if len(self.messages) > window else self.messages
        return "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent])

async def main():
    # Initialize the RAG system with persistence
    rag = PersistentRAGSystem("rag_storage", chunk_size=256)
    
    # Add some sample documents with metadata
    sample_docs = [
        ("Python is a high-level programming language known for its simplicity and readability.", 
         {"category": "programming", "language": "python"}),
        ("Machine learning enables computers to learn from data and improve through experience.", 
         {"category": "ai", "topic": "machine_learning"}),
        ("Natural Language Processing helps computers understand human language.", 
         {"category": "ai", "topic": "nlp"})
    ]
    
    # Process documents in chunks
    for content, metadata in sample_docs:
        chunks = await rag.add_document_with_chunks(content, metadata)
        print(f"Added document with {len(chunks)} chunks")

    # Perform similarity search
    query = "What is Python programming?"
    results = await rag.search_similar(query, top_k=2)
    print("\nSearch Results:")
    for doc, score in results:
        print(f"Score: {score:.4f}")
        print(f"Content: {doc.content}")
        print(f"Metadata: {doc.metadata}\n")

    # Generate a response using the RAG system
    response_data = await rag.query(query)
    print("Generated Response:")
    print(response_data['response'])
    
    # Demonstrate conversation capability
    conv_rag = ConversationalRAG()
    conv_id = str(uuid.uuid4())
    
    chat_response = await conv_rag.chat(conv_id, "Tell me about machine learning")
    print("\nConversational Response:")
    print(chat_response['response'])
"""
async def vector_playground():
    rag = PersistentRAGSystem("rag_storage")
    
    # Test subtle variations
    variations = [
        "Python is a programming language",
        "Python is a coding language",
        "Python helps you program computers",
        "Python lets you write software"
    ]
    
    # Generate embeddings and compare directly
    for i, text1 in enumerate(variations):
        embedding1 = await rag.generate_embedding(text1)
        for j, text2 in enumerate(variations[i+1:], i+1):
            embedding2 = await rag.generate_embedding(text2)
            # Calculate similarity directly using the rag system's similarity function
            similarity = rag.calculate_similarity(tuple(embedding1), tuple(embedding2))
            print(f"\nComparing:\n'{text1}'\nwith:\n'{text2}'\nSimilarity: {similarity:.4f}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

    asyncio.run(vector_playground())
"""
async def vector_playground():
    rag = PersistentRAGSystem("rag_storage", chunk_size=256)
    
    variations = [
        "Python is a programming language",
        "Python is a coding language",
        "Python helps you program computers",
        "Python lets you write software"
    ]
    
    # Store each variation with metadata to track pairs
    stored_chunks = []
    for i, text in enumerate(variations):
        chunks = await rag.add_document_with_chunks(text, metadata={
            "variation_id": i,
            "text": text
        })
        stored_chunks.extend(chunks)
        print(f"\nStored variation {i}:")
        print(f"Text: {text}")
        print(f"Chunk ID: {chunks[0].chunk_id}")
    
    # Compare stored vectors using their chunk IDs
    for i, chunk1 in enumerate(stored_chunks):
        for j, chunk2 in enumerate(stored_chunks[i+1:], i+1):
            similarity = rag.calculate_similarity(
                tuple(chunk1.embedding), 
                tuple(chunk2.embedding)
            )
            print(f"\nComparing chunks:")
            print(f"'{variations[i]}' (ID: {chunk1.chunk_id})")
            print(f"'{variations[j]}' (ID: {chunk2.chunk_id})")
            print(f"Similarity: {similarity:.4f}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
    asyncio.run(vector_playground())