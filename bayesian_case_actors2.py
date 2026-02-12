import numpy as np
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

# ---------------------------------------------------------------------------------
# FREELANDIA INCIDENT - FIXED BAYESIAN NETWORK (Sponsor attribution + consequences)
# --------------------------------------------------------------------------------

model = DiscreteBayesianNetwork()

# -----------------------------------------------------------------------------
# Nodes
# -----------------------------------------------------------------------------
# Hypothesis
H = "H_sponsor"  # 0=Russia, 1=NewRepublic, 2=FPD, 3=US, 4=Other

# Deception/deniability
proxy = "Proxy_Used"           # 0=F, 1=T
falseflag = "FalseFlag_Planted" # 0=F, 1=T

# Capabilities (single nodes, conditioned on sponsor)
cap_ics = "Cap_Industrial_Control_Systems"            # 0=Low, 1=Med, 2=High
cap_multi = "Cap_Multidomain"  # 0=Low, 1=Med, 2=High
cap_io = "Cap_IO"              # 0=Low, 1=Med, 2=High

# Motives (binary, conditioned on sponsor)
m_punish = "Motive_Punish_West_Turn"        # NR
m_undermine = "Motive_Undermine_West"       # Russia
m_domestic = "Motive_Domestic_Radicalism"   # FPD
m_casus = "Motive_CasusBelli"               # US (low but nonzero)

# Access / opportunity (conditioned on sponsor) not actions but preconditions
a_vendor = "Access_Vendor"           # 0=F, 1=T could somebody plausibly access the grid through the vendor path.. it depends on the sponsor because each of these has different probabilities.
a_patient = "Access_Patient_Weeks"   # 0=F, 1=T could they have persistent access for weeks before activation. Operational Patience.
a_drone = "Access_Drone_Logistics"   # 0=F, 1=T did the sponsor have the logistical capability to deploy the drones near the airport.

# Aggregators (keep CPT sizes small)
intent = "Intent"        # 0=Low, 1=Med, 2=High how motivated the sponsor is
means = "Means"          # 0=Low, 1=Med, 2=High how technically capable they are
opportunity = "Opportunity"  # 0=Low, 1=Med, 2=High did they reaListically have structural access.




"""NOW WE LOOK AT THE ACTUAL INCIDENT"""
# Planning/execution
planned = "Operation_Planned"     # 0=F, 1=T it depends on intent, means and opportunity
cyber = "Cyber_Op_Executed"       # 0=F, 1=T depends on operation_planned
drone = "Drone_Op_Executed"       # 0=F, 1=T depends on operation_planned
coord = "Coordination_Achieved"   # 0=F, 1=T depends on operation_action

# Reliability ; these influence the evidence node probabilities and the attribution certainty.
rel_for = "Reliability_Forensics"  # 0=Low, 1=Med, 2=High. represents how trustworthy the data is (more factual)
rel_int = "Reliability_Intel"      # 0=Low, 1=Med, 2=High. reporting, of the actual intelligence

# Evidence (observables)
e_vendor = "E_Vendor_Path"              # 0=F, 1=T
e_patient = "E_Patient_Access_Weeks"    # 0=F, 1=T
e_logic = "E_Logic_Altered"             # 0=F, 1=T
e_drone_coord = "E_Drones_Coordinated"  # 0=F, 1=T
e_drone_low = "E_Drone_OffTheShelf"     # 0=F, 1=T
e_serial = "E_Drone_Serial_Filed"       # 0=F, 1=T
e_tight = "E_Tight_Coordination"        # 0=F, 1=T
e_fog = "E_AttributionFog_Narratives"   # 0=F, 1=T
e_fastmsg = "E_NewRepublic_Fast_Messaging"  # 0=F, 1=T (kept, but weakened)

# Attribution + consequences
attr = "Attribution_Certainty"     # 0=Low, 1=Med, 2=High. how confident investigators are in identifying the sponsor.
sanctions = "O_Sanctions"          # 0=None, 1=Limited, 2=Expanded. depends on sponsor and attribution certainty and sanctions are more severe if attribution certainty it high.
mil = "O_Military_Presence"        # 0=Low, 1=Med, 2=High
escal = "O_Escalation_Risk"        # 0=Low, 1=Med, 2=High

