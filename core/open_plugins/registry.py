from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from open_plugins.validator import ManifestInfo, validate_manifest


@dataclass(frozen=True)
class PluginEntry:
    name_for_model: str
    name_for_human: str
    manifest_path: Path
    api_url: str


def discover_manifests(root: str | Path) -> List[Path]:
    rootp = Path(root).resolve()
    return sorted(rootp.glob("**/.well-known/ai-plugin.json"))


def build_registry(root: str | Path) -> List[PluginEntry]:
    entries: List[PluginEntry] = []
    for manifest_path in discover_manifests(root):
        info: ManifestInfo = validate_manifest(manifest_path)
        entries.append(
            PluginEntry(
                name_for_model=info.name_for_model,
                name_for_human=info.name_for_human,
                manifest_path=info.manifest_path,
                api_url=info.api_url,
            )
        )
    return entries


def find_plugin(root: str | Path, name_for_model: str) -> Optional[PluginEntry]:
    for entry in build_registry(root):
        if entry.name_for_model == name_for_model:
            return entry
    return None
