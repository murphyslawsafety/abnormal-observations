# RCX-PB-GC-0002H — Final Outcome v1.0

Status: FAIL
Classification: legitimate negative historical holdout result
Parent model: RCX-PB-GC-0002 fitted model v1.0
Parent model SHA-256: 7831729fc8ba4fc385e8956961572f1e5ca8fc289c57ded77ef49fe49b441b87

The frozen RCX-PB-GC-0002 model was evaluated once against 273 previously untouched RCX-PB-GC-0001 sealed outcomes.

Results:
- white LLR total: -1.0609633278593975 nats
- Powerball LLR total: -0.04148639364255091 nats
- combined LLR total: -1.1024497215019484 nats
- e-value: 0.33205664023409914
- log10(e): -0.47878783062407293
- positive individual dates: 155 / 273
- positive 30-target blocks: 2 / 9
- maximum positive single-date contribution: 0.11365808855036974 nats
- maximum negative single-date contribution: -0.1247788044035052 nats
- maximum single-date share of all positive LLR: 0.03196458045438138

Frozen decision rule: FAIL if total LLR < 0.

Conclusion:
The fitted RCX-PB-GC-0002 relational compiler did not outperform the fair conditional baseline on this untouched historical holdout. The result closes this fitted model as a historical holdout predictor. It does not establish that every possible physical dependence, latent representation, quotient structure, or transformation grammar is absent.

Audit:
- sealed truth SHA-256: 75944ced5af872586d65643c8aeb725f91d612b7bc939ba0baad0febe923cbcf
- preregistration Git blob: 9f796cd41dd88522ae3b75b8ad489b1b15ff95f9
- evaluator Git blob: 7b01bc6c1b56bc863ae8f3a809bf631af5c8c263
- frozen live scorer Git blob: cf920a30d8aa809b9794ad252ec45443945f3926
- workflow run: 37131198645
- artifact: 11276692495
- artifact digest: sha256:af57b52602db49e8bb880eed6705aff980885608211e723f9b49ad5ba0c74594

EUREKA: none. Cross-project EUREKA tally remains 3.