nodes = [
    H, proxy, falseflag,
    cap_ics, cap_multi, cap_io,
    m_punish, m_undermine, m_domestic, m_casus,
    a_vendor, a_patient, a_drone,
    intent, means, opportunity,
    planned, cyber, drone, coord,
    rel_for, rel_int,
    e_vendor, e_patient, e_logic, e_drone_coord, e_drone_low, e_serial, e_tight, e_fog, e_fastmsg,
    attr, sanctions, mil, escal
]
model.add_nodes_from(nodes)

# -----------------------------------------------------------------------------
# Edges
# -----------------------------------------------------------------------------
edges = [
    (H, cap_ics), (H, cap_multi), (H, cap_io),
    (H, m_punish), (H, m_undermine), (H, m_domestic), (H, m_casus),
    (H, a_vendor), (H, a_patient), (H, a_drone),
    (H, proxy), (H, falseflag),

    # aggregators
    (m_punish, intent), (m_undermine, intent), (m_domestic, intent), (m_casus, intent),
    (cap_ics, means), (cap_multi, means),
    (a_vendor, opportunity), (a_patient, opportunity), (a_drone, opportunity),

    # planning and execution
    (intent, planned), (means, planned), (opportunity, planned),
    (planned, cyber), (planned, drone),
    (cyber, coord), (drone, coord),

    # evidence (now discriminative)
    (cyber, e_vendor), (a_vendor, e_vendor), (rel_for, e_vendor),
    (cyber, e_patient), (a_patient, e_patient), (rel_for, e_patient),
    (cyber, e_logic), (cap_ics, e_logic), (rel_for, e_logic),

    (drone, e_drone_coord), (coord, e_drone_coord), (rel_for, e_drone_coord),
    (drone, e_drone_low), (rel_for, e_drone_low),
    (drone, e_serial), (rel_for, e_serial),

    (coord, e_tight), (rel_for, e_tight),

    # fog / narratives
    (cap_io, e_fog), (falseflag, e_fog), (proxy, e_fog), (rel_int, e_fog),

    # fast messaging: allow it even if not sponsor (because people message fast when attacked)
    (planned, e_fastmsg), (cap_io, e_fastmsg), (rel_int, e_fastmsg),

    # attribution certainty depends on evidence strength + deception + reliability
    (e_vendor, attr), (e_logic, attr), (e_tight, attr), (e_fog, attr),
    (falseflag, attr), (proxy, attr), (rel_for, attr), (rel_int, attr),

    # consequences depend on sponsor + attribution certainty
    (H, sanctions), (attr, sanctions),
    (H, mil), (attr, mil),
    (sanctions, escal), (mil, escal),
]
model.add_edges_from(edges)

# -----------------------------------------------------------------------------
# CONDITIONAL PROBABILITY DISTRIBUTIONS
# -----------------------------------------------------------------------------
# Sponsor prior (invented so definitely not the most accurate network)
cpd_H = TabularCPD(
    variable=H, variable_card=5,
    values=[[0.22], [0.22], [0.18], [0.08], [0.30]] # other here has the highest probbility to reflect uncertainty
)

# Proxy / falseflag (simple sponsor-conditioned tendencies)
cpd_proxy = TabularCPD(
    variable=proxy, variable_card=2,
    values=[
        [0.35, 0.40, 0.50, 0.25, 0.55],  # Proxy=F/0 conditioned for each sponsor
        [0.65, 0.60, 0.50, 0.75, 0.45],  # Proxy=T/1 (proxy=true|russia)=65%. Makes sense that Russia needs someone on the island to perform. Russia Needs them for deniability. FPD used by NR? 
    ],
    evidence=[H], evidence_card=[5]
)

cpd_falseflag = TabularCPD(
    variable=falseflag, variable_card=2,
    values=[
        [0.70, 0.75, 0.80, 0.55, 0.85],  # FF=F
        [0.30, 0.25, 0.20, 0.45, 0.15],  # FF=T US highest chances.
    ],
    evidence=[H], evidence_card=[5]
)

