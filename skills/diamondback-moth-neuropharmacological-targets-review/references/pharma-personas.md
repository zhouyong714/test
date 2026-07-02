# Pharma Personas Reference Guide

> **Version**: 2.4  
> **Last Updated**: 2026-01-06  
> **Purpose**: Define target audience personas and coverage requirements for pharma×AI reviews

---

## Overview

Pharma×AI reviews should address multiple stakeholder perspectives. Each persona has distinct priorities, vocabulary preferences, and evaluation criteria.

---

## Core Personas

### 1. MedicinalChem (Medicinal Chemist)

**Role**: Designs and optimizes drug candidates

**Key Concerns**:
- Structure-Activity Relationships (SAR)
- Multi-Parameter Optimization (MPO)
- Synthesizability and synthetic routes
- Patent space and freedom to operate
- Lead-likeness and drug-likeness

**AI Applications They Care About**:
- Generative molecular design
- Property prediction (esp. for MPO)
- Retrosynthesis planning
- Matched molecular pair analysis

**Language Preferences**:
- Specific chemistry terminology (scaffold, bioisostere, warhead)
- Quantitative property thresholds (cLogP < 3, TPSA 60-140)
- Practical applicability over theoretical novelty

---

### 2. DMPK (Drug Metabolism & Pharmacokinetics)

**Role**: Studies drug absorption, distribution, metabolism, excretion, and toxicity

**Key Concerns**:
- In vitro to in vivo extrapolation (IVIVE)
- Exposure-toxicity relationships
- Metabolite prediction
- Drug-drug interactions (DDI)
- Clearance and bioavailability

**AI Applications They Care About**:
- ADMET prediction models
- Metabolite/soft spot prediction
- CYP inhibition/induction
- PK/PD modeling
- Toxicity endpoint prediction

**Language Preferences**:
- Pharmacokinetic parameters (AUC, Cmax, t½, Vd)
- Assay-specific terminology (microsomal stability, Caco-2)
- Regulatory context (FDA guidance, ICH)

---

### 3. Biology (Biologist / Translational Scientist)

**Role**: Studies disease biology and validates drug targets

**Key Concerns**:
- Target identification and validation
- Disease mechanism understanding
- Biomarker identification
- Patient stratification
- Preclinical to clinical translation

**AI Applications They Care About**:
- Target discovery from omics data
- Knowledge graph reasoning
- Phenotypic screening analysis
- Biomarker discovery
- Single-cell analysis

**Language Preferences**:
- Biological pathway terminology
- Target validation concepts (genetic, pharmacological)
- Disease area specifics

---

### 4. ClinPharm (Clinical Pharmacologist)

**Role**: Designs clinical studies and analyzes human pharmacology

**Key Concerns**:
- Dose selection and optimization
- First-in-human safety
- PK/PD modeling in humans
- Population PK
- Real-world evidence

**AI Applications They Care About**:
- Clinical trial optimization
- Patient stratification
- Dosing regimen prediction
- Adverse event prediction
- Drug repurposing

**Language Preferences**:
- Clinical trial terminology (Phase I/II/III)
- Regulatory context
- Statistical rigor

---

### 5. Regulatory (Regulatory Scientist)

**Role**: Ensures regulatory compliance and prepares submissions

**Key Concerns**:
- Regulatory acceptance of AI/ML
- Validation and reproducibility
- Model documentation
- Interpretability and explainability
- Change management

**AI Applications They Care About**:
- Regulatory guidance on AI/ML
- Model documentation frameworks
- Validation strategies
- Risk-based approaches

**Language Preferences**:
- Regulatory terminology (FDA, EMA, ICH)
- Quality and validation language
- Risk management concepts

---

### 6. CMC (Chemistry, Manufacturing, and Controls)

**Role**: Develops and controls manufacturing processes

**Key Concerns**:
- Process optimization
- Scale-up and tech transfer
- Quality control
- Stability prediction
- Process Analytical Technology (PAT)

**AI Applications They Care About**:
- Process optimization models
- Crystallization prediction
- Stability prediction
- Impurity prediction
- Formulation optimization

**Language Preferences**:
- Manufacturing terminology
- Quality control metrics
- Process parameters

---

### 7. DataScience (Data Scientist / ML Engineer)

**Role**: Develops and deploys AI/ML models

**Key Concerns**:
- Model architecture and training
- Benchmarking and validation
- Deployment and MLOps
- Data quality and curation
- Reproducibility

**AI Applications They Care About**:
- All of the above, from technical perspective
- Model comparison and selection
- Infrastructure and tooling

**Language Preferences**:
- Technical ML terminology
- Benchmark metrics (AUROC, RMSE)
- Implementation details

---

### 8. General (Cross-Functional / Leadership)

**Role**: Broad oversight across drug discovery

**Key Concerns**:
- Strategic value of AI
- Resource allocation
- Timeline and productivity
- Risk management
- Integration across functions

**AI Applications They Care About**:
- End-to-end pipeline integration
- Portfolio-level impact
- ROI and productivity metrics

**Language Preferences**:
- High-level summaries
- Business impact language
- Strategic framing

---

## Coverage Requirements

### Minimum Coverage Rule
Pharma×AI reviews **MUST** meaningfully address at least 3 distinct personas.

### Coverage Verification
In Issues CSV, each Writing issue should have `Persona` column filled:
- Single persona: `MedicinalChem`
- Multiple personas: `MedicinalChem;DMPK;DataScience`

### QA Check
During Phase 3 QA:
1. Tally persona coverage across all Writing issues
2. Ensure ≥3 unique personas are represented
3. Verify no single persona dominates >50% of content

---

## Writing Guidance

### Adapting Language by Persona

**For MedicinalChem audience**:
> The model prioritizes compounds with cLogP < 3 and TPSA 60-120 Å², 
> aligning with oral drug-likeness heuristics familiar to medicinal chemists.

**For DataScience audience**:
> The GNN architecture uses message-passing layers with edge features 
> encoding bond order and stereochemistry, achieving 0.89 AUROC on held-out scaffolds.

**For ClinPharm audience**:
> Model predictions were validated against Phase I PK data from 23 compounds, 
> showing correlation with observed human clearance (R² = 0.72).

### Section Mapping

| Section | Primary Personas | Secondary Personas |
|---------|-----------------|-------------------|
| Introduction | General | All |
| Data & Representations | DataScience | MedicinalChem |
| Model Architectures | DataScience | All |
| Hit Discovery | MedicinalChem | Biology |
| Lead Optimization | MedicinalChem | DMPK |
| ADMET Prediction | DMPK | MedicinalChem, Regulatory |
| Synthesis Planning | MedicinalChem | CMC |
| Clinical Translation | ClinPharm | Biology, Regulatory |
| Regulatory Considerations | Regulatory | All |
| Future Directions | General | All |

---

## Cross-Reference

- `references/pharma-task-dictionary.md`: Tasks by persona relevance
- `references/review-writing-playbook.md`: Section narrative loop includes "Pharma Implications"
- `assets/scope-template.yaml`: Persona configuration
