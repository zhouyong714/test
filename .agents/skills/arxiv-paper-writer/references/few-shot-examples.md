# Few-Shot Examples for Review Writing Playbook

> Example paragraphs demonstrating the 6 playbook rules.
> Copy and adapt these patterns for your review.

---

## Rule 1: Opening Three-Part Structure

### Example: GNN for ADMET Prediction

```latex
% Part 1: Context/Trend (Why now)
The pharmaceutical industry faces mounting pressure to reduce drug development 
timelines and costs, with recent estimates suggesting that bringing a new drug 
to market now exceeds \$2.6 billion and takes over a decade~\cite{dimasi2016}. 
Graph neural networks (GNNs) have emerged as a promising approach to accelerate 
early-stage drug discovery by directly learning from molecular graph 
representations~\cite{gilmer2017,xiong2019}.

% Part 2: Pain Point (What hurts)
Despite the proliferation of GNN-based ADMET prediction models, practitioners 
in medicinal chemistry and DMPK departments struggle to select appropriate 
methods for their specific endpoints. Published benchmarks often use random 
splits that inflate performance estimates, while real-world deployments require 
scaffold-based generalization~\cite{wu2018moleculenet}.

% Part 3: Gap Statement (However/Yet/Despite)
\textbf{However}, no comprehensive review systematically evaluates GNN 
architectures across the full spectrum of ADMET endpoints using rigorous 
scaffold-split benchmarks, nor provides practitioners with actionable 
guidance on model selection for specific R\&D decision points.
```

### Pattern Template
```
[1-2 sentences: Field trend + urgency]
[1-2 sentences: Recent advances + citations]
[1-2 sentences: Core problem from practitioner perspective]
[1 sentence starting with However/Yet/Despite: Explicit gap]
```

---

## Rule 2: Scope & Deliverables

### Example: Scope Statement

```latex
This review provides a systematic evaluation of GNN methods for ADMET prediction, 
with the following scope and deliverables:

\begin{itemize}
    \item \textbf{Task coverage}: Absorption, Distribution, Metabolism, Excretion, 
          and Toxicity prediction across 12 key endpoints
    \item \textbf{Model scope}: Message-passing GNNs, attention-based architectures, 
          and hybrid approaches (2019--2024)
    \item \textbf{Evidence level}: Studies with scaffold-split validation (L2) or 
          experimental confirmation (L3)
    \item \textbf{Deliverables}: 
          (1) Taxonomy of GNN architectures for ADMET,
          (2) Benchmark comparison table with standardized metrics,
          (3) Decision guide mapping endpoints to recommended architectures,
          (4) Actionable roadmap for practitioners
\end{itemize}
```

### Pattern Template
```
[Intro sentence: "This review provides..."]
\begin{itemize}
    \item \textbf{Task coverage}: [Which AI/ML tasks]
    \item \textbf{Object scope}: [Which modalities/molecules/targets]
    \item \textbf{Evidence level}: [Which R&D stages, min evidence level]
    \item \textbf{Deliverables}: [3-5 specific outputs]
\end{itemize}
```

### ❌ Bad Example (Too Vague)
```latex
% DON'T DO THIS
We review recent progress in applying deep learning to drug discovery.
This paper surveys the field and discusses future directions.
```

---

## Rule 3: Taxonomy-First

### Example: Taxonomy Paragraph

```latex
\section{Taxonomy of GNN Architectures for Molecular Property Prediction}

We organize GNN approaches along three orthogonal axes that reflect 
decision-making in pharmaceutical R\&D (Figure~\ref{fig:taxonomy}):

\textbf{Axis 1: Graph representation level.} Methods operate on 2D molecular 
graphs (atom-bond topology), 3D conformer graphs (spatial coordinates), or 
multi-scale graphs (hierarchical substructure groupings).

\textbf{Axis 2: Message-passing mechanism.} We distinguish convolutional 
approaches~\cite{kipf2016gcn}, attentional mechanisms~\cite{velickovic2018gat}, 
and geometric equivariant networks~\cite{satorras2021egnn}.

\textbf{Axis 3: R\&D decision point.} Methods are mapped to their primary 
application: hit identification, lead optimization, or ADMET profiling.

Subsequent sections are organized by Axis 2, with subsections addressing 
performance across Axis 3 applications.
```