# Capabilities: P(level | sponsor)
# columns: Russia, NR, FPD, US, Other
cpd_cap_ics = TabularCPD(
    variable=cap_ics, variable_card=3,
    values=[
        [0.10, 0.20, 0.55, 0.05, 0.45],  # Low here highest FPD
        [0.35, 0.45, 0.35, 0.20, 0.40],  # Med here highest NR
        [0.55, 0.35, 0.10, 0.75, 0.15],  # High russia and us, more or less should be the same?
    ],
    evidence=[H], evidence_card=[5]
)

cpd_cap_multi = TabularCPD(
    variable=cap_multi, variable_card=3,
    values=[
        [0.15, 0.25, 0.60, 0.10, 0.50],  # Low
        [0.35, 0.45, 0.30, 0.25, 0.35],  # Med
        [0.50, 0.30, 0.10, 0.65, 0.15],  # High
    ],
    evidence=[H], evidence_card=[5]
)

cpd_cap_io = TabularCPD(
    variable=cap_io, variable_card=3,
    values=[
        [0.10, 0.25, 0.45, 0.15, 0.55],  # Low
        [0.30, 0.45, 0.40, 0.30, 0.30],  # Med
        [0.60, 0.30, 0.15, 0.55, 0.15],  # High
    ],
    evidence=[H], evidence_card=[5]
)

# Motives (binary, conditioned by sponsor)
def cpd_binary(name, p_true_by_sponsor):
    # p_true_by_sponsor list length 5
    p_false = [1 - p for p in p_true_by_sponsor]
    return TabularCPD(
        variable=name, variable_card=2,
        values=[p_false, p_true_by_sponsor],
        evidence=[H], evidence_card=[5]
    )

cpd_m_punish = cpd_binary(m_punish,   [0.35, 0.75, 0.30, 0.10, 0.20])
cpd_m_undermine = cpd_binary(m_undermine, [0.70, 0.35, 0.20, 0.10, 0.15])
cpd_m_domestic = cpd_binary(m_domestic, [0.05, 0.10, 0.45, 0.05, 0.15])
cpd_m_casus = cpd_binary(m_casus,     [0.10, 0.08, 0.05, 0.25, 0.05])

# Access nodes 
cpd_a_vendor = cpd_binary(a_vendor,  [0.55, 0.45, 0.25, 0.50, 0.35])
cpd_a_patient = cpd_binary(a_patient,[0.60, 0.55, 0.35, 0.60, 0.40])
cpd_a_drone = cpd_binary(a_drone,    [0.45, 0.55, 0.35, 0.35, 0.30])

# Reliability
cpd_rel_for = TabularCPD(variable=rel_for, variable_card=3, values=[[0.30],[0.45],[0.25]])
cpd_rel_int = TabularCPD(variable=rel_int, variable_card=3, values=[[0.35],[0.45],[0.20]])

# Intent aggregator (rank-ish, from 4 motive binaries)
# States: 0=Low,1=Med,2=High
# CPT size: 3 x 2^4 = 48 entries: manageable
# Rule: more motives true:  higher intent
def intent_probs(m_true_count):
    if m_true_count == 0:
        return [0.80, 0.18, 0.02]
    if m_true_count == 1:
        return [0.45, 0.45, 0.10]
    if m_true_count == 2:
        return [0.20, 0.55, 0.25]
    if m_true_count == 3:
        return [0.10, 0.40, 0.50]
    return [0.05, 0.25, 0.70]  # 4

intent_vals = [[], [], []]
for mp in [0,1]:
    for mu in [0,1]:
        for md in [0,1]:
            for mc in [0,1]:
                cnt = mp + mu + md + mc
                pL,pM,pH = intent_probs(cnt)
                intent_vals[0].append(pL)
                intent_vals[1].append(pM)
                intent_vals[2].append(pH)

cpd_intent = TabularCPD(
    variable=intent, variable_card=3,
    values=intent_vals,
    evidence=[m_punish, m_undermine, m_domestic, m_casus],
    evidence_card=[2,2,2,2]
)

