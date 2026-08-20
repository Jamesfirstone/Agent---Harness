# Figure generation log

Date: 2026-08-20

## AI-generated conceptual figure

- Tool path: built-in image generation, selected after the native scientific-schematics backend reported `OPENROUTER_API_KEY=missing`.
- Accepted asset: `figures/supplement/instruction_compliance_complete_mediation.png`.
- Use case: `scientific-educational`.
- Core prompt: a landscape, publication-style architecture diagram with the exact lifecycle labels `Policy Source → Intent → Plan → Tool Call → Execution → Result` and enforcement labels `Spec & Parse → Capability / IFC → Pre-execution Gate → Sandbox → Postcondition → Audit & Recovery`; include `BLOCK` and `APPROVE` branches; no invented metrics.
- Validation: labels and lifecycle order were visually inspected. The figure is conceptual; it is not evidence for any empirical count.

## Deterministic screening figure

- Asset: `figures/supplement/prisma_screening_flow.svg`.
- Method: generated directly from `sources/supplement/screening_flow.json`; no generative model was used for counts or labels.
- Reason: a first AI-rendered draft collapsed the distinction between 35 supplementary candidates and the final 29 additions/rescues. It was rejected from the repository to avoid an ambiguous denominator.
