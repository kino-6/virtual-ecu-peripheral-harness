# Specification Scaffold

Source requirements: `Requirements.md`

> Generated scaffold. This scaffold is not an approved specification.
> Resolve open questions before using it as approved MBD input.

## Review Status

- Behavior approval: **PENDING**
- Coverage meaning: requirement IDs are preserved for review; behavior is not approved by trace presence alone.
- Demo role: business-process demo for requirements, MBD handoff, harness preview, generated C preview, and reports.
- Tool boundary: repo-local execution is preview-only; existing MBD/product-test infrastructure remains the verification backend.

## Demo Assumption Policy

- The demo may use fictional component names and fictional requirement classes already stated in `Requirements.md`.
- The demo may generate scaffolds, TODO placeholders, trace tables, and review questions from the requirements.
- The demo must not invent accepted threshold values, timings, recovery conditions, fault semantics, or pass criteria.
- Missing behavior must remain visible as `TODO` or `open-question` until reviewed.

## Review Path

1. Review `Requirements.md` for stakeholder and system intent.
2. Review this scaffold for grouped behavior and unresolved decisions.
3. Approve or revise the missing behavior before accepting generated MBD source.
4. Regenerate MBD IR, handoff artifacts, preview C, scenarios, and reports from the approved source.
5. Use external MBD/product-test infrastructure for production-grade verification.

## Open Questions

Do not invent missing thresholds, timings, recovery rules, or fault semantics.

- `SYS-005`: confirm threshold/timing/recovery/fault semantics and required scenario evidence.
- `SYS-006`: confirm threshold/timing/recovery/fault semantics and required scenario evidence.
- `SYS-007`: confirm threshold/timing/recovery/fault semantics and required scenario evidence.
- `SYS-008`: confirm threshold/timing/recovery/fault semantics and required scenario evidence.

## Item Behavior

- `STK-001`: A reviewer can read one textual source and understand the control intent without opening a commercial MBD tool.
- `STK-002`: An MBD engineer can regenerate handoff artifacts for external MBD tool review from the same textual source.
- `STK-003`: A software engineer can inspect product-like ECU control logic that uses HAL-style boundaries and is not production-derived.
- `STK-004`: A test engineer can run preview scenarios and see inputs, scenario steps, observed behavior, expected behavior, and pass/fail results separated in the report.
- `STK-005`: A process reviewer can trace requirements to markup sections, generated artifacts, preview scenarios, and tests.
- `STK-006`: An AI workflow reviewer can see how MBD and harness artifacts reduce manual synchronization work across requirements, model changes, preview code, and reports.
- `STK-007`: A toolchain reviewer can distinguish the external MBD handoff path from the repo-local preview loop.
- `SYS-001`: The system shall read a fictional temperature value from `ToyTempSensorIC`.
- `SYS-002`: The system shall command a fictional fan duty output through `ToyFanDriverIC`.
- `SYS-003` (`DSC-A`): The system shall increase cooling command when temperature exceeds a fictional high threshold.
- `SYS-004` (`DSC-A`): The system shall reduce cooling command only after temperature falls below a fictional low threshold, preserving hysteresis.
- `SYS-005` (`DSC-B`): The system shall command fictional derating when temperature enters a high-but-valid protection range.
- `SYS-006` (`DSC-C`): The system shall enter a safe fictional command when the temperature input is marked invalid.
- `SYS-007` (`DSC-C`): The system shall latch a diagnostic fault when invalid sensor input persists beyond a fictional debounce window.
- `SYS-008` (`DSC-C`): The system shall recover from a latched fault only after explicit recovery conditions are met.
- `SYS-009`: The system shall expose normal, threshold-boundary, derating, sensor-fault, fault-latch, and recovery scenario behavior through generated review reports.

## Software And Control Behavior

