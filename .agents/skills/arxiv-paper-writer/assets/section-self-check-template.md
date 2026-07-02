# Section Self-Check Template

> Per-section QA checklist for Writing Playbook compliance.
> Complete this for each technical section before marking issue as DONE.

---

## Section Information

- **Section Number**: `§___`
- **Section Title**: `_______________`
- **Issue ID**: `_______________`
- **Reviewer**: `_______________`
- **Date**: `_______________`

---

## Playbook Rule 4: Section Narrative Loop

### ✅ Mechanism Paragraph (1¶)
- [ ] Explains WHY the approach works
- [ ] Describes inductive bias or mathematical principle
- [ ] Connects to domain intuition (pharma context)
- [ ] Length: 3-5 sentences

**Mechanism summary**: `_______________________________________________`

### ✅ Representative Methods (2-4¶)
- [ ] Covers 3-5 representative methods (not exhaustive listing)
- [ ] Includes comparison/contrast between methods
- [ ] Highlights innovations and improvements
- [ ] Uses specific citations for each method
- [ ] Avoids pure enumeration ("Method A does X. Method B does Y.")

**Methods covered**: `_______________________________________________`

### ✅ Failure Modes (≥1¶)
- [ ] Explicitly states when/why the approach FAILS
- [ ] Describes boundary conditions and edge cases
- [ ] Mentions data requirements and limitations
- [ ] Acknowledges computational/practical constraints
- [ ] Uses hedging language appropriately ("may", "can", "under certain conditions")

**Failure modes identified**: `_______________________________________________`

### ✅ Pharma Implications (1¶)
- [ ] Addresses how practitioners would USE this approach
- [ ] Connects to specific R&D stage decisions
- [ ] Provides actionable insight for domain users
- [ ] Maps back to taxonomy/scope

**Practitioner takeaway**: `_______________________________________________`

---

## Playbook Rule 6: Evidence Binding

### Citation Density
- [ ] No 3+ sentences without a citation
- [ ] Quantitative claims have citations
- [ ] Method descriptions cite original papers

**Citation count in section**: `___` citations in `___` paragraphs

### Uncertainty Language
- [ ] Strong claims backed by L2+ evidence
- [ ] Weaker claims use hedging: "preliminary", "suggests", "may", "early evidence"
- [ ] Preprints marked with `[Preprint]`

### Evidence Level Distribution
| Level | Count | Percentage |
|-------|-------|------------|
| L0 | | |
| L1 | | |
| L2 | | |
| L3 | | |

**Minimum L2 evidence present?** [ ] Yes [ ] No

---

## Content Quality Checks

### Taxonomy Alignment
- [ ] Section topics align with taxonomy.yaml vocabulary
- [ ] Task/method terms used consistently
- [ ] Clear mapping to classification in §3

### Scope Compliance
- [ ] Content stays within scope.yaml boundaries
- [ ] Out-of-scope topics acknowledged but not deep-dived
- [ ] R&D stage relevance maintained

### Critical Limitations
- [ ] At least 2 limitations discussed in section
- [ ] Limitations are specific (not generic "needs more data")
- [ ] Future work suggestions connected to limitations

**Limitations listed**:
1. `_______________________________________________`
2. `_______________________________________________`

---

## Technical Accuracy

### Terminology
- [ ] Technical terms defined or cited on first use
- [ ] Acronyms expanded on first use
- [ ] Consistent terminology throughout

### Equations/Formulas (if applicable)
- [ ] Equations numbered and referenced
- [ ] Variables defined
- [ ] Notation consistent with field conventions

### Figures/Tables (if applicable)
- [ ] Figures cited in text before appearance
- [ ] Figure captions self-contained
- [ ] Tables have clear column headers
- [ ] Visual elements serve narrative purpose

---

## Length and Flow

### Paragraph Rhythm
- [ ] Varied paragraph lengths (not all same size)
- [ ] Topic sentences present
- [ ] Transitions between paragraphs

### Word Count
- **Target**: `___` words
- **Actual**: `___` words
- **Status**: [ ] On target [ ] Over [ ] Under

### Reading Flow
- [ ] Reads smoothly without backtracking
- [ ] Logical progression of ideas
- [ ] No orphan sentences or abrupt topic changes

---

## Final Checklist

| Requirement | Status | Notes |
|-------------|--------|-------|
| Mechanism ¶ | [ ] | |
| Methods ¶¶ | [ ] | |
| Failure ¶ | [ ] | |
| Pharma ¶ | [ ] | |
| Citations | [ ] | |
| Evidence levels | [ ] | |
| Limitations | [ ] | |
| Taxonomy aligned | [ ] | |
| Length appropriate | [ ] | |

---

## Sign-off

**Section ready for integration?** [ ] Yes [ ] No, needs revision

**If no, required revisions**:
1. `_______________________________________________`
2. `_______________________________________________`
3. `_______________________________________________`

**Signed off by**: `_______________`
**Date**: `_______________`
