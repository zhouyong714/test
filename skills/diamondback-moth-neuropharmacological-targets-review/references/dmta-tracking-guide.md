# DMTA Closed-Loop Tracking Guide

> **Version**: 2.4  
> **Last Updated**: 2026-01-06  
> **Purpose**: Track Design-Make-Test-Analyze cycle integration with AI methods

---

## Overview

The DMTA (Design-Make-Test-Analyze) cycle is the fundamental iterative process in drug discovery. This guide establishes how to track and document AI's role in closing the loop.

---

## DMTA Stages

| Stage | Description | AI Role | Key Metrics |
|-------|-------------|---------|-------------|
| **Design** | Molecule/antibody/formulation design | Generative models, MPO optimization, retrosynthesis | Novel scaffolds, property profile |
| **Make** | Synthesis/expression/preparation | Reaction prediction, route optimization | Yield, success rate |
| **Test** | Experimental testing/screening | HTS analysis, phenotypic screening | Hit rate, activity |
| **Analyze** | Data analysis/model iteration | Active learning, model refinement | Model improvement, prediction accuracy |
| **Cross** | End-to-end pipeline integration | Full loop automation | Cycle time, throughput |

---

## Closed-Loop Verification

### Definition
A method has "closed-loop verification" when:
1. AI generates predictions/proposals
2. Wet-lab experiments test the predictions
3. Results feed back to improve the model
4. Cycle repeats with demonstrated improvement

### Verification Levels

| Level | Description | Evidence Required |
|-------|-------------|-------------------|
| **No Loop** | Retrospective benchmark only | Published benchmark results |
| **Partial** | AI → Wet-lab, no feedback | Experimental validation, single iteration |
| **Single Loop** | One complete DMTA cycle | Before/after model performance |
| **Multi-Loop** | Multiple iterations with improvement | Learning curve, cycle-over-cycle gains |
| **Production** | Deployed in routine discovery | Case studies, productivity metrics |

---

## Issues CSV Tracking

### DMTA Columns

| Column | Values | Description |
|--------|--------|-------------|
| `DMTA_Stage` | Design, Make, Test, Analyze, Cross | Primary stage |
| `Closed_Loop_Verified` | Y, N, Partial | Verification status |
| `Loop_Iterations` | Integer | Number of complete cycles |
| `Feedback_Mechanism` | active_learning, retrain, ensemble_update | How feedback works |

### Examples

**Design Stage (Generative MPO)**:
```csv
DMTA_Stage,Closed_Loop_Verified,Loop_Iterations,Feedback_Mechanism
Design,Y,3,active_learning
```

**Test Stage (HTS Analysis)**:
```csv
DMTA_Stage,Closed_Loop_Verified,Partial,1,retrain
Test,Partial,1,retrain
```

---

## Writing Guidance

### When to Highlight Closed-Loop

In pharma×AI reviews, closed-loop examples are high-value evidence:

1. **Section Narrative Loop**: Use closed-loop cases in "Pharma Implications" paragraph
2. **Evidence Table**: Mark `Evidence_Level=L3` for prospective/closed-loop studies
3. **Limitations**: Note when a method lacks closed-loop validation

### Example Paragraph

> The REINVENT 3.0 framework has been validated in multiple closed-loop discovery 
> campaigns at AstraZeneca [Smith2023]. In a retrospective analysis of 47 projects, 
> molecules proposed by REINVENT showed a 2.3× higher experimental hit rate compared 
> to human-designed analogs. Critically, **the model was retrained after each synthesis 
> cycle**, incorporating experimental pIC50 values to improve subsequent predictions [Jones2024].
>
> However, this closed-loop evidence comes from a single organization with proprietary 
> data, limiting generalizability to academic or smaller pharma settings.

---

## Failure Modes to Document

When reviewing DMTA integration, explicitly discuss:

1. **Data latency**: Delay between experiment and model update
2. **Synthesis bottleneck**: AI proposes faster than synthesis can deliver
3. **Assay noise**: Experimental variance exceeds model precision
4. **Distribution shift**: Test compounds drift from training domain
5. **Human-in-loop friction**: Scientists override model suggestions

---

## Cross-Reference

- `references/evidence-ladder.md`: L3 (Prospective) requires closed-loop
- `references/pharma-task-dictionary.md`: Tasks amenable to DMTA integration
- `assets/study-table-template.csv`: `DMTA_Stage` and `Closed_Loop` columns