- `SWE-001`: Each sample controller shall be described in `samples/<sample-id>/model.mbd.md` using Mermaid-like MBD markup as the public source.
- `SWE-002`: The parser shall convert the markup into an internal IR snapshot without requiring YAML as an input.
- `SWE-003`: The IR shall retain enough trace information to connect requirements, components, ports, states, flows, control rules, and tests.
- `SWE-004`: Generated preview C shall use HAL-style headers for sensor and fan interactions rather than Python internals.
- `SWE-005`: Generated preview C and Python preview behavior shall be labeled preview-only and non-certified.
- `ENG-001`: The repository shall provide a simplified Simulink-compatible preview engine.
- `ENG-002`: The engine shall execute only an explicitly declared subset of MBD semantics.
- `ENG-003`: The supported subset shall include at minimum inports, outports, parameters, compare, switch, logical operators, state transitions, and simple memory or hysteresis behavior.
- `ENG-004`: The engine shall produce deterministic step-by-step execution traces.
- `ENG-005`: The engine shall link each executed step to source model elements and requirement IDs when available.
- `ENG-006`: The engine shall not claim full Simulink compatibility.
- `ENG-007`: Unsupported behavior shall be reported as requiring external MBD tool verification.

## Harness And Test Behavior

- `CGEN-001`: The repository shall provide a preview-only MBD-to-C scaffold path.
- `CGEN-002`: Preview C shall be generated from MBD IR, not manually synchronized.
- `CGEN-003`: Preview C shall use HAL-style boundaries.
- `CGEN-004`: Preview C shall not call Python internals.
- `CGEN-005`: Preview C shall be suitable for early AI/CI review, not production deployment.
- `CGEN-006`: Production C generation is assumed to be handled by existing MBD/code-generation infrastructure.
- `HAR-001`: The preview harness shall simulate only fictional virtual IC boundaries needed by the scenario.
- `HAR-002`: The harness shall not modify ECU controller logic for simulation convenience.
- `HAR-003`: Preview scenarios shall be discrete steps, not a full plant or physics model.
- `HAR-004`: Reports shall separate model inputs, scenario steps, observed behavior, expected behavior, and pass/fail result.
- `HAR-005`: Scenario YAML, if used, shall be test input only and shall not be treated as the MBD source of truth.
- `HAR-006`: Harness shall support normal, threshold-boundary, derating, sensor fault, fault latch, and recovery scenarios.
- `HAR-007`: Harness reports shall state which behavior was checked locally and which behavior requires external MBD/product-test infrastructure.

## MBD And Toolchain Behavior

- `M2M-001`: Mermaid-like Markdown shall be the public authoring source.
- `M2M-002`: The Mermaid-to-MBD engine shall parse authoring blocks into MBD IR.
- `M2M-003`: The engine shall preserve requirement IDs, signal names, states, control rules, data flows, safety-class-like tags, and harness boundaries.
- `M2M-004`: The engine shall reject ambiguous or malformed model semantics with actionable diagnostics.
- `M2M-005`: Generated MBD IR shall be deterministic from unchanged Mermaid-like source.
- `M2M-006`: Mermaid diagrams shall be review artifacts; they shall not replace semantic MBD IR.
- `REQ2SPEC-001`: The repository shall extract requirement IDs, safety-class-like tags, statements, source sections, and planned evidence from `Requirements.md`.
- `REQ2SPEC-002`: The repository shall generate or update a human-readable specification scaffold from extracted requirements.
- `REQ2SPEC-003`: Generated specification scaffolds shall preserve requirement IDs and expose assumptions, open questions, unresolved behavior, and expected review evidence.
- `REQ2SPEC-004`: The generated specification shall separate item behavior, software/control behavior, harness behavior, MBD handoff behavior, preview engine behavior, AI/RAG behavior, and process evidence.
- `REQ2SPEC-005`: The agent shall ask the user before inventing behavior not present in requirements or approved specification text.
- `REQ2SPEC-006`: Specification updates shall be deterministic from unchanged requirements and template rules.
- `REQ2MBD-001`: The repository shall generate Mermaid-like MBD scaffold from approved requirements and human-readable specification content.
- `REQ2MBD-002`: Generated MBD source shall include trace references from model elements to requirement IDs and specification anchors.
- `REQ2MBD-003`: `DSC-B` and `DSC-C` requirements shall require explicit state, control, harness, scenario, and expected-behavior coverage before they can be marked covered.
- `REQ2MBD-004`: The validator shall report requirements that lack specification coverage.
- `REQ2MBD-005`: The validator shall report requirements that lack MBD coverage.
- `REQ2MBD-006`: The validator shall report MBD behavior that lacks requirement or specification trace.
- `REQ2MBD-007`: The scaffold generator shall emit open questions instead of silently inventing missing thresholds, timings, recovery rules, or fault semantics.
- `IR-001`: MBD IR shall represent ports, parameters, states, transitions, control rules, data flows, harness boundaries, and safety-class-like tags.
- `IR-002`: MBD IR shall retain traceability from requirement IDs to model elements.
- `IR-003`: MBD IR shall be tool-facing intermediate data, not the public authoring format.
- `IR-004`: MBD IR shall be exportable to existing MBD handoff artifacts.
- `IR-005`: MBD IR shall be executable by the repo preview engine for supported subset semantics.
- `MBD-001`: The tool shall generate a Markdown review document from the markup.
- `MBD-002`: The tool shall generate Mermaid and PlantUML preview diagrams from the markup.
- `MBD-003`: The tool shall generate a Simulink model-generation `.m` script from the markup.
- `MBD-004`: The tool shall generate a Modelica `.mo` text artifact from the markup.
- `MBD-005`: The tool shall generate SCXML or Stateflow-oriented handoff content when state behavior is present.
- `MBD-006`: The tool shall generate FMI-oriented metadata while clearly stating that no FMU is produced by this repository.
- `MBD-007`: Generated artifacts shall be deterministic for unchanged markup.
- `MBD-008`: Existing MBD tools shall remain the intended backend for production-grade verification and production MBD code generation.

