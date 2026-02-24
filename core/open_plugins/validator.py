from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Tuple

import yaml


class ManifestValidationError(ValueError):
    pass


REQUIRED_MANIFEST_FIELDS = [
    "schema_version",
    "name_for_human",
    "name_for_model",
    "description_for_human",
    "description_for_model",
    "auth",
    "api",
    "logo_url",
    "contact_email",
    "legal_info_url",
]


@dataclass(frozen=True)
class ManifestInfo:
    manifest_path: Path
    api_url: str
    schema_version: str
    name_for_model: str
    name_for_human: str


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise ManifestValidationError(f"Failed to read JSON: {path}: {e}") from e


def _read_yaml(path: Path) -> Dict[str, Any]:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as e:
        raise ManifestValidationError(f"Failed to read YAML: {path}: {e}") from e


def validate_manifest(path: str | Path) -> ManifestInfo:
    p = Path(path).resolve()
    if not p.exists():
        raise ManifestValidationError(f"Manifest not found: {p}")

    manifest = _read_json(p)

    missing = [k for k in REQUIRED_MANIFEST_FIELDS if k not in manifest]
    if missing:
        raise ManifestValidationError(f"Missing required fields: {missing}")

    api = manifest.get("api", {})
    if api.get("type") != "openapi" or not api.get("url"):
        raise ManifestValidationError("manifest.api must have type=openapi and a non-empty url")

    auth = manifest.get("auth", {})
    if "type" not in auth:
        raise ManifestValidationError("manifest.auth.type is required (e.g. none, user_http, service_http)")

    return ManifestInfo(
        manifest_path=p,
        api_url=str(api["url"]),
        schema_version=str(manifest["schema_version"]),
        name_for_model=str(manifest["name_for_model"]),
        name_for_human=str(manifest["name_for_human"]),
    )


def validate_openapi_yaml(path: str | Path) -> Tuple[str, Dict[str, Any]]:
    p = Path(path).resolve()
    if not p.exists():
        raise ManifestValidationError(f"OpenAPI file not found: {p}")

    spec = _read_yaml(p)
    version = str(spec.get("openapi", "")).strip()
    if not version:
        raise ManifestValidationError("OpenAPI spec missing 'openapi' version")
    if "paths" not in spec or not isinstance(spec["paths"], dict) or not spec["paths"]:
        raise ManifestValidationError("OpenAPI spec missing non-empty 'paths'")

    return version, spec
