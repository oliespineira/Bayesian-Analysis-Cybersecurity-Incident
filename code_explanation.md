# Detailed Code Explanation: Freelandia Bayesian Network

## Table of Contents
1. [Overview](#overview)
2. [Network Structure](#network-structure)
3. [Probability Distributions Explained](#probability-distributions-explained)
4. [Inference Engine](#inference-engine)
5. [Case Study Analysis](#case-study-analysis)

---

## Overview

This code implements a **Discrete Bayesian Network** for the Freelandia Case Study from DIGITAL FOG: INTELLIGENCE, CYBERSECURITY AND THE NEW FRONTLINES OF GEOPOLITICS. It has been constructed given the evidence from the first common case study regarding the Island's situation and the first Russian Intelligence package. This network has been created using the `pgmpy` library. The network models probabilistic relationships between:

- **Sponsor identity** (hypothesis)
- **Operational capabilities and motives**
- **Evidence observations**
- **Attribution confidence**
- **Policy consequences**
- 

### Key Components

## Installation

Before running the project, make sure to install the required dependencies:

```bash
pip install -r requirements.txt


These libraries are being used:

```python
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
```

- `DiscreteBayesianNetwork`: The graph structure (nodes + edges)
- `TabularCPD`: Conditional Probability Distributions
- `VariableElimination`: Exact inference algorithm



## Network Structure

### 1. Hypothesis Node

```python
H = "H_sponsor"  # 0=Russia, 1=NewRepublic, 2=FPD, 3=US, 4=Other
```

**Prior Distribution:**
```python
cpd_H = TabularCPD(
    variable=H, variable_card=5,
    values=[[0.22], [0.22], [0.18], [0.08], [0.30]]
)
```

- **Cardinality**: 5 states (5 possible sponsors)
- **Values**: Column vector representing P(H)
  - Russia: 22%
  - NewRepublic: 22%
  - FPD: 18%
  - US: 8%
  - Other: 30%

**Interpretation**: This represents our prior belief BEFORE seeing any evidence. "Other" has highest probability (30%) reflecting uncertainty.

---

### 2. Deception Nodes

#### Proxy Use

```python
cpd_proxy = TabularCPD(
    variable=proxy, variable_card=2,
    values=[
        [0.35, 0.40, 0.50, 0.25, 0.55],  # Proxy=False
        [0.65, 0.60, 0.50, 0.75, 0.45],  # Proxy=True
    ],
    evidence=[H], evidence_card=[5]
)
```

**Structure:**
- **Rows**: States of `proxy` (False=0, True=1)
- **Columns**: Conditioned on each sponsor (Russia, NR, FPD, US, Other)
- **Evidence**: Parent node is H_sponsor with 5 states

**Reading the table:**
- P(Proxy=True | Russia) = 0.65 (65% chance Russia uses proxy)
- P(Proxy=True | US) = 0.75 (75% chance US uses proxy)
- P(Proxy=True | FPD) = 0.50 (50% chance FPD uses proxy)

**Why these values?**
- Major powers (Russia, US) more likely to use proxies for deniability
- FPD (smaller actor) has 50-50 chance
- "Other" actors less sophisticated, use proxies less (45%)

#### False Flags

```python
cpd_falseflag = TabularCPD(
    variable=falseflag, variable_card=2,
    values=[
        [0.70, 0.75, 0.80, 0.55, 0.85],  # FalseFlag=False
        [0.30, 0.25, 0.20, 0.45, 0.15],  # FalseFlag=True
    ],
    evidence=[H], evidence_card=[5]
)
```

- P(FalseFlag=True | US) = 0.45 (highest: US most likely to plant false flags)
- P(FalseFlag=True | Russia) = 0.30
- P(FalseFlag=True | Other) = 0.15 (least sophisticated)

---

### 3. Capability Nodes

#### ICS Capability

```python
cpd_cap_ics = TabularCPD(
    variable=cap_ics, variable_card=3,
    values=[
        [0.10, 0.20, 0.55, 0.05, 0.45],  # Low
        [0.35, 0.45, 0.35, 0.20, 0.40],  # Med
        [0.55, 0.35, 0.10, 0.75, 0.15],  # High
    ],
    evidence=[H], evidence_card=[5]
)
```

**Structure:**
- **3 states**: Low=0, Med=1, High=2
- **Columns**: [Russia, NewRepublic, FPD, US, Other]

**Reading by sponsor:**

| Sponsor | P(Low) | P(Med) | P(High) |
|---------|--------|--------|---------|
| Russia  | 0.10   | 0.35   | **0.55** |
| NR      | 0.20   | **0.45** | 0.35 |
| FPD     | **0.55** | 0.35 | 0.10 |
| US      | 0.05   | 0.20   | **0.75** |
| Other   | 0.45   | 0.40   | 0.15 |

**Interpretation:**
- **US and Russia**: Advanced ICS capabilities (75% and 55% high)
- **NewRepublic**: Medium capability (balanced distribution)
- **FPD**: Weak ICS capability (55% low)
- **Other**: Mostly low to medium

**Why these distributions?**
- Based on known nation-state APT capabilities
- ICS attacks require specialized knowledge (SCADA, PLCs)
- US/Russia have demonstrated Stuxnet-level capability
- FPD is a less-developed state

Similar logic applies to:
- `cap_multi` (Multi-domain operations)
- `cap_io` (Information Operations)

---

### 4. Motive Nodes

#### Binary Motive Helper Function

```python
def cpd_binary(name, p_true_by_sponsor):
    p_false = [1 - p for p in p_true_by_sponsor]
    return TabularCPD(
        variable=name, variable_card=2,
        values=[p_false, p_true_by_sponsor],
        evidence=[H], evidence_card=[5]
    )
```

This helper creates binary CPTs where:
- Row 0: P(Motive=False)
- Row 1: P(Motive=True)

#### Punish West Motive

```python
cpd_m_punish = cpd_binary(m_punish, [0.35, 0.75, 0.30, 0.10, 0.20])
```

**Probabilities by sponsor:**
- Russia: 35% (moderate)
- **NewRepublic: 75%** (very high: they want to punish Western influence)
- FPD: 30%
- US: 10% (low: US wouldn't attack itself to punish West plus the US wouldn't lead to hospitals suffering consequences)
- Other: 20%

#### Undermine West Motive

```python
cpd_m_undermine = cpd_binary(m_undermine, [0.70, 0.35, 0.20, 0.10, 0.15])
```

- **Russia: 70%** (high: geopolitical adversary)
- NewRepublic: 35%
- FPD: 20%
- US: 10%
- Other: 15%

**Pattern**: Each sponsor has different motivational profile based on geopolitical context.

---

### 5. Aggregator Nodes

#### Intent Aggregation

```python
def intent_probs(m_true_count):
    if m_true_count == 0:
        return [0.80, 0.18, 0.02]  # Mostly Low intent
    if m_true_count == 1:
        return [0.45, 0.45, 0.10]  # Balanced
    if m_true_count == 2:
        return [0.20, 0.55, 0.25]  # Mostly Medium
    if m_true_count == 3:
        return [0.10, 0.40, 0.50]  # Mostly High
    return [0.05, 0.25, 0.70]      # Very High (4 motives)
```

**Logic**: More active motives leads to Higher intent

The CPT is built by iterating over all combinations:

```python
intent_vals = [[], [], []]
for mp in [0,1]:           # Motive_Punish
    for mu in [0,1]:       # Motive_Undermine
        for md in [0,1]:   # Motive_Domestic
            for mc in [0,1]:  # Motive_CasusBelli
                cnt = mp + mu + md + mc
                pL, pM, pH = intent_probs(cnt)
                intent_vals[0].append(pL)
                intent_vals[1].append(pM)
                intent_vals[2].append(pH)
```

**Result**: 2^4 = 16 columns (all combinations of 4 binary motives)

**Example scenarios:**
- All motives False (0000): 80% Low, 18% Med, 2% High intent
- Two motives True: 20% Low, 55% Med, 25% High intent
- All motives True (1111): 5% Low, 25% Med, 70% High intent

#### Means Aggregation

```python
means_vals = [[], [], []]
for c1 in [0,1,2]:      # Cap_ICS
    for c2 in [0,1,2]:  # Cap_Multidomain
        m = max(c1, c2)
        if m == 0:
            probs = [0.80, 0.18, 0.02]
        elif m == 1:
            probs = [0.25, 0.60, 0.15]
        else:
            probs = [0.10, 0.35, 0.55]
        means_vals[0].append(probs[0])
        means_vals[1].append(probs[1])
        means_vals[2].append(probs[2])
```

**Logic**: Take the maximum of two capability dimensions
- If max capability is Low (0): Mostly low means
- If max capability is Medium (1): Mostly medium means
- If max capability is High (2): Mostly high means

**Why max instead of average?**
- In practice, an attacker only needs ONE high capability domain
- If you're expert in ICS but weak in multi-domain, you can still execute sophisticated ICS attacks

---

### 6. Planning Node

```python
plan_false = []
plan_true = []
for i in [0,1,2]:        # Intent
    for m in [0,1,2]:    # Means
        for o in [0,1,2]:  # Opportunity
            score = i + m + o  # Range: 0-6
            if score <= 1:
                pT = 0.05
            elif score == 2:
                pT = 0.15
            elif score == 3:
                pT = 0.35
            elif score == 4:
                pT = 0.60
            elif score == 5:
                pT = 0.80
            else:
                pT = 0.90
            plan_true.append(pT)
            plan_false.append(1 - pT)
```

**Logic**: Operation gets planned if Intent + Means + Opportunity are all high

**Scoring:**
- Score 0-1: Only 5% chance operation is planned
- Score 3 (median): 35% chance
- Score 6 (maximum): 90% chance

**Example:**
- Intent=High(2), Means=High(2), Opportunity=High(2) → score=6 → 90% planned
- Intent=Low(0), Means=Low(0), Opportunity=Med(1) → score=1 → 5% planned

---

### 7. Execution Nodes

#### Cyber Operation

```python
cpd_cyber = TabularCPD(
    variable=cyber, variable_card=2,
    values=[[0.97, 0.15],    # Cyber=False
            [0.03, 0.85]],   # Cyber=True
    evidence=[planned], evidence_card=[2]
)
```

**Reading:**
- P(Cyber=True | Planned=False) = 0.03 (3%: rare to execute without planning)
- P(Cyber=True | Planned=True) = 0.85 (85%: high execution rate when planned)

**Interpretation**: If operation is NOT planned, very unlikely cyber component executes. If planned, high likelihood.

#### Coordination

```python
cpd_coord = TabularCPD(
    variable=coord, variable_card=2,
    values=[
        [0.99, 0.55, 0.55, 0.15],  # Coordination=False
        [0.01, 0.45, 0.45, 0.85],  # Coordination=True
    ],
    evidence=[cyber, drone], evidence_card=[2,2]
)
```

**Columns**: (Cyber=0,Drone=0), (Cyber=0,Drone=1), (Cyber=1,Drone=0), (Cyber=1,Drone=1)

**Reading:**
- P(Coord=True | Cyber=False, Drone=False) = 0.01 (no ops → no coordination)
- P(Coord=True | Cyber=True, Drone=True) = 0.85 (both ops → high coordination)
- P(Coord=True | Only one op) = 0.45 (partial coordination possible)

---

### 8. Evidence Generation

Evidence nodes model **likelihood** of observing indicators given underlying states.

#### Vendor Path Evidence

```python
p_vendor_true = []
for cy in [0,1]:           # Cyber executed?
    for av in [0,1]:       # Vendor access available?
        for rf in [0,1,2]: # Forensic reliability
            if cy == 0:
                base = 0.05  # No cyber op: rarely see vendor path
            else:
                base = 0.35 if av == 0 else 0.80
                # Cyber executed:
                #   - Without vendor access: 35% chance we find evidence
                #   - With vendor access: 80% chance we find evidence
            
            # Reliability modifier
            mod = {0: -0.15, 1: 0.0, 2: 0.10}[rf]
            p = min(max(base + mod, 0.01), 0.99)
            p_vendor_true.append(p)
```

**Logic breakdown:**

1. **Base probability** depends on operational reality:
   - If no cyber op executed: base = 5% (false positive rate)
   - If cyber op executed:
     - With vendor access: 80% (attackers used this path, we likely find it)
     - Without vendor access: 35% (they used different path, might still leave traces)

2. **Reliability modifier** adjusts based on forensic quality:
   - Low reliability: -0.15 (might miss evidence)
   - Medium reliability: 0.0 (no adjustment)
   - High reliability: +0.10 (more likely to find evidence)

3. **Clamping**: Ensure probability stays in (0.01, 0.99) range

**Example scenarios:**
- Cyber=True, Access=True, Reliability=High: p = 0.80 + 0.10 = 0.90
- Cyber=True, Access=False, Reliability=Low: p = 0.35 - 0.15 = 0.20
- Cyber=False, Reliability=High: p = 0.05 + 0.10 = 0.15

#### Logic Altered Evidence

```python
p_logic_true = []
for cy in [0,1]:
    for ci in [0,1,2]:     # ICS capability
        for rf in [0,1,2]:
            if cy == 0:
                base = 0.04  # False positive
            else:
                base = [0.35, 0.65, 0.85][ci]
                # Low ICS cap: 35% detection
                # Med ICS cap: 65% detection
                # High ICS cap: 85% detection
            
            mod = {0: -0.12, 1: 0.0, 2: 0.08}[rf]
            p = min(max(base + mod, 0.01), 0.99)
            p_logic_true.append(p)
```

**Key insight**: Higher ICS capability: More sophisticated logic alteration: Higher detection probability

**Why?** More sophisticated attackers leave more detectable traces in the logic (they alter MORE things, or alter them in ways that are eventually discovered).

---

### 9. Attribution Fog

This is complex because it depends on 4 parents:

```python
p_fog_true = []
for cio in [0,1,2]:        # IO capability
    for ff in [0,1]:       # False flag
        for pr in [0,1]:   # Proxy
            for ri in [0,1,2]:  # Intel reliability
                base = [0.25, 0.45, 0.65][cio]
                # Higher IO capability → More fog
                
                if ff == 1: base += 0.10  # False flag adds fog
                if pr == 1: base += 0.10  # Proxy adds fog
                
                mod = {0: -0.10, 1: 0.0, 2: 0.05}[ri]
                p = min(max(base + mod, 0.01), 0.99)
                p_fog_true.append(p)
```

**Logic:**
1. **Base from IO capability**: Better IO → more likely to create narratives
2. **False flags add 10%**: Planting false flags creates confusion
3. **Proxies add 10%**: Using proxies muddies attribution
4. **Reliability**: Better intel can partially cut through fog (+5% for high)

**Example:**
- High IO (cio=2), False flag, Proxy, Low intel reliability:
  - base = 0.65 + 0.10 + 0.10 = 0.85
  - mod = -0.10
  - p = 0.75 (75% chance we observe attribution fog)

---

### 10. Attribution Certainty

This is the **most complex CPD** (576 combinations):

```python
attr_vals = [[], [], []]
for ev in [0,1]:           # E_vendor
    for el in [0,1]:       # E_logic
        for et in [0,1]:   # E_tight
            for ef in [0,1]:   # E_fog
                strength = ev + el + et  # 0-3
                for ff in [0,1]:
                    for pr in [0,1]:
                        for rf in [0,1,2]:
                            for ri in [0,1,2]:
                                # Baseline from technical evidence
                                if strength == 0:
                                    pH = 0.05
                                elif strength == 1:
                                    pH = 0.15
                                elif strength == 2:
                                    pH = 0.35
                                else:
                                    pH = 0.60
                                
                                # Deception reduces certainty
                                if ef == 1: pH -= 0.15
                                if ff == 1: pH -= 0.10
                                if pr == 1: pH -= 0.10
                                
                                # Reliability increases certainty
                                pH += {0: -0.05, 1: 0.0, 2: 0.05}[rf]
                                pH += {0: -0.04, 1: 0.0, 2: 0.04}[ri]
                                
                                pH = float(min(max(pH, 0.01), 0.90))
                                
                                # Split remainder
                                rem = 1 - pH
                                if strength >= 2:
                                    pM = rem * 0.65
                                    pL = rem * 0.35
                                else:
                                    pM = rem * 0.45
                                    pL = rem * 0.55
```

**Multi-stage logic:**

1. **Technical strength** (0-3): Count of strong technical evidence
   - 0 pieces: 5% high certainty
   - 3 pieces: 60% high certainty

2. **Deception penalties**:
   - Attribution fog: -15%
   - False flag: -10%
   - Proxy: -10%
   - (Can stack up to -35% reduction!)

3. **Reliability bonuses**:
   - High forensic reliability: +5%
   - High intel reliability: +4%

4. **Remainder distribution**: Split leftover probability between Low/Medium
   - Strong evidence → favor Medium over Low
   - Weak evidence → favor Low over Medium

**Example calculation:**
```
Evidence: vendor=1, logic=1, tight=1, fog=1
Deception: ff=1, proxy=1
Reliability: both high

strength = 1 + 1 + 1 = 3
pH_base = 0.60
pH_deception = 0.60 - 0.15 - 0.10 - 0.10 = 0.25
pH_reliability = 0.25 + 0.05 + 0.04 = 0.34
pH_final = 0.34 (clipped to [0.01, 0.90])

remainder = 1 - 0.34 = 0.66
pM = 0.66 * 0.65 = 0.43
pL = 0.66 * 0.35 = 0.23

Result: [pL=0.23, pM=0.43, pH=0.34]
```

---

### 11. Sanctions

```python
for h in range(5):     # Each sponsor
    for c in [0,1,2]:  # Attribution certainty
        # Base by certainty
        if c == 0:
            none, lim, exp = 0.60, 0.35, 0.05
        elif c == 1:
            none, lim, exp = 0.35, 0.50, 0.15
        else:
            none, lim, exp = 0.20, 0.50, 0.30
        
        # Sponsor-specific adjustments
        if h == 0:  # Russia
            exp += 0.10 if c == 2 else 0.05 if c == 1 else 0.00
            none -= 0.05
        elif h == 1:  # NewRepublic
            exp += 0.05 if c == 2 else 0.02 if c == 1 else 0.00
            none -= 0.03
        elif h == 3:  # US
            exp -= 0.10
            none += 0.08
        
        # Normalize
        vec = np.array([max(none,0.01), max(lim,0.01), max(exp,0.01)])
        vec = (vec / vec.sum()).tolist()
```

**Logic:**

1. **Base by certainty**: Higher certainty → stronger sanctions
2. **Sponsor adjustments**:
   - Russia: More likely to face expanded sanctions (geopolitical rival)
   - US: Less likely to face sanctions (self-attribution paradox)
   - NewRepublic: Slight increase to expanded

**Example:**
- Russia, High certainty:
  - base: [0.20, 0.50, 0.30]
  - adjusted: [0.15, 0.50, 0.40]
  - normalized: [0.143, 0.476, 0.381]

---

### 12. Escalation Risk

```python
for s in [0,1,2]:      # Sanctions level
    for m in [0,1,2]:  # Military presence
        score = s + m  # 0-4
        if score <= 1:
            p = [0.75, 0.22, 0.03]
        elif score == 2:
            p = [0.45, 0.45, 0.10]
        elif score == 3:
            p = [0.25, 0.50, 0.25]
        else:
            p = [0.15, 0.45, 0.40]
```

**Simple additive logic**: Combined policy response intensity → escalation risk

---

## Inference Engine

### Variable Elimination Algorithm

```python
inference = VariableElimination(model)
```

Variable Elimination works by:

1. **Instantiate evidence**: Set observed variables to their values
2. **Create factors**: CPTs become factor functions
3. **Elimination order**: Choose order to eliminate hidden variables
4. **Marginalization**: Sum out variables one by one
5. **Normalization**: Ensure result sums to 1.0

### Query Example

```python
evidence = {
    e_vendor: 1,
    e_patient: 1,
    e_logic: 1,
    e_drone_coord: 1,
    e_drone_low: 1,
    e_serial: 1,
    e_tight: 1,
    e_fog: 1,
    e_fastmsg: 1,
    rel_for: 2,  # High
    rel_int: 1   # Medium
}

result = inference.query([H], evidence=evidence)
```

**What happens:**

1. Evidence nodes are "clamped" to observed values
2. Algorithm computes: P(H | all evidence)
3. Result is posterior distribution over 5 sponsors

**Computational complexity:**
- Exact inference in BNs is NP-hard in general
- But with Variable Elimination and good elimination ordering, tractable for networks of this size
- Largest factor size: ~1,728 entries (Attribution CPT)

---

## Key Insights

### 1. Hierarchical Structure
```
Sponsor → Capabilities/Motives → Intent/Means/Opportunity 
       → Planning → Execution → Evidence → Attribution → Consequences
```

### 2. Discriminative Evidence
Not all evidence is equally informative:
- **Strong**: E_logic, E_tight (directly tied to capabilities)
- **Weak**: E_fastmsg (many actors message quickly)
- **Deceptive**: E_fog (reduces certainty)

### 3. Reliability Matters
Same evidence with different reliability → different conclusions
- High reliability forensics can overcome some deception
- Low reliability can make strong evidence worthless

### 4. Deception Modeling
Explicit nodes for:
- Proxy use
- False flags
- Attribution fog

These directly reduce attribution certainty.

### 5. Policy Feedback
Consequences depend on both:
- Who did it (sponsor)
- How certain we are (attribution level)

This models realistic decision-making under uncertainty.

---

## Usage Patterns

### 1. Forward Reasoning
"If Russia is sponsor, what evidence would we expect?"
```python
evidence = {H: 0}  # Russia
result = inference.query([e_logic, e_vendor], evidence=evidence)
```

### 2. Backward Reasoning (Attribution)
"Given this evidence, who is most likely sponsor?"
```python
evidence = {e_vendor: 1, e_logic: 1, e_tight: 1}
result = inference.query([H], evidence=evidence)
```

### 3. Counterfactual Analysis
"What if forensic reliability was low instead of high?"
```python
evidence_high_rel = {..., rel_for: 2}
evidence_low_rel = {..., rel_for: 0}
compare_results()
```

### 4. Sensitivity Analysis
"Which evidence node matters most for attribution?"
```python
for ev_node in [e_vendor, e_logic, e_tight]:
    evidence_with = {**base_evidence, ev_node: 1}
    evidence_without = {**base_evidence, ev_node: 0}
    compare_posteriors()
```

---

## Summary

This Bayesian network represents a sophisticated approach to cyber-kinetic attack attribution that:

1. **Models uncertainty** explicitly through probability distributions
2. **Captures domain knowledge** in CPT specifications
3. **Handles deception** through dedicated nodes and probability adjustments
4. **Supports inference** for both attribution and consequence prediction
5. **Enables analysis** of evidence value and decision sensitivity

The probability values are based on qualitative assessments of:
- Nation-state capabilities (from threat intelligence)
- Geopolitical motives (from strategic analysis)
- Technical evidence reliability (from forensic best practices)
- Policy response patterns (from historical precedent)

While these probabilities are somewhat subjective, the **structure** of the network encodes genuine causal relationships, and the **inference** provides principled reasoning under uncertainty.