## AI And RAG Behavior

- `AI-001`: AI shall be able to propose MBD updates from changed requirements.
- `AI-002`: AI shall be able to regenerate artifacts deterministically from Mermaid-like source.
- `AI-003`: AI shall be able to identify impacted requirements, model elements, preview engine behavior, generated C scaffold, and scenarios.
- `AI-004`: Reports shall show enough traceability for a human reviewer to judge whether AI-generated changes are plausible.
- `AI-005`: The workflow shall reduce manual synchronization between requirements, MBD diagrams, harness scenarios, generated preview code, and reports.
- `RAG-001`: The workflow shall support retrieval over repository-local requirements, specifications, MBD source, generated artifacts, tests, reports, and design principles.
- `RAG-002`: Retrieved context shall be cited or trace-linked in AI-generated changes when it affects requirements, MBD, harness behavior, or code scaffolds.
- `RAG-003`: RAG shall be used to reduce missed synchronization across requirements, MBD IR, preview engine semantics, harness scenarios, generated C, and reports.
- `RAG-004`: RAG shall not ingest real hardware datasheets, confidential product documentation, production ECU code, or vendor-specific register maps for this fictional MVP.
- `RAG-005`: If required context is missing or contradictory, the agent shall ask the user instead of inventing product behavior.

## Requirement Trace Appendix

