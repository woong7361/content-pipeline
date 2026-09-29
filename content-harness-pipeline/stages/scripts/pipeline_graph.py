from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class DagNode:
    name: str
    upstream: tuple[str, ...]
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]


class PipelineDag:
    def __init__(self, nodes: Iterable[DagNode]):
        self.nodes = {node.name: node for node in nodes}
        self._validate()

    def _validate(self) -> None:
        for node in self.nodes.values():
            missing = [name for name in node.upstream if name not in self.nodes]
            if missing:
                raise ValueError(f"{node.name}: unknown upstream nodes: {missing}")
        self.topological_order()

    def topological_order(self) -> list[str]:
        pending = {name: set(node.upstream) for name, node in self.nodes.items()}
        ordered: list[str] = []
        while pending:
            ready = sorted(name for name, deps in pending.items() if not deps)
            if not ready:
                raise ValueError(f"pipeline DAG has a cycle: {sorted(pending)}")
            ordered.extend(ready)
            for name in ready:
                pending.pop(name)
            for deps in pending.values():
                deps.difference_update(ready)
        return ordered

    def descendants(self, names: Iterable[str]) -> set[str]:
        found = set(names)
        changed = True
        while changed:
            changed = False
            for node in self.nodes.values():
                if node.name not in found and any(parent in found for parent in node.upstream):
                    found.add(node.name)
                    changed = True
        return found


class StageCache:
    VERSION = 1

    def __init__(self, run_dir: Path, dag: PipelineDag):
        self.run_dir = run_dir
        self.dag = dag
        self.path = run_dir / ".pipeline" / "cache.json"
        self.data = self._load()

    def _load(self) -> dict:
        if not self.path.exists():
            return {"version": self.VERSION, "stages": {}}
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"version": self.VERSION, "stages": {}}
        if value.get("version") != self.VERSION:
            return {"version": self.VERSION, "stages": {}}
        return value

    def fingerprint(self, node_name: str, extra: dict | None = None) -> str:
        node = self.dag.nodes[node_name]
        digest = hashlib.sha256()
        digest.update(f"cache-v{self.VERSION}:{node_name}\n".encode())
        for relative in sorted(node.inputs):
            path = self.run_dir / relative
            digest.update(relative.encode())
            digest.update(file_digest(path).encode())
        for parent in sorted(node.upstream):
            digest.update(parent.encode())
            digest.update(str(self.data.get("stages", {}).get(parent, {}).get("output_digest", "missing")).encode())
        digest.update(json.dumps(extra or {}, ensure_ascii=False, sort_keys=True).encode())
        return digest.hexdigest()

    def hit(self, node_name: str, fingerprint: str) -> bool:
        node = self.dag.nodes[node_name]
        entry = self.data.get("stages", {}).get(node_name) or {}
        if entry.get("fingerprint") != fingerprint:
            return False
        return all((self.run_dir / relative).exists() for relative in node.outputs)

    def record(self, node_name: str, fingerprint: str) -> None:
        node = self.dag.nodes[node_name]
        output_digest = hashlib.sha256()
        for relative in sorted(node.outputs):
            output_digest.update(relative.encode())
            output_digest.update(file_digest(self.run_dir / relative).encode())
        self.data.setdefault("stages", {})[node_name] = {
            "fingerprint": fingerprint,
            "output_digest": output_digest.hexdigest(),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def invalidate(self, names: Iterable[str]) -> set[str]:
        affected = self.dag.descendants(names)
        stages = self.data.setdefault("stages", {})
        for name in affected:
            stages.pop(name, None)
        if self.path.parent.exists():
            self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return affected


def file_digest(path: Path) -> str:
    if not path.exists():
        return "missing"
    digest = hashlib.sha256()
    if path.is_file():
        digest.update(path.read_bytes())
        return digest.hexdigest()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(child.relative_to(path).as_posix().encode())
        digest.update(child.read_bytes())
    return digest.hexdigest()