### Pattern Template
```
\section{Taxonomy...}

[Intro sentence: "We organize X along N axes..."]

\textbf{Axis 1: [Name].} [Description + examples]

\textbf{Axis 2: [Name].} [Description + examples]

\textbf{Axis 3: [Name].} [Description + examples]

[Sentence explaining how taxonomy maps to subsequent sections]
```

---

## Rule 4: Section Narrative Loop

### Example: Technical Section

```latex
\subsection{Graph Attention Networks for Property Prediction}

% Part 1: Mechanism (1¶) - WHY it works
Graph attention networks (GATs) address a fundamental limitation of 
spectral GNNs: the assumption that all neighbor atoms contribute equally 
to molecular properties. By introducing learnable attention coefficients 
$\alpha_{ij}$ between atom pairs, GATs can selectively weight the 
contribution of functional groups and scaffold patterns that are most 
predictive for specific endpoints~\cite{velickovic2018gat}. This 
attention-based inductive bias aligns with medicinal chemistry intuition, 
where specific pharmacophore patterns dominate property behavior.

% Part 2: Representative Methods (2-4¶) - WHAT exists
AttentiveFP~\cite{xiong2019} extends the basic GAT framework with 
graph-level attention, achieving state-of-the-art results on MoleculeNet 
benchmarks. Unlike standard GATs that aggregate to a fixed readout, 
AttentiveFP learns molecule-level attention over atom representations, 
enabling size-invariant property prediction.

PAGTN~\cite{chen2021} further improves upon AttentiveFP by incorporating 
path-based attention, capturing longer-range dependencies crucial for 
properties like membrane permeability. In contrast, MAT~\cite{maziarka2020} 
adopts a Transformer-style self-attention mechanism, treating molecules 
as fully-connected graphs with distance-based attention biases.

% Part 3: Failure Modes (≥1¶) - WHEN/WHY it fails
Despite their success, attention-based GNNs exhibit notable failure modes. 
First, attention weights can become uniformly distributed on large molecules, 
losing the selectivity advantage~\cite{knyazev2019understanding}. Second, 
models trained on drug-like molecules (MW < 500) generalize poorly to 
PROTACs and macrocycles, where long-range interactions dominate but training 
data is scarce. Third, attention patterns learned for one endpoint (e.g., 
solubility) may not transfer to another (e.g., hERG toxicity), limiting 
multi-task transfer learning.

% Part 4: Pharma Implications (1¶) - HOW practitioners use it
For medicinal chemists, GAT-based models offer interpretable atom-level 
attention maps that can guide structure-activity relationship (SAR) 
analysis. DMPK scientists should consider AttentiveFP or PAGTN for 
permeability endpoints where scaffold patterns are predictive. However, 
users should validate that attention patterns align with known 
pharmacophores before relying on model explanations for decision-making.
```

### Pattern Checklist
- [ ] ¶1: Mechanism - explains inductive bias/math principle
- [ ] ¶2-4: Methods - compares 3-5 methods, not just lists
- [ ] ¶5+: Failure modes - specific conditions, not generic "needs more data"
- [ ] Final ¶: Pharma implications - actionable for practitioners

---

## Rule 5: Actionable Roadmap

### Example: Conclusion Roadmap