# Means aggregator from cap_ics and cap_multi (3x3 parents => 9 columns)
# Heuristic: take the max
means_vals = [[], [], []]
for c1 in [0,1,2]:
    for c2 in [0,1,2]:
        m = max(c1, c2)
        # soften it a bit
        if m == 0:
            probs = [0.80, 0.18, 0.02]
        elif m == 1:
            probs = [0.25, 0.60, 0.15]
        else:
            probs = [0.10, 0.35, 0.55]
        means_vals[0].append(probs[0])
        means_vals[1].append(probs[1])
        means_vals[2].append(probs[2])

cpd_means = TabularCPD(
    variable=means, variable_card=3,
    values=means_vals,
    evidence=[cap_ics, cap_multi],
    evidence_card=[3,3]
)

# Opportunity aggregator from 3 access binaries (2^3=8 columns)
opp_vals = [[], [], []]
for av in [0,1]:
    for ap in [0,1]:
        for ad in [0,1]:
            cnt = av + ap + ad
            if cnt == 0:
                probs = [0.85, 0.14, 0.01]
            elif cnt == 1:
                probs = [0.45, 0.45, 0.10]
            elif cnt == 2:
                probs = [0.20, 0.55, 0.25]
            else:
                probs = [0.10, 0.35, 0.55]
            opp_vals[0].append(probs[0])
            opp_vals[1].append(probs[1])
            opp_vals[2].append(probs[2])

cpd_opportunity = TabularCPD(
    variable=opportunity, variable_card=3,
    values=opp_vals,
    evidence=[a_vendor, a_patient, a_drone],
    evidence_card=[2,2,2]
)

# Planning: Operation_Planned | Intent, Means, Opportunity
# binary with strong dependence
plan_false = []
plan_true = []
for i in [0,1,2]:
    for m in [0,1,2]:
        for o in [0,1,2]:
            score = i + m + o  # 0..6
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

cpd_planned = TabularCPD(
    variable=planned, variable_card=2,
    values=[plan_false, plan_true],
    evidence=[intent, means, opportunity],
    evidence_card=[3,3,3]
)

# Execution: | planned
cpd_cyber = TabularCPD(
    variable=cyber, variable_card=2,
    values=[[0.97, 0.15],
            [0.03, 0.85]],
    evidence=[planned], evidence_card=[2]
)
cpd_drone = TabularCPD(
    variable=drone, variable_card=2,
    values=[[0.97, 0.25],
            [0.03, 0.75]],
    evidence=[planned], evidence_card=[2]
)

# Coordination: depends on both executed
cpd_coord = TabularCPD(
    variable=coord, variable_card=2,
    values=[
        [0.99, 0.55, 0.55, 0.15],  # coord=F
        [0.01, 0.45, 0.45, 0.85],  # coord=T
    ],
    evidence=[cyber, drone], evidence_card=[2,2]
)

# Helper to create reliability-aware evidence: P(E=True) by (core_true?, reliability)
def cpd_evidence(name, parents, card_parents, p_true_table):
    """
    p_true_table must be a list of length = product(card_parents)
    that gives P(E=True) for each parent configuration (pgmpy order).
    """
    p_false = [1 - p for p in p_true_table]
    return TabularCPD(name, 2, values=[p_false, p_true_table], evidence=parents, evidence_card=card_parents)

# Evidence: Vendor path depends on cyber execution, vendor access, rel_for
p_vendor_true = []
for cy in [0,1]:
    for av in [0,1]:
        for rf in [0,1,2]:
            if cy == 0:
                base = 0.05
            else:
                base = 0.35 if av == 0 else 0.80
            # reliability modifier
            mod = {0: -0.15, 1: 0.0, 2: 0.10}[rf]
            p = min(max(base + mod, 0.01), 0.99)
            p_vendor_true.append(p)

cpd_e_vendor = cpd_evidence(e_vendor, [cyber, a_vendor, rel_for], [2,2,3], p_vendor_true)

