# MBD Review Principles

This project uses lightweight Mermaid-like MBD markup, but review expectations
should still resemble professional Model-Based Design practice. These principles
are adapted for a commercial-tool-free MVP and do not claim Simulink, ISO 26262,
ASPICE, DO-178C, or tool-qualification compliance.

## Review Order

Review generated MBD artifacts in this order:

1. Requirement and specification intent.
2. Spec-to-MBD compliance table.
3. Interface and data-flow boundaries.
4. State transitions, guard conditions, and actions.
5. Harness/scenario evidence.
6. Generated handoff artifacts and preview C boundary.
7. Known assumptions, unsupported semantics, and external verification needs.

## Checklist

- Requirements traceability: each claimed requirement shall link to concrete
  MBD elements, tests/scenarios, generated artifacts, or report checks. Broad
  component-level trace is not enough.
- Interface and data-flow review: inputs, outputs, virtual IC boundaries, HAL
  boundaries, and report observations shall be visible and directionally clear.
- State/control behavior: states, guard conditions, actions, latches, recovery
  rules, and unsupported timing assumptions shall be reviewable in one place.
- Requirements-based scenario evidence: each scenario shall show model inputs,
  scenario steps, observed behavior, expected behavior, and pass/fail.
- Modeling standards and readability: keep names stable, diagrams readable,
  model elements small, and generated views simpler than the behavior under
  review.
- Generated artifact boundary: Simulink `.m`, Modelica `.mo`, SCXML, Mermaid,
  PlantUML, FMI metadata, and preview C are generated outputs. Review source
  markup and regenerate artifacts instead of editing generated files.

## Source-Informed Rationale

- MathWorks MAB/JMAAB guidance emphasizes common understanding for modelers and
  reviewers, with readability, simulation/verification, and code generation as
  key objectives.
- MathWorks Model Advisor/Simulink Check positions model checks as a way to
  enforce modeling guidelines and detect inefficient or inaccurate modeling
  conditions.
- MathWorks Requirements Toolbox describes traceability as connecting
  requirements, models, tests, and code, including gap and impact analysis.
- Requirements-based verification guidance emphasizes turning informal
  requirements into unambiguous assessments and tracing requirements to design
  and tests.
- NASA review terminology for preliminary design reviews expects evidence that
  the design meets requirements, interfaces are identified, and verification
  methods are described.

## References

- MathWorks, Model Advisor checks for MAB modeling guidelines:
  https://www.mathworks.com/help/slcheck/ref/model-advisor-checks-for-mab-modeling-guidelines.html
- MathWorks, Modeling guidelines and Model Advisor checks for industry
  standards:
  https://www.mathworks.com/help/ecoder/ug/guidelines-checks-industry-stds-ecoder.html
- MathWorks, Requirements Toolbox:
  https://www.mathworks.com/products/requirements-toolbox.html
- MathWorks, Requirements-based verification with Simulink Test:
  https://www.mathworks.com/videos/requirements-based-verification-with-simulink-test-1554822878413.html
- NASA Systems Engineering Handbook appendix:
  https://www.nasa.gov/reference/system-engineering-handbook-appendix/
