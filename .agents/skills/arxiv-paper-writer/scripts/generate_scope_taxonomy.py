#!/usr/bin/env python3
"""Generate scope.yaml and taxonomy.yaml from user prompt.

This script parses a user's review topic description and generates:
1. notes/scope.yaml - Review scope contract
2. notes/taxonomy.yaml - Vocabulary definitions for this review

Usage:
    python generate_scope_taxonomy.py --project-dir <paper_dir> --topic "Your review topic" [--skeleton pipeline|pillars|method-bridge]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

# Default scope template
SCOPE_TEMPLATE = {
    "version": "2.4",
    "created": "",
    "last_updated": "",
    "review": {
        "title": "",
        "slug": "",
        "mode": "pharma",
        "target_venue": "arXiv",
        "target_pages": 8,
    },
    "scope": {
        "ai_tasks": {"included": [], "excluded": []},
        "molecule_types": {"included": ["small_molecules"], "excluded": []},
        "lifecycle_stages": {"included": [], "excluded": []},
        "evidence_scope": {"min_level": "L3", "max_level": "L0"},
        "time_range": {"start_year": 2020, "end_year": 2026, "classic_exceptions": True},
    },
    "personas": {
        "primary": [],
        "secondary": [],
        "coverage_requirement": {"min_personas": 3},
    },
    "deliverables": {
        "taxonomy": {"required": True, "type": "hierarchical"},
        "evidence_tables": {
            "study_table": {"required": True, "min_rows": 20},
            "benchmark_table": {"required": True, "min_rows": 10},
        },
        "visualizations": {
            "min_count": 5,
            "required_types": ["taxonomy_diagram", "pipeline_figure", "comparison_table"],
        },
    },
    "benchmark_policy": {
        "mode": "AUTO",
        "min_per_task": 1,
        "allow_new": True,
        "selection_criteria": [
            "community_usage_or_leaderboard",
            "data_accessible_and_citable",
            "clear_split_and_metrics",
            "external_validity_if_possible",
        ],
        "user_priority_list": [],
        "blocklist": [],
    },
    "preprint_policy": {
        "bioRxiv_allowed": True,
        "medRxiv_allowed": True,
        "upgrade_check_required": True,
        "allowed_for": ["method_structure", "dataset_construction", "evaluation_protocol", "engineering_system"],
        "forbidden_for": ["clinical_efficacy", "safety_conclusion", "dosing_recommendation", "regulatory_claim"],
    },
}

# Task detection patterns
TASK_PATTERNS = {
    "ADMET": [r"admet", r"adme-?t?", r"absorption", r"distribution", r"metabolism", r"excretion", r"toxicity"],
    "property_prediction": [r"property prediction", r"qsar", r"molecular property"],
    "generative_design": [r"generative", r"de novo", r"molecular generation", r"molecule generation"],
    "virtual_screening": [r"virtual screening", r"docking", r"ligand-based"],
    "MPO": [r"multi.?parameter optimization", r"mpo", r"lead optimization"],
    "retrosynthesis": [r"retrosynthesis", r"synthesis planning", r"reaction prediction"],
    "target_identification": [r"target identification", r"target discovery", r"target validation"],
    "DTI": [r"drug.?target interaction", r"dti", r"binding affinity"],
    "DDI": [r"drug.?drug interaction", r"ddi"],
    "toxicity": [r"toxicity", r"tox21", r"toxcast", r"hepatotoxicity", r"cardiotoxicity"],
}

# Lifecycle stage detection
LIFECYCLE_PATTERNS = {
    "target_identification": [r"target identification", r"target discovery"],
    "hit_discovery": [r"hit discovery", r"hit finding", r"virtual screening"],
    "lead_optimization": [r"lead optimization", r"lead opt", r"mpo"],
    "admet_prediction": [r"admet", r"adme", r"pk.?pd", r"pharmacokinetic"],
    "preclinical": [r"preclinical", r"in vivo", r"animal"],
    "clinical": [r"clinical", r"phase [i123]", r"human trial"],
}

# AI method detection
AI_PATTERNS = {
    "GNN": [r"gnn", r"graph neural network", r"message passing", r"mpnn"],
    "Transformer": [r"transformer", r"attention", r"bert", r"gpt"],
    "Diffusion": [r"diffusion", r"score.?based", r"ddpm"],
    "VAE": [r"vae", r"variational autoencoder"],
    "RL": [r"reinforcement learning", r"policy gradient", r"ppo"],
    "LLM": [r"llm", r"large language model", r"foundation model"],
}

# Persona detection
PERSONA_PATTERNS = {
    "MedicinalChem": [r"medicinal chemist", r"sar", r"structure.?activity", r"synthesizability"],
    "DMPK": [r"dmpk", r"admet", r"pharmacokinetic", r"clearance", r"bioavailability"],
    "Biology": [r"biolog", r"target", r"pathway", r"mechanism"],
    "DataScience": [r"data scien", r"ml engineer", r"benchmark", r"model"],
    "Regulatory": [r"regulat", r"fda", r"ema", r"compliance"],
    "ClinPharm": [r"clinical pharma", r"dose", r"pk.?pd"],
}


def detect_patterns(text: str, patterns: dict[str, list[str]]) -> list[str]:
    """Detect which patterns match in the text."""
    text_lower = text.lower()
    matches = []
    for key, regexes in patterns.items():
        for regex in regexes:
            if re.search(regex, text_lower):
                matches.append(key)
                break
    return matches


def generate_slug(topic: str) -> str:
    """Generate a kebab-case slug from topic."""
    slug = re.sub(r"[^\w\s-]", "", topic.lower())
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug[:50]  # Limit length


def generate_scope(topic: str, skeleton: str = "pipeline") -> dict:
    """Generate scope.yaml content from topic."""
    scope = dict(SCOPE_TEMPLATE)
    now = datetime.now().strftime("%Y-%m-%d")
    
    scope["created"] = now
    scope["last_updated"] = now
    scope["review"]["title"] = topic
    scope["review"]["slug"] = generate_slug(topic)
    
    # Detect tasks
    detected_tasks = detect_patterns(topic, TASK_PATTERNS)
    scope["scope"]["ai_tasks"]["included"] = detected_tasks if detected_tasks else ["property_prediction"]
    
    # Detect lifecycle stages
    detected_stages = detect_patterns(topic, LIFECYCLE_PATTERNS)
    scope["scope"]["lifecycle_stages"]["included"] = detected_stages if detected_stages else ["lead_optimization", "admet_prediction"]
    
    # Detect personas
    detected_personas = detect_patterns(topic, PERSONA_PATTERNS)
    scope["personas"]["primary"] = detected_personas[:2] if detected_personas else ["DataScience", "MedicinalChem"]
    scope["personas"]["secondary"] = detected_personas[2:4] if len(detected_personas) > 2 else ["DMPK"]
    
    return scope


def generate_taxonomy(topic: str, scope: dict) -> dict:
    """Generate taxonomy.yaml content based on scope."""
    detected_ai = detect_patterns(topic, AI_PATTERNS)
    
    taxonomy = {
        "version": "2.4",
        "derived_from": "notes/scope.yaml",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "rd_stages": {
            "allowed": [
                {"id": "Target", "label": "Target Identification & Validation"},
                {"id": "Hit", "label": "Hit Discovery"},
                {"id": "Lead", "label": "Lead Optimization"},
                {"id": "ADMET_DMPK", "label": "ADMET/DMPK"},
                {"id": "Synthesis", "label": "Synthesis Planning"},
                {"id": "Clinical", "label": "Clinical Development"},
                {"id": "Cross", "label": "Cross-stage"},
            ],
            "in_scope": scope["scope"]["lifecycle_stages"]["included"],
        },
        "pharma_tasks": {
            "allowed": list(TASK_PATTERNS.keys()),
            "in_scope": scope["scope"]["ai_tasks"]["included"],
        },
        "ai_families": {
            "allowed": list(AI_PATTERNS.keys()),
            "in_scope": detected_ai if detected_ai else ["GNN", "Transformer"],
        },
        "data_modalities": {
            "allowed": ["SMILES", "2D_graph", "3D", "protein_seq", "structure", "omics", "text"],
            "in_scope": ["SMILES", "2D_graph"],  # Default
        },
        "evidence_levels": {
            "allowed": [
                {"id": "L0", "label": "Benchmark Only", "description": "Retrospective public datasets"},
                {"id": "L1", "label": "External Test", "description": "Temporal/scaffold split, held-out"},
                {"id": "L2", "label": "Wet-Lab Validated", "description": "Experimental confirmation"},
                {"id": "L3", "label": "Prospective/Closed-Loop", "description": "Model-driven discovery"},
            ],
        },
        "personas": {
            "allowed": list(PERSONA_PATTERNS.keys()),
            "primary": scope["personas"]["primary"],
            "secondary": scope["personas"]["secondary"],
        },
        "dmta_stages": {
            "allowed": ["Design", "Make", "Test", "Analyze", "Cross"],
        },
    }
    
    return taxonomy


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate scope.yaml and taxonomy.yaml from user prompt"
    )
    parser.add_argument("--project-dir", required=True, help="Paper project directory")
    parser.add_argument("--topic", required=True, help="Review topic description")
    parser.add_argument(
        "--skeleton",
        choices=["pipeline", "pillars", "method-bridge"],
        default="pipeline",
        help="Review skeleton type",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    
    args = parser.parse_args()
    
    project_dir = Path(args.project_dir)
    notes_dir = project_dir / "notes"
    
    # Ensure notes directory exists
    notes_dir.mkdir(parents=True, exist_ok=True)
    
    scope_path = notes_dir / "scope.yaml"
    taxonomy_path = notes_dir / "taxonomy.yaml"
    
    # Check for existing files
    if not args.force:
        if scope_path.exists():
            print(f"Error: {scope_path} already exists. Use --force to overwrite.", file=sys.stderr)
            return 1
        if taxonomy_path.exists():
            print(f"Error: {taxonomy_path} already exists. Use --force to overwrite.", file=sys.stderr)
            return 1
    
    # Generate files
    print(f"Generating scope and taxonomy for topic: {args.topic}")
    
    scope = generate_scope(args.topic, args.skeleton)
    taxonomy = generate_taxonomy(args.topic, scope)
    
    # Write scope.yaml
    with scope_path.open("w", encoding="utf-8") as f:
        yaml.dump(scope, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"Created: {scope_path}")
    
    # Write taxonomy.yaml
    with taxonomy_path.open("w", encoding="utf-8") as f:
        yaml.dump(taxonomy, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"Created: {taxonomy_path}")
    
    # Summary
    print("\nDetected scope:")
    print(f"  Tasks: {scope['scope']['ai_tasks']['included']}")
    print(f"  Lifecycle stages: {scope['scope']['lifecycle_stages']['included']}")
    print(f"  Primary personas: {scope['personas']['primary']}")
    print(f"  AI families: {taxonomy['ai_families']['in_scope']}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
