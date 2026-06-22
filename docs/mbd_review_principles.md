# MBD Review Principles

This project uses lightweight Mermaid-like MBD markup, but review expectations
should still resemble professional Model-Based Design practice. These principles
are adapted for a commercial-tool-free MVP and do not claim Simulink, ISO 26262,
ASPICE, DO-178C, or tool-qualification compliance.

`demo.html` is an MBD review artifact compatibility filename, not a casual
visual demo.

## Review Order

Review generated MBD artifacts in this order:

1. Requirement and specification intent.
2. System context and functional decomposition.
3. Requirement allocation to functions, components, and scenarios.
4. Spec-to-MBD compliance table.
5. Interface and data-flow boundaries.
6. State transitions, guard conditions, and actions.
7. Harness/scenario evidence.
8. Generated handoff artifacts and preview C boundary.
9. Known assumptions, unsupported semantics, and external verification needs.

## Design Layer Separation

Do not treat every Mermaid diagram in a specification as executable control
semantics. For reviewable MBD handoff work, keep these layers distinct:

- Component View: components, responsibilities, owned signals, and boundaries.
- Data Flow View: ports, parameters, constants, signals, direction, and report
  observation paths.
- Sequence View: scenario order, stimulus, expected observations, and Harness
  preview expectations.
- Control Semantics View: states, transitions, guards, priorities, and actions
  that may become `mbd-state` or `mbd-control`.

Component, data-flow, and sequence diagrams are design review inputs. Only an
explicit Control Semantics View, or the legacy Design Overview subset used by
older samples, should drive executable state/control generation. Sequence
diagrams may feed scenario expectations and reports, but shall not add control
behavior missing from the MBD source.

## Generated-Side Consistency Checks

This repository does not verify production MBD semantics. Existing MBD tools
remain the intended verification backends. The repository shall still verify
that generated handoff packages are internally consistent before they are
reviewed or handed off:

- The parsed IR, generated review artifacts, handoff artifacts, Harness preview
  reports, and preview C scaffold shall trace back to requirements and
  specification views.
- Exporter output shall be deterministic and regenerated from `.mbd.md` source.
- Harness preview shall compare observed behavior with expected behavior that
  comes from requirements, specification, and MBD control semantics.
- Preview C shall remain HAL-boundary, preview-only scaffold and may be
  syntax-checked or smoke-tested when a local toolchain is available.
- Scenario YAML, Python preview code, virtual IC fixtures, or generated preview
  C shall not compensate for missing MBD semantics.

## Checklist

- Requirements traceability: each claimed requirement shall link to concrete
  MBD elements, tests/scenarios, generated artifacts, or report checks. Broad
  component-level trace is not enough.
- Functional decomposition: the specification and MBD source shall identify the
  system context, functional components, responsibility allocation, owned
  signals, and interfaces before detailed control rules. Reject flat
  controller-only models when the expected review target is a system or
  architecture-level MBD artifact.
- Allocation clarity: each high-risk behavior shall say which function owns
  detection, state management, command calculation, output mapping, diagnostic
  reporting, and scenario evidence. Reject duplicated or orphaned behavior.
- Interface and data-flow review: inputs, outputs, virtual IC boundaries, HAL
  boundaries, and report observations shall be visible and directionally clear.
- State/control behavior: states, guard conditions, actions, latches, recovery
  rules, and unsupported timing assumptions shall be reviewable in one place.
- Requirements-based scenario evidence: each scenario shall show model inputs,
  scenario steps, observed behavior, expected behavior, and pass/fail.
- Harness evidence boundary: Harness is a preview evidence layer. It may show
  scenario stimulus, virtual IC boundaries, HAL boundaries, observed behavior,
  and report evidence, but it shall not own control decisions, state
  transitions, output decisions, thresholds, recovery rules, or product
  behavior. Scenario YAML must not add control behavior missing from the MBD
  source.
- Modeling standards and readability: keep names stable, diagrams readable,
  model elements small, and generated views simpler than the behavior under
  review.
- Generated artifact boundary: Simulink `.m`, Modelica `.mo`, SCXML, Mermaid,
  PlantUML, FMI metadata, and preview C are generated outputs. Review source
  markup and regenerate artifacts instead of editing generated files.

## Harness Evidence Lane

The Harness evidence lane is a hard review gate for preview work.

