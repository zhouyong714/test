# Pharma Outline Templates

> **Version**: 2.4  
> **Purpose**: 药学×AI 综述的大纲模板库，按 Drug R&D Lifecycle 组织

---

## 模板选择指南

| 综述焦点 | 推荐模板 |
|----------|----------|
| 特定疾病领域 (如 Cancer AI) | Template A: Disease-Centric |
| 特定技术 (如 GNN for Molecules) | Template B: Technology-Centric |
| 研发阶段 (如 ADMET Prediction) | Template C: Lifecycle-Stage |
| 全景综述 (AI in Drug Discovery) | Template D: Panorama |

---

## Template A: Disease-Centric (疾病中心型)

适用于：特定疾病领域的 AI 应用综述

```markdown
# [Disease Name] and AI: A Comprehensive Review

## 1. Introduction (1.5 pages)
- 1.1 Disease burden and unmet needs (Context)
- 1.2 Current treatment landscape challenges (Pain Point)
- 1.3 Why AI for [Disease]? (Gap Statement)
- 1.4 Scope and deliverables of this review

## 2. Taxonomy of AI Applications in [Disease] (1 page)
- 2.1 Classification framework
- 2.2 Mapping to drug R&D lifecycle

## 3. Target Identification and Validation (1.5 pages)
- 3.1 Disease mechanism modeling
- 3.2 Druggable target prediction
- 3.3 Representative methods and benchmarks
- 3.4 Failure modes and pharma implications

## 4. Hit Discovery and Lead Optimization (1.5 pages)
- 4.1 Virtual screening for [Disease] targets
- 4.2 Generative models for [Disease]-specific molecules
- 4.3 ADMET considerations for [Disease]
- 4.4 Failure modes and pharma implications

## 5. Clinical Translation (1 page)
- 5.1 Patient stratification and biomarkers
- 5.2 Clinical trial optimization
- 5.3 Real-world evidence integration
- 5.4 Regulatory considerations

## 6. Challenges and Roadmap (1 page)
- 6.1 Data availability and quality
- 6.2 Interpretability for clinical adoption
- 6.3 Actionable roadmap (6-18m, 2-5y)

## 7. Conclusion (0.5 pages)
```

---

## Template B: Technology-Centric (技术中心型)

适用于：特定 AI 技术在药学中的应用综述

```markdown
# [AI Technology] for Drug Discovery: A Review

## 1. Introduction (1.5 pages)
- 1.1 Evolution of [Technology] in chemistry/biology (Context)
- 1.2 Limitations of prior approaches (Pain Point)
- 1.3 What [Technology] uniquely enables (Gap Statement)
- 1.4 Scope and deliverables

## 2. Technical Foundations (1 page)
- 2.1 Core principles of [Technology]
- 2.2 Taxonomy of architectural variants
- 2.3 Key inductive biases for molecular applications

## 3. Applications Across Drug R&D (3 pages)
- 3.1 Target identification with [Technology]
- 3.2 Molecular property prediction
- 3.3 Generative molecular design
- 3.4 Drug-drug interaction prediction
- 3.5 Clinical outcome prediction

## 4. Benchmarks and Evaluation (1 page)
- 4.1 Standard benchmarks
- 4.2 Pharma-relevant evaluation metrics
- 4.3 Gap between benchmarks and real-world

## 5. Failure Modes and Limitations (1 page)
- 5.1 When [Technology] fails
- 5.2 Data requirements and biases
- 5.3 Interpretability challenges

## 6. Future Directions and Roadmap (1 page)
- 6.1 Emerging variants and extensions
- 6.2 Integration with experimental workflows
- 6.3 Actionable roadmap

## 7. Conclusion (0.5 pages)
```

---

## Template C: Lifecycle-Stage (研发阶段型)

适用于：特定研发阶段的 AI 方法综述

```markdown
# AI for [R&D Stage]: Methods, Benchmarks, and Future Directions

## 1. Introduction (1.5 pages)
- 1.1 Role of [Stage] in drug development (Context)
- 1.2 Bottlenecks and failure rates (Pain Point)
- 1.3 Promise and gaps in AI for [Stage] (Gap Statement)
- 1.4 Scope: what this review covers

## 2. Problem Formulation (0.5 pages)
- 2.1 Input/output specifications
- 2.2 Success metrics in pharma context

## 3. Taxonomy of Methods (1 page)
- 3.1 By model architecture
- 3.2 By data modality
- 3.3 By learning paradigm

## 4. Method Deep Dives (3 pages)
- 4.1 Category A methods
  - Mechanism, representatives, failures, implications
- 4.2 Category B methods
  - Mechanism, representatives, failures, implications
- 4.3 Category C methods
  - Mechanism, representatives, failures, implications

## 5. Benchmarks and Datasets (1 page)
- 5.1 Established benchmarks
- 5.2 Dataset quality issues
- 5.3 Reproducibility concerns

## 6. Industrial Adoption (0.5 pages)
- 6.1 Case studies from pharma
- 6.2 Integration challenges

## 7. Roadmap and Conclusion (1 page)
- 7.1 Short-term priorities (6-18m)
- 7.2 Medium-term vision (2-5y)
- 7.3 Concluding remarks
```

---

## Template D: Panorama (全景型)

适用于：AI 在药物研发整体的全景综述

```markdown
# Artificial Intelligence in Drug Discovery and Development: A Panoramic Review

## 1. Introduction (2 pages)
- 1.1 The drug discovery challenge (Context)
- 1.2 AI's transformative potential (Why now)
- 1.3 Current state and gaps (Gap Statement)
- 1.4 What this review provides (Scope & Deliverables)

## 2. Taxonomy and Organization (1.5 pages)
- 2.1 AI techniques landscape
- 2.2 Drug R&D lifecycle stages
- 2.3 Our organizing framework

## 3. Target Discovery and Validation (1 page)
- 3.1 Key methods and results
- 3.2 Limitations

## 4. Hit Discovery (1 page)
- 4.1 Virtual screening
- 4.2 De novo design
- 4.3 Limitations

## 5. Lead Optimization (1 page)
- 5.1 QSAR and property prediction
- 5.2 Generative optimization
- 5.3 Limitations

## 6. ADMET and Safety (1 page)
- 6.1 Pharmacokinetics prediction
- 6.2 Toxicity prediction
- 6.3 Limitations

## 7. Clinical Development (1 page)
- 7.1 Patient stratification
- 7.2 Trial optimization
- 7.3 Limitations

## 8. Cross-Cutting Challenges (1 page)
- 8.1 Data quality and availability
- 8.2 Interpretability and trust
- 8.3 Regulatory landscape

## 9. Future Roadmap (1 page)
- 9.1 Short-term priorities
- 9.2 Medium-term vision
- 9.3 Long-term speculation

## 10. Conclusion (0.5 pages)
```

---

## 使用说明

1. 根据综述主题选择最合适的模板
2. 调整章节深度以匹配目标页数
3. 确保每个技术章节遵循 Section Loop (Mechanism → Methods → Failures → Implications)
4. 验证 Taxonomy 出现在前 20% 位置
5. 确保 Roadmap 有具体时间线