# Patient weeks depends on cyber, patient access, rel_for
p_patient_true = []
for cy in [0,1]:
    for ap in [0,1]:
        for rf in [0,1,2]:
            if cy == 0:
                base = 0.05
            else:
                base = 0.30 if ap == 0 else 0.75
            mod = {0: -0.15, 1: 0.0, 2: 0.10}[rf]
            p = min(max(base + mod, 0.01), 0.99)
            p_patient_true.append(p)

cpd_e_patient = cpd_evidence(e_patient, [cyber, a_patient, rel_for], [2,2,3], p_patient_true)

# Logic altered depends on cyber, cap_ics, rel_for
p_logic_true = []
for cy in [0,1]:
    for ci in [0,1,2]:
        for rf in [0,1,2]:
            if cy == 0:
                base = 0.04
            else:
                base = [0.35, 0.65, 0.85][ci]
            mod = {0: -0.12, 1: 0.0, 2: 0.08}[rf]
            p = min(max(base + mod, 0.01), 0.99)
            p_logic_true.append(p)

cpd_e_logic = cpd_evidence(e_logic, [cyber, cap_ics, rel_for], [2,3,3], p_logic_true)

# Drone corridor coordination depends on drone op, coordination, rel_for
p_drone_coord_true = []
for dr in [0,1]:
    for co in [0,1]:
        for rf in [0,1,2]:
            if dr == 0:
                base = 0.05
            else:
                base = 0.35 if co == 0 else 0.80
            mod = {0: -0.12, 1: 0.0, 2: 0.08}[rf]
            p = min(max(base + mod, 0.01), 0.99)
            p_drone_coord_true.append(p)

cpd_e_drone_coord = cpd_evidence(e_drone_coord, [drone, coord, rel_for], [2,2,3], p_drone_coord_true)

# Drone off-the-shelf depends on drone op, rel_for (not very discriminative)
p_low_true = []
for dr in [0,1]:
    for rf in [0,1,2]:
        base = 0.20 if dr == 0 else 0.70
        mod = {0: -0.08, 1: 0.0, 2: 0.05}[rf]
        p = min(max(base + mod, 0.01), 0.99)
        p_low_true.append(p)

cpd_e_drone_low = cpd_evidence(e_drone_low, [drone, rel_for], [2,3], p_low_true)

# Serial filed depends on drone op, rel_for
p_serial_true = []
for dr in [0,1]:
    for rf in [0,1,2]:
        base = 0.15 if dr == 0 else 0.80
        mod = {0: -0.10, 1: 0.0, 2: 0.07}[rf]
        p = min(max(base + mod, 0.01), 0.99)
        p_serial_true.append(p)

cpd_e_serial = cpd_evidence(e_serial, [drone, rel_for], [2,3], p_serial_true)

# Tight coordination depends on coord, rel_for
p_tight_true = []
for co in [0,1]:
    for rf in [0,1,2]:
        base = 0.08 if co == 0 else 0.85
        mod = {0: -0.15, 1: 0.0, 2: 0.08}[rf]
        p = min(max(base + mod, 0.01), 0.99)
        p_tight_true.append(p)

cpd_e_tight = cpd_evidence(e_tight, [coord, rel_for], [2,3], p_tight_true)

# Attribution fog narratives depends on IO + deception + intel reliability
p_fog_true = []
for cio in [0,1,2]:
    for ff in [0,1]:
        for pr in [0,1]:
            for ri in [0,1,2]:
                base = [0.25, 0.45, 0.65][cio]
                if ff == 1: base += 0.10
                if pr == 1: base += 0.10
                mod = {0: -0.10, 1: 0.0, 2: 0.05}[ri]
                p = min(max(base + mod, 0.01), 0.99)
                p_fog_true.append(p)

cpd_e_fog = cpd_evidence(e_fog, [cap_io, falseflag, proxy, rel_int], [3,2,2,3], p_fog_true)

