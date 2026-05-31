# Nomenclature Guards

These constraints are enforced by `tests/unit/test_nomenclature.py`.

1. `RMC-6236`, `RMC-6291`, and `RMC-9805` are Revolution Medicines RAS(ON)
   inhibitors, not mTOR bi-sterics. Only `RMC-5552` (clinical), `RMC-6272`, and
   `RMC-4627` (tool compounds) are bi-steric mTOR agents.
2. MTOR S2448 phosphorylation is attributed to RPS6KB1 feedback, not AKT1, and
   has no defined function. The graph must not encode `AKT1 -> MTOR S2448`.
3. The canonical AKT site on TSC2 is T1462. There is no `S1462` site.
4. MTOR S2481 is an autophosphorylation site, rapamycin-insensitive and
   predominant in MTORC2. It is not an external-kinase target.
5. Sapanisertib, MLN0128, INK128, and TAK-228 are the same molecule and must be
   represented by one alias-unified node.