Review Harness evidence as supporting evidence, not as a verification backend.
Accept Harness content only when it helps a reviewer connect model inputs,
scenario steps, virtual IC or HAL boundary crossings, observed behavior,
expected behavior, and pass/fail result back to concrete MBD elements and
requirements.

Reject Harness shortcuts when scenario YAML, Python preview code, virtual IC
fixtures, or generated preview C compensate for missing MBD semantics. The
review artifact should separate what Harness preview observed from what
external MBD/product-test infrastructure must still verify.

## Self-Review Reject Examples

Reject a generated review artifact before showing it as ready when:

- It asks whether the generated MBD matches `Spec.md`, but does not place the
  spec intent, spec diagram, generated MBD diagram, and generated transition
  table close enough for direct comparison.
- It introduces concepts absent from the spec, such as generic sensors,
  actuators, plants, or harness nodes, without explicitly marking them as open
  assumptions.
- It treats a state-machine diagram as sufficient evidence and fails to expose
  the initial/default state, transition table, guard/effect/action semantics,
  and scenario evidence.
- It buries unresolved semantics such as implicit self-hold, else behavior,
  timing, or unsupported entry/exit actions instead of listing them as review
  questions.
- It reads like a generated dump rather than a curated answer to the user's
  review question.
- A reviewer cannot make an initial accept/reject judgment in 30 seconds to
  1 minute. The first viewport and immediately following review block shall show
  the review verdict, spec intent, generated behavior, mismatch status, and open
  questions without forcing long reading or repeated scrolling.
- Dense trace lists, generated element paths, and tool-handoff explanations
  appear before the concise human review summary.
- Harness PASS is presented as formal MBD verification, or Harness/scenario YAML
  contains control decisions that are not present in the spec, `mbd-control`, or
  functional decomposition.

## Source-Informed Rationale

- MathWorks MAB/JMAAB guidance emphasizes common understanding for modelers and
  reviewers, with readability, simulation/verification, and code generation as
  key objectives.
- MathWorks model-architecture guidance describes controller-model layers such
  as function, sub-function, schedule, control-flow, selection, and data-flow
  layers, and warns against splitting subsystems merely to save space.
- MathWorks architecture guidance recommends component-based modeling for
  complex systems and using hierarchy to communicate at an appropriate fidelity.
- MathWorks Model Advisor/Simulink Check positions model checks as a way to
  enforce modeling guidelines and detect inefficient or inaccurate modeling
  conditions.
- MathWorks Requirements Toolbox describes traceability as connecting
  requirements, models, tests, and code, including gap and impact analysis.
- Requirements-based verification guidance emphasizes turning informal
  requirements into unambiguous assessments and tracing requirements to design
  and tests.
- NASA logical decomposition guidance frames decomposition as functional
  analysis that translates top-level requirements into functions, allocates
  those functions downward, and identifies functional/subsystem interfaces.
- NASA review terminology for preliminary design reviews expects evidence that
  the design meets requirements, interfaces are identified, and verification
  methods are described.

## References

- MathWorks, Model Advisor checks for MAB modeling guidelines:
  https://www.mathworks.com/help/slcheck/ref/model-advisor-checks-for-mab-modeling-guidelines.html
- MathWorks, Understanding Model Architecture:
  https://www.mathworks.com/help/simulink/mdl_gd/maab/understanding-model-architecture.html
- MathWorks, System Architecture and Functionality:
  https://www.mathworks.com/help/simulink/ug/mbd-sys-arch-and-functionality.html
- MathWorks, Best Practices for Large-Scale Architecture Modeling:
  https://www.mathworks.com/help/systemcomposer/ug/best-practices-for-large-scale-architecture-modeling.html
- MathWorks, Modeling guidelines and Model Advisor checks for industry
  standards:
  https://www.mathworks.com/help/ecoder/ug/guidelines-checks-industry-stds-ecoder.html
- MathWorks, Requirements Toolbox:
  https://www.mathworks.com/products/requirements-toolbox.html
- MathWorks, Requirements-based verification with Simulink Test:
  https://www.mathworks.com/videos/requirements-based-verification-with-simulink-test-1554822878413.html
- NASA, Logical Decomposition:
  https://www.nasa.gov/reference/4-3-logical-decomposition/
- NASA Systems Engineering Handbook appendix:
  https://www.nasa.gov/reference/system-engineering-handbook-appendix/