# Fast messaging depends on planned + IO capability + intel reliability (weakly diagnostic)
# Note: does NOT directly depend on sponsor anymore.
p_fast_true = []
for pl in [0,1]:
    for cio in [0,1,2]:
        for ri in [0,1,2]:
            base = 0.30  # people message fast even when innocent
            if pl == 1: base += 0.15
            base += {0: 0.00, 1: 0.05, 2: 0.10}[cio]
            base += {0: -0.08, 1: 0.0, 2: 0.05}[ri]
            p = min(max(base, 0.01), 0.99)
            p_fast_true.append(p)

cpd_e_fast = cpd_evidence(e_fastmsg, [planned, cap_io, rel_int], [2,3,3], p_fast_true)

# Attribution certainty: depends on key evidence + deception + reliability
# CPT size: 3 x (2^4 *2*2*3*3)= big if we do it raw, so simplify:
# Make attr depend on 4 binary evidences + deception only, and keep reliabilities as soft priors
# BUT since edges already include reliabilities -> attr, we keep a manageable CPT by:
# - ignoring rels in CPT and letting them influence via upstream evidence.
# keep rels as parents but collapse their effect lightly with coarse mapping.

# build CPT over
# parents: e_vendor,e_logic,e_tight,e_fog,falseflag,proxy,rel_for,rel_int
# columns: 2^4 *2*2*3*3 = 16*4*9 = 576 -> manageable programmatically.
attr_vals = [[], [], []]
for ev in [0,1]:
    for el in [0,1]:
        for et in [0,1]:
            for ef in [0,1]:
                strength = ev + el + et  # 0..3 (fog not strength; it reduces)
                for ff in [0,1]:
                    for pr in [0,1]:
                        for rf in [0,1,2]:
                            for ri in [0,1,2]:
                                # baseline from technical strength
                                if strength == 0:
                                    pH = 0.05
                                elif strength == 1:
                                    pH = 0.15
                                elif strength == 2:
                                    pH = 0.35
                                else:
                                    pH = 0.60

                                # fog and deception reduce certainty
                                if ef == 1:
                                    pH -= 0.15
                                if ff == 1:
                                    pH -= 0.10
                                if pr == 1:
                                    pH -= 0.10

                                # higher reliabilities increase certainty a bit
                                pH += {0: -0.05, 1: 0.0, 2: 0.05}[rf]
                                pH += {0: -0.04, 1: 0.0, 2: 0.04}[ri]

                                pH = float(min(max(pH, 0.01), 0.90))
                                # split remainder between Low/Med with mild bias to Med when some strength exists
                                rem = 1 - pH
                                if strength >= 2:
                                    pM = rem * 0.65
                                    pL = rem * 0.35
                                else:
                                    pM = rem * 0.45
                                    pL = rem * 0.55

                                attr_vals[0].append(pL)
                                attr_vals[1].append(pM)
                                attr_vals[2].append(pH)

cpd_attr = TabularCPD(
    variable=attr, variable_card=3,
    values=attr_vals,
    evidence=[e_vendor, e_logic, e_tight, e_fog, falseflag, proxy, rel_for, rel_int],
    evidence_card=[2,2,2,2,2,2,3,3]
)

# Consequences: depend on sponsor + certainty
# Sanctions
san_vals = [[], [], []]
for h in range(5):
    for c in [0,1,2]:
        # base by certainty
        if c == 0:
            none, lim, exp = 0.60, 0.35, 0.05
        elif c == 1:
            none, lim, exp = 0.35, 0.50, 0.15
        else:
            none, lim, exp = 0.20, 0.50, 0.30

        # sponsor adjustment (example)
        if h == 0:      # Russia: more likely expanded when high certainty
            exp += 0.10 if c == 2 else 0.05 if c == 1 else 0.00
            none -= 0.05
        elif h == 1:    # NR: moderate
            exp += 0.05 if c == 2 else 0.02 if c == 1 else 0.00
            none -= 0.03
        elif h == 3:    # US: sanctions less likely
            exp -= 0.10
            none += 0.08
        # normalize
        vec = np.array([max(none,0.01), max(lim,0.01), max(exp,0.01)], dtype=float)
        vec = (vec / vec.sum()).tolist()
        san_vals[0].append(vec[0]); san_vals[1].append(vec[1]); san_vals[2].append(vec[2])