| Requirement | Class | Source section | Statement | Planned evidence |
| --- | --- | --- | --- | --- |
| `STK-001` | `` | Stakeholder Needs | A reviewer can read one textual source and understand the control intent without opening a commercial MBD tool. | TBD |
| `STK-002` | `` | Stakeholder Needs | An MBD engineer can regenerate handoff artifacts for external MBD tool review from the same textual source. | TBD |
| `STK-003` | `` | Stakeholder Needs | A software engineer can inspect product-like ECU control logic that uses HAL-style boundaries and is not production-derived. | TBD |
| `STK-004` | `` | Stakeholder Needs | A test engineer can run preview scenarios and see inputs, scenario steps, observed behavior, expected behavior, and pass/fail results separated in the report. | TBD |
| `STK-005` | `` | Stakeholder Needs | A process reviewer can trace requirements to markup sections, generated artifacts, preview scenarios, and tests. | TBD |
| `STK-006` | `` | Stakeholder Needs | An AI workflow reviewer can see how MBD and harness artifacts reduce manual synchronization work across requirements, model changes, preview code, and reports. | TBD |
| `STK-007` | `` | Stakeholder Needs | A toolchain reviewer can distinguish the external MBD handoff path from the repo-local preview loop. | TBD |
| `SYS-001` | `` | System Requirements | The system shall read a fictional temperature value from `ToyTempSensorIC`. | Markup components, control rules, scenarios, reports |
| `SYS-002` | `` | System Requirements | The system shall command a fictional fan duty output through `ToyFanDriverIC`. | Markup components, control rules, scenarios, reports |
| `SYS-003` | `DSC-A` | System Requirements | The system shall increase cooling command when temperature exceeds a fictional high threshold. | Markup components, control rules, scenarios, reports |
| `SYS-004` | `DSC-A` | System Requirements | The system shall reduce cooling command only after temperature falls below a fictional low threshold, preserving hysteresis. | Markup components, control rules, scenarios, reports |
| `SYS-005` | `DSC-B` | System Requirements | The system shall command fictional derating when temperature enters a high-but-valid protection range. | Markup components, control rules, scenarios, reports |
| `SYS-006` | `DSC-C` | System Requirements | The system shall enter a safe fictional command when the temperature input is marked invalid. | Markup components, control rules, scenarios, reports |
| `SYS-007` | `DSC-C` | System Requirements | The system shall latch a diagnostic fault when invalid sensor input persists beyond a fictional debounce window. | Markup components, control rules, scenarios, reports |
| `SYS-008` | `DSC-C` | System Requirements | The system shall recover from a latched fault only after explicit recovery conditions are met. | Markup components, control rules, scenarios, reports |
| `SYS-009` | `` | System Requirements | The system shall expose normal, threshold-boundary, derating, sensor-fault, fault-latch, and recovery scenario behavior through generated review reports. | Markup components, control rules, scenarios, reports |
| `SWE-001` | `` | Software Requirements | Each sample controller shall be described in `samples/<sample-id>/model.mbd.md` using Mermaid-like MBD markup as the public source. | Parser tests, IR snapshot tests, preview C export tests |
| `SWE-002` | `` | Software Requirements | The parser shall convert the markup into an internal IR snapshot without requiring YAML as an input. | Parser tests, IR snapshot tests, preview C export tests |
| `SWE-003` | `` | Software Requirements | The IR shall retain enough trace information to connect requirements, components, ports, states, flows, control rules, and tests. | Parser tests, IR snapshot tests, preview C export tests |
| `SWE-004` | `` | Software Requirements | Generated preview C shall use HAL-style headers for sensor and fan interactions rather than Python internals. | Parser tests, IR snapshot tests, preview C export tests |
| `SWE-005` | `` | Software Requirements | Generated preview C and Python preview behavior shall be labeled preview-only and non-certified. | Parser tests, IR snapshot tests, preview C export tests |
| `M2M-001` | `` | Mermaid-To-MBD Engine Requirements | Mermaid-like Markdown shall be the public authoring source. | Mermaid-to-MBD parser tests and diagnostics tests |
| `M2M-002` | `` | Mermaid-To-MBD Engine Requirements | The Mermaid-to-MBD engine shall parse authoring blocks into MBD IR. | Mermaid-to-MBD parser tests and diagnostics tests |
| `M2M-003` | `` | Mermaid-To-MBD Engine Requirements | The engine shall preserve requirement IDs, signal names, states, control rules, data flows, safety-class-like tags, and harness boundaries. | Mermaid-to-MBD parser tests and diagnostics tests |
| `M2M-004` | `` | Mermaid-To-MBD Engine Requirements | The engine shall reject ambiguous or malformed model semantics with actionable diagnostics. | Mermaid-to-MBD parser tests and diagnostics tests |
| `M2M-005` | `` | Mermaid-To-MBD Engine Requirements | Generated MBD IR shall be deterministic from unchanged Mermaid-like source. | Mermaid-to-MBD parser tests and diagnostics tests |
| `M2M-006` | `` | Mermaid-To-MBD Engine Requirements | Mermaid diagrams shall be review artifacts; they shall not replace semantic MBD IR. | Mermaid-to-MBD parser tests and diagnostics tests |
| `REQ2SPEC-001` | `` | Requirements-To-Spec Support Requirements | The repository shall extract requirement IDs, safety-class-like tags, statements, source sections, and planned evidence from `Requirements.md`. | Requirements extraction tests and generated specification scaffold reviews |
| `REQ2SPEC-002` | `` | Requirements-To-Spec Support Requirements | The repository shall generate or update a human-readable specification scaffold from extracted requirements. | Requirements extraction tests and generated specification scaffold reviews |
| `REQ2SPEC-003` | `` | Requirements-To-Spec Support Requirements | Generated specification scaffolds shall preserve requirement IDs and expose assumptions, open questions, unresolved behavior, and expected review evidence. | Requirements extraction tests and generated specification scaffold reviews |
| `REQ2SPEC-004` | `` | Requirements-To-Spec Support Requirements | The generated specification shall separate item behavior, software/control behavior, harness behavior, MBD handoff behavior, preview engine behavior, AI/RAG behavior, and process evidence. | Requirements extraction tests and generated specification scaffold reviews |
| `REQ2SPEC-005` | `` | Requirements-To-Spec Support Requirements | The agent shall ask the user before inventing behavior not present in requirements or approved specification text. | Requirements extraction tests and generated specification scaffold reviews |
| `REQ2SPEC-006` | `` | Requirements-To-Spec Support Requirements | Specification updates shall be deterministic from unchanged requirements and template rules. | Requirements extraction tests and generated specification scaffold reviews |
| `REQ2MBD-001` | `` | Requirements-To-MBD Support Requirements | The repository shall generate Mermaid-like MBD scaffold from approved requirements and human-readable specification content. | MBD scaffold generation tests and coverage validation reports |
| `REQ2MBD-002` | `` | Requirements-To-MBD Support Requirements | Generated MBD source shall include trace references from model elements to requirement IDs and specification anchors. | MBD scaffold generation tests and coverage validation reports |
| `REQ2MBD-003` | `` | Requirements-To-MBD Support Requirements | `DSC-B` and `DSC-C` requirements shall require explicit state, control, harness, scenario, and expected-behavior coverage before they can be marked covered. | MBD scaffold generation tests and coverage validation reports |
| `REQ2MBD-004` | `` | Requirements-To-MBD Support Requirements | The validator shall report requirements that lack specification coverage. | MBD scaffold generation tests and coverage validation reports |
| `REQ2MBD-005` | `` | Requirements-To-MBD Support Requirements | The validator shall report requirements that lack MBD coverage. | MBD scaffold generation tests and coverage validation reports |
| `REQ2MBD-006` | `` | Requirements-To-MBD Support Requirements | The validator shall report MBD behavior that lacks requirement or specification trace. | MBD scaffold generation tests and coverage validation reports |
| `REQ2MBD-007` | `` | Requirements-To-MBD Support Requirements | The scaffold generator shall emit open questions instead of silently inventing missing thresholds, timings, recovery rules, or fault semantics. | MBD scaffold generation tests and coverage validation reports |
| `IR-001` | `` | MBD IR Requirements | MBD IR shall represent ports, parameters, states, transitions, control rules, data flows, harness boundaries, and safety-class-like tags. | IR snapshot tests and source-to-IR trace tests |
| `IR-002` | `` | MBD IR Requirements | MBD IR shall retain traceability from requirement IDs to model elements. | IR snapshot tests and source-to-IR trace tests |
| `IR-003` | `` | MBD IR Requirements | MBD IR shall be tool-facing intermediate data, not the public authoring format. | IR snapshot tests and source-to-IR trace tests |
| `IR-004` | `` | MBD IR Requirements | MBD IR shall be exportable to existing MBD handoff artifacts. | IR snapshot tests and source-to-IR trace tests |
| `IR-005` | `` | MBD IR Requirements | MBD IR shall be executable by the repo preview engine for supported subset semantics. | IR snapshot tests and source-to-IR trace tests |
| `MBD-001` | `` | MBD Handoff Requirements | The tool shall generate a Markdown review document from the markup. | Exporter tests and deterministic regeneration tests |
| `MBD-002` | `` | MBD Handoff Requirements | The tool shall generate Mermaid and PlantUML preview diagrams from the markup. | Exporter tests and deterministic regeneration tests |
| `MBD-003` | `` | MBD Handoff Requirements | The tool shall generate a Simulink model-generation `.m` script from the markup. | Exporter tests and deterministic regeneration tests |
| `MBD-004` | `` | MBD Handoff Requirements | The tool shall generate a Modelica `.mo` text artifact from the markup. | Exporter tests and deterministic regeneration tests |
| `MBD-005` | `` | MBD Handoff Requirements | The tool shall generate SCXML or Stateflow-oriented handoff content when state behavior is present. | Exporter tests and deterministic regeneration tests |
| `MBD-006` | `` | MBD Handoff Requirements | The tool shall generate FMI-oriented metadata while clearly stating that no FMU is produced by this repository. | Exporter tests and deterministic regeneration tests |
| `MBD-007` | `` | MBD Handoff Requirements | Generated artifacts shall be deterministic for unchanged markup. | Exporter tests and deterministic regeneration tests |
| `MBD-008` | `` | MBD Handoff Requirements | Existing MBD tools shall remain the intended backend for production-grade verification and production MBD code generation. | Exporter tests and deterministic regeneration tests |
| `ENG-001` | `` | Preview Engine Requirements | The repository shall provide a simplified Simulink-compatible preview engine. | Preview engine semantic subset tests and execution traces |
| `ENG-002` | `` | Preview Engine Requirements | The engine shall execute only an explicitly declared subset of MBD semantics. | Preview engine semantic subset tests and execution traces |
| `ENG-003` | `` | Preview Engine Requirements | The supported subset shall include at minimum inports, outports, parameters, compare, switch, logical operators, state transitions, and simple memory or hysteresis behavior. | Preview engine semantic subset tests and execution traces |
| `ENG-004` | `` | Preview Engine Requirements | The engine shall produce deterministic step-by-step execution traces. | Preview engine semantic subset tests and execution traces |
| `ENG-005` | `` | Preview Engine Requirements | The engine shall link each executed step to source model elements and requirement IDs when available. | Preview engine semantic subset tests and execution traces |
| `ENG-006` | `` | Preview Engine Requirements | The engine shall not claim full Simulink compatibility. | Preview engine semantic subset tests and execution traces |
| `ENG-007` | `` | Preview Engine Requirements | Unsupported behavior shall be reported as requiring external MBD tool verification. | Preview engine semantic subset tests and execution traces |
| `CGEN-001` | `` | MBD-To-C Process Requirements | The repository shall provide a preview-only MBD-to-C scaffold path. | Preview C generation tests and C syntax checks |
| `CGEN-002` | `` | MBD-To-C Process Requirements | Preview C shall be generated from MBD IR, not manually synchronized. | Preview C generation tests and C syntax checks |
| `CGEN-003` | `` | MBD-To-C Process Requirements | Preview C shall use HAL-style boundaries. | Preview C generation tests and C syntax checks |
| `CGEN-004` | `` | MBD-To-C Process Requirements | Preview C shall not call Python internals. | Preview C generation tests and C syntax checks |
| `CGEN-005` | `` | MBD-To-C Process Requirements | Preview C shall be suitable for early AI/CI review, not production deployment. | Preview C generation tests and C syntax checks |
| `CGEN-006` | `` | MBD-To-C Process Requirements | Production C generation is assumed to be handled by existing MBD/code-generation infrastructure. | Preview C generation tests and C syntax checks |
| `HAR-001` | `` | Harness Requirements | The preview harness shall simulate only fictional virtual IC boundaries needed by the scenario. | Preview runtime tests and scenario report checks |
| `HAR-002` | `` | Harness Requirements | The harness shall not modify ECU controller logic for simulation convenience. | Preview runtime tests and scenario report checks |
| `HAR-003` | `` | Harness Requirements | Preview scenarios shall be discrete steps, not a full plant or physics model. | Preview runtime tests and scenario report checks |
| `HAR-004` | `` | Harness Requirements | Reports shall separate model inputs, scenario steps, observed behavior, expected behavior, and pass/fail result. | Preview runtime tests and scenario report checks |
| `HAR-005` | `` | Harness Requirements | Scenario YAML, if used, shall be test input only and shall not be treated as the MBD source of truth. | Preview runtime tests and scenario report checks |
| `HAR-006` | `` | Harness Requirements | Harness shall support normal, threshold-boundary, derating, sensor fault, fault latch, and recovery scenarios. | Preview runtime tests and scenario report checks |
| `HAR-007` | `` | Harness Requirements | Harness reports shall state which behavior was checked locally and which behavior requires external MBD/product-test infrastructure. | Preview runtime tests and scenario report checks |
| `AI-001` | `` | AI Development Efficiency Requirements | AI shall be able to propose MBD updates from changed requirements. | Impact analysis reports and regenerated artifact diffs |
| `AI-002` | `` | AI Development Efficiency Requirements | AI shall be able to regenerate artifacts deterministically from Mermaid-like source. | Impact analysis reports and regenerated artifact diffs |
| `AI-003` | `` | AI Development Efficiency Requirements | AI shall be able to identify impacted requirements, model elements, preview engine behavior, generated C scaffold, and scenarios. | Impact analysis reports and regenerated artifact diffs |
| `AI-004` | `` | AI Development Efficiency Requirements | Reports shall show enough traceability for a human reviewer to judge whether AI-generated changes are plausible. | Impact analysis reports and regenerated artifact diffs |
| `AI-005` | `` | AI Development Efficiency Requirements | The workflow shall reduce manual synchronization between requirements, MBD diagrams, harness scenarios, generated preview code, and reports. | Impact analysis reports and regenerated artifact diffs |
| `RAG-001` | `` | RAG And Context Requirements | The workflow shall support retrieval over repository-local requirements, specifications, MBD source, generated artifacts, tests, reports, and design principles. | Retrieved-context citations, trace links, and ask-back records |
| `RAG-002` | `` | RAG And Context Requirements | Retrieved context shall be cited or trace-linked in AI-generated changes when it affects requirements, MBD, harness behavior, or code scaffolds. | Retrieved-context citations, trace links, and ask-back records |
| `RAG-003` | `` | RAG And Context Requirements | RAG shall be used to reduce missed synchronization across requirements, MBD IR, preview engine semantics, harness scenarios, generated C, and reports. | Retrieved-context citations, trace links, and ask-back records |
| `RAG-004` | `` | RAG And Context Requirements | RAG shall not ingest real hardware datasheets, confidential product documentation, production ECU code, or vendor-specific register maps for this fictional MVP. | Retrieved-context citations, trace links, and ask-back records |
| `RAG-005` | `` | RAG And Context Requirements | If required context is missing or contradictory, the agent shall ask the user instead of inventing product behavior. | Retrieved-context citations, trace links, and ask-back records |
| `PROC-001` | `` | Process Requirements | `Requirements.md` shall be updated before substantial changes to the validation example. | `Tasks.md`, docs updates, quality gates, project philosophy tests |
| `PROC-002` | `` | Process Requirements | `Tasks.md` shall break requirements into checked task-list items with explicit verification steps. | `Tasks.md`, docs updates, quality gates, project philosophy tests |
| `PROC-003` | `` | Process Requirements | Tests shall prove deterministic regeneration of generated artifacts. | `Tasks.md`, docs updates, quality gates, project philosophy tests |
| `PROC-004` | `` | Process Requirements | Documentation shall keep the commercial-tool-free MVP boundary clear while preserving the future path to Simulink, Modelica, and FMI export. | `Tasks.md`, docs updates, quality gates, project philosophy tests |
| `PROC-005` | `` | Process Requirements | Harness and preview engine implementation shall grow by TDD: add or update scenario/tests before adding supported semantics. | `Tasks.md`, docs updates, quality gates, project philosophy tests |
| `PROC-006` | `` | Process Requirements | New preview engine semantics shall not be considered supported until they are declared, tested, reported, and linked to requirements. | `Tasks.md`, docs updates, quality gates, project philosophy tests |