```latex
\section{Conclusion and Future Directions}

[Key takeaways paragraph...]

\subsection{Research Roadmap}

\textbf{Short-term (6--18 months):}
\begin{itemize}
    \item Standardize scaffold-split benchmarks across ADMET endpoints 
          to enable fair model comparison
    \item Develop uncertainty quantification methods for GNN predictions 
          to support go/no-go decisions in lead optimization
    \item Create curated datasets for underrepresented endpoints 
          (e.g., PXR induction, bile salt export pump inhibition)
\end{itemize}

\textbf{Medium-term (2--5 years):}
\begin{itemize}
    \item Integrate GNN-based ADMET models into closed-loop 
          design-make-test-analyze (DMTA) cycles with automated synthesis
    \item Develop foundation models pre-trained on large chemical spaces 
          that can be fine-tuned for specific ADMET endpoints with minimal data
    \item Establish prospective validation protocols linking in-silico 
          predictions to clinical PK outcomes
\end{itemize}

Addressing the gap identified in Section~\ref{sec:intro}---the lack of 
systematic guidance for model selection---requires coordinated effort 
across computational chemistry, experimental DMPK, and machine learning 
communities.
```

### Pattern Template
```
\textbf{Short-term (6--18 months):}
\begin{itemize}
    \item [Data/benchmark improvement]
    \item [Method enhancement]
    \item [Community resource]
\end{itemize}

\textbf{Medium-term (2--5 years):}
\begin{itemize}
    \item [Integration/deployment goal]
    \item [Foundational advance]
    \item [Validation/translation goal]
\end{itemize}

[Sentence referencing back to Introduction gap]
```

### ❌ Bad Example (Too Generic)
```latex
% DON'T DO THIS
Future work should focus on improving model performance and 
addressing current limitations. More research is needed.
```

---

## Rule 6: Evidence Binding

### Example: Proper Citation Density

```latex
% GOOD: Every quantitative claim has a citation
GNN-based models have achieved AUROC values exceeding 0.90 on the BBBP 
benchmark~\cite{wang2023unimol}, representing a 5\% improvement over 
random forest baselines~\cite{wu2018moleculenet}. However, performance 
degrades significantly (AUROC 0.75--0.80) when evaluated on temporal 
splits simulating prospective deployment~\cite{chen2024temporal}.
```

### Example: Uncertainty Language

```latex
% Hedging for weaker evidence
Preliminary results \textit{suggest} that incorporating 3D conformer 
information \textit{may} improve predictions for stereoselective 
metabolism~\cite{preprint2024}~[Preprint]. Early evidence indicates 
that equivariant networks \textit{could} better capture chirality-dependent 
effects, though this \textit{requires further validation} with 
larger stereoisomer datasets.
```

### Example: Preprint Marking

```latex
% Preprints MUST be marked
Recent work on molecular foundation models~\cite{fang2024molfm}~[Preprint] 
proposes pre-training on 100M molecules, though peer-reviewed validation 
is pending. For key claims, we prioritize published results: Uni-Mol 
achieved state-of-the-art performance across 12 MoleculeNet 
tasks~\cite{zhou2023unimol}.
```

### Quick Rules
- ✅ No 3+ sentences without citation
- ✅ Quantitative claims always cited
- ✅ Preprints marked with `[Preprint]`
- ✅ Uncertainty language for L0-L1 evidence
- ❌ Preprints as sole evidence for key claims

---

## Checklist for Each Section

```markdown
## Section: _______________

### Rule 1 (Intro only)
- [ ] Context/Trend paragraph
- [ ] Pain Point paragraph  
- [ ] Gap statement (However/Yet/Despite)

### Rule 2 (Intro only)
- [ ] Scope bullets (3-6)
- [ ] Deliverables list

### Rule 3 (§2-3)
- [ ] Taxonomy figure/description
- [ ] Clear mapping to sections

### Rule 4 (Each technical section)
- [ ] Mechanism ¶
- [ ] Methods ¶¶ (comparison, not listing)
- [ ] Failure modes ¶
- [ ] Pharma implications ¶

### Rule 5 (Conclusion only)
- [ ] Short-term directions
- [ ] Medium-term directions
- [ ] Reference to intro gap

### Rule 6 (All sections)
- [ ] Citation density OK
- [ ] Quantitative claims cited
- [ ] Preprints marked
- [ ] Uncertainty language for weak evidence
```