cpd_san = TabularCPD(
    variable=sanctions, variable_card=3,
    values=san_vals,
    evidence=[H, attr], evidence_card=[5,3]
)

# Military presence increase
mil_vals = [[], [], []]
for h in range(5):
    for c in [0,1,2]:
        if c == 0:
            low, med, high = 0.65, 0.30, 0.05
        elif c == 1:
            low, med, high = 0.40, 0.45, 0.15
        else:
            low, med, high = 0.25, 0.50, 0.25

        if h == 0 and c >= 1:  # Russia -> more likely high presence
            high += 0.05
            low -= 0.03
        if h == 3:  # US sponsor -> less "presence increase" against itself
            high -= 0.08
            low += 0.06

        vec = np.array([max(low,0.01), max(med,0.01), max(high,0.01)], dtype=float)
        vec = (vec / vec.sum()).tolist()
        mil_vals[0].append(vec[0]); mil_vals[1].append(vec[1]); mil_vals[2].append(vec[2])

cpd_mil = TabularCPD(
    variable=mil, variable_card=3,
    values=mil_vals,
    evidence=[H, attr], evidence_card=[5,3]
)

# Escalation risk from sanctions + military (3x3 = 9 cols)
esc_vals = [[], [], []]
for s in [0,1,2]:
    for m in [0,1,2]:
        score = s + m  # 0..4
        if score <= 1:
            p = [0.75, 0.22, 0.03]
        elif score == 2:
            p = [0.45, 0.45, 0.10]
        elif score == 3:
            p = [0.25, 0.50, 0.25]
        else:
            p = [0.15, 0.45, 0.40]
        esc_vals[0].append(p[0]); esc_vals[1].append(p[1]); esc_vals[2].append(p[2])

cpd_escal = TabularCPD(
    variable=escal, variable_card=3,
    values=esc_vals,
    evidence=[sanctions, mil], evidence_card=[3,3]
)

# Add all CPDs
model.add_cpds(
    cpd_H, cpd_proxy, cpd_falseflag,
    cpd_cap_ics, cpd_cap_multi, cpd_cap_io,
    cpd_m_punish, cpd_m_undermine, cpd_m_domestic, cpd_m_casus,
    cpd_a_vendor, cpd_a_patient, cpd_a_drone,
    cpd_rel_for, cpd_rel_int,
    cpd_intent, cpd_means, cpd_opportunity,
    cpd_planned, cpd_cyber, cpd_drone, cpd_coord,
    cpd_e_vendor, cpd_e_patient, cpd_e_logic, cpd_e_drone_coord, cpd_e_drone_low, cpd_e_serial, cpd_e_tight,
    cpd_e_fog, cpd_e_fast,
    cpd_attr, cpd_san, cpd_mil, cpd_escal
)

print("Checking model validity...")
print("Model valid:", model.check_model())

# -----------------------------------------------------------------------------
# Example inference with Freelandia case evidence
# -----------------------------------------------------------------------------
inference = VariableElimination(model)

# Evidence: same spirit, but WITHOUT the unrelated FPD-URF items
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
    rel_for: 2,  # high forensics
    rel_int: 1   # medium intel
}

print("\nP(H_sponsor | evidence):")
res = inference.query([H], evidence=evidence)
print(res)

names = ["Russia", "NewRepublic", "FPD", "US", "Other"]
print("\nPosterior sponsor probabilities:")
for i, n in enumerate(names):
    print(f"  {n:12s}: {res.values[i]:.4f} ({res.values[i]*100:.2f}%)")

print("\nP(Proxy_Used | evidence):")
print(inference.query([proxy], evidence=evidence))

print("\nP(FalseFlag_Planted | evidence):")
print(inference.query([falseflag], evidence=evidence))

print("\nP(Attribution_Certainty | evidence):")
res_attr = inference.query([attr], evidence=evidence)
print(res_attr)

print("\nP(O_Sanctions | evidence):")
print(inference.query([sanctions], evidence=evidence))

print("\nP(O_Escalation_Risk | evidence):")
print(inference.query([escal], evidence=evidence))
