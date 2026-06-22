from pathlib import Path

from veph.cli import main
from veph.markup_parser import parse_markup, parse_markup_file
from veph.preview_runtime.generic import run_preview
from veph.sample_catalog import load_sample
from veph.spec_mbd_alignment import compare_spec_to_mbd, compare_spec_to_mbd_model
from veph.spec_mbd_conversion import generate_mbd_from_spec
from veph.spec_mbd_viewer import export_spec_mbd_viewer


ROOT = Path(__file__).resolve().parents[1]


def test_generate_mbd_from_spec_mermaid_is_parseable_and_aligned():
    sample = load_sample("simple_threshold_indicator", ROOT)

    mbd_text = generate_mbd_from_spec(
        sample.paths.spec,
        component_name="ToyThresholdIndicator",
        parameter_defaults={"limit": "10"},
        scenario="above_limit",
    )
    model = parse_markup(mbd_text, sample.paths.generated_dir / "from_spec.model.mbd.md")
    report = compare_spec_to_mbd_model(sample.paths.spec, model, model.source_path)

    assert model.component.name == "ToyThresholdIndicator"
    assert set(model.ports) == {"sampleValue", "active"}
    assert set(model.component.parameters) == {"limit"}
    assert len(model.controls) == 2
    assert report.passed is True
    assert "Generated from Spec Mermaid Design Overview" in mbd_text
    assert "priority 10 rule active_true" in mbd_text
    assert "priority 20 rule active_false" in mbd_text


def test_state_machine_spec_conversion_carries_review_context():
    sample = load_sample("simple_state_machine", ROOT)

    mbd_text = generate_mbd_from_spec(
        sample.paths.spec,
        component_name=sample.spec_mbd["component"],
        input_defaults=sample.spec_mbd["inputDefaults"],
        output_defaults=sample.spec_mbd["outputDefaults"],
        scenario=sample.spec_mbd["scenario"],
    )

    assert "```mbd-spec-review" in mbd_text
    assert "intent SM-001 | When `startCommand` is true while the controller is `IDLE`" in mbd_text
    assert "controller shall enter `RUNNING`, set `busy` to true, and clear `complete`." in mbd_text
    assert "spec-initial IDLE" in mbd_text
    assert "spec-transition [*] --> IDLE: initial" in mbd_text
    assert "open-question SMQ-001" in mbd_text


def test_layered_spec_uses_data_flow_and_control_semantics_only(tmp_path):
    spec = tmp_path / "spec.md"
    spec.write_text(
        """# Layered Relay Specification

## Intent

- `LAY-001`: `OFF --> ON` shall set `active=true` when `level >= onThreshold`.
- `LAY-002`: `ON --> OFF` shall set `active=false` when `level <= offThreshold`.
- `LAY-003`: The preview report shall show observed behavior.

## Component View

```mermaid
flowchart LR
  source[ToyLevelSource] --> shortcut{component shortcut should not execute?}
  shortcut --> bogus[Output active = true]
```

## Data Flow View

```mermaid
flowchart LR
  source[ToyLevelSource] -->|level| level[Input Port: level]
  on[Parameter: onThreshold] --> controller[ToyRelayController]
  off[Parameter: offThreshold] --> controller
  level --> controller
  controller --> active[Output active]
  active --> report[ScenarioReport.observedBehavior]
```

## Sequence View

```mermaid
sequenceDiagram
  participant Source as ToyLevelSource
  participant Controller as ToyRelayController
  Source->>Controller: level >= onThreshold
  Controller-->>Source: preview expects active=true
```

## Control Semantics View

```mermaid
stateDiagram-v2
  [*] --> OFF
  OFF --> ON: level >= onThreshold
  ON --> OFF: level <= offThreshold
```
""",
        encoding="utf-8",
    )

    mbd_text = generate_mbd_from_spec(
        spec,
        component_name="ToyLayeredRelay",
        parameter_defaults={"onThreshold": "70", "offThreshold": "30"},
        input_defaults={"level": "0"},
        output_defaults={"active": "false"},
        scenario="layered_relay",
    )
    model = parse_markup(mbd_text, tmp_path / "from_spec.model.mbd.md")
    report = compare_spec_to_mbd_model(spec, model, model.source_path)

    assert report.passed
    assert "Generated from Spec Data Flow View and Control Semantics View" in mbd_text
    assert "component shortcut should not execute" not in mbd_text
    assert "sequenceDiagram" not in mbd_text
    assert "OFF --> ON: level >= onThreshold" in mbd_text
    assert "ON --> OFF: level <= offThreshold" in mbd_text
    assert [control.name for control in model.controls] == ["off_to_on", "on_to_off"]


def test_state_machine_spec_conversion_supports_entry_during_exit_actions(tmp_path):
    spec = tmp_path / "spec.md"
    spec.write_text(
        """# State Action Specification

## Intent

- `ACT-001`: RUNNING shall assert `busy` during execution.
- `ACT-002`: DONE shall assert `complete` on entry.

## Design Overview

```mermaid
flowchart LR
  source[ToyCommandSource] -->|startCommand| start[Input Port: startCommand]
  start --> controller[ToyActionController]
  controller --> busy[Output busy]
  controller --> complete[Output complete]
  busy --> report[ScenarioReport.observedBehavior]
  complete --> report
```

## State Model

```mermaid
stateDiagram-v2
  [*] --> IDLE
  IDLE --> RUNNING: startCommand == true
  RUNNING --> DONE: always
  RUNNING: during busy=true
  DONE: entry complete=true
  DONE: exit complete=false
```
""",
        encoding="utf-8",
    )

    mbd_text = generate_mbd_from_spec(
        spec,
        component_name="ToyActionController",
        input_defaults={"startCommand": "false"},
        output_defaults={"busy": "false", "complete": "false"},
        scenario="state_actions",
    )
    model = parse_markup(mbd_text, tmp_path / "from_spec.model.mbd.md")

    assert "state-action RUNNING during | busy=true" in mbd_text
    assert "state-action DONE entry | complete=true" in mbd_text
    assert "rule running_during_action" in mbd_text
    assert "rule done_entry_action" in mbd_text
    assert "rule done_exit_action" in mbd_text
    assert any(control.name == "running_during_action" for control in model.controls)


def test_state_machine_spec_conversion_explicitly_handles_advanced_state_semantics(tmp_path):
    spec = tmp_path / "spec.md"
    spec.write_text(
        """# Advanced State MVP Specification

## Intent

- `ADV-001`: The model shall preserve hierarchy review intent.
- `ADV-002`: The model shall preserve parallel-region review intent.
- `ADV-003`: The model shall preserve shallow history review intent.
- `ADV-004`: The model shall preserve temporal event review intent.

## Design Overview

```mermaid
flowchart LR
  source[ToyAdvancedSource] -->|startCommand| start[Input Port: startCommand]
  start --> controller[ToyAdvancedController]
  controller --> busy[Output busy]
  busy --> report[ScenarioReport.observedBehavior]
```

## State Model

```mermaid
stateDiagram-v2
  [*] --> OFF
  state ACTIVE {
    [H] --> RUNNING
    RUNNING --> WAITING: after 10ms
    --
    MONITORING --> FAULTED: startCommand == false
  }
  OFF --> RUNNING: startCommand == true
```
""",
        encoding="utf-8",
    )

    mbd_text = generate_mbd_from_spec(
        spec,
        component_name="ToyAdvancedController",
        input_defaults={"startCommand": "false"},
        output_defaults={"busy": "false"},
        scenario="advanced_state_review",
    )
    model = parse_markup(mbd_text, tmp_path / "from_spec.model.mbd.md")

    assert "advanced-state hierarchy" in mbd_text
    assert "advanced-state parallel" in mbd_text
    assert "advanced-state history" in mbd_text
    assert "advanced-state temporal" in mbd_text
    assert "RUNNING --> WAITING: after 10ms" in mbd_text
    assert model.transitions


def test_generate_mbd_from_spec_supports_constant_items():
    sample = load_sample("simple_switch_selector", ROOT)

    mbd_text = generate_mbd_from_spec(
        sample.paths.spec,
        component_name=sample.spec_mbd["component"],
        input_defaults=sample.spec_mbd["inputDefaults"],
        output_defaults=sample.spec_mbd["outputDefaults"],
        scenario=sample.spec_mbd["scenario"],
    )
    model = parse_markup(mbd_text, sample.paths.generated["convertedMbd"])
    report = compare_spec_to_mbd_model(sample.paths.spec, model, model.source_path)

    assert report.passed
    assert "parameter highValue: count = 100" in mbd_text
    assert "parameter lowValue: count = 25" in mbd_text
    assert "port in selectHigh: bool = false" in mbd_text
    assert "constant value trace" in mbd_text
    assert "Constant: highValue = 100" in report.matched_nodes
    assert "Constant: lowValue = 25" in report.matched_nodes


def test_generate_mbd_from_spec_supports_logical_or_decision(tmp_path):
    spec = tmp_path / "spec.md"
    spec.write_text(
        """# Logical OR Specification

## Intent

- `LOGIC-001`: The output shall become active when `enable` is true or `force` is true.
- `LOGIC-002`: The output shall remain inactive when both inputs are false.
- `LOGIC-003`: The preview report shall show pass/fail evidence.

## Design Overview

```mermaid
flowchart LR
  source[ToyLogicSource] -->|enable| enable[Input Port: enable]
  source -->|force| force[Input Port: force]
  enable --> decision{enable == true or force == true?}
  force --> decision
  decision -->|true| active[Output active = true]
  decision -->|false| inactive[Output active = false]
  active --> report[ScenarioReport.observedBehavior]
  inactive --> report
```
""",
        encoding="utf-8",
    )

    mbd_text = generate_mbd_from_spec(
        spec,
        component_name="ToyLogicalOr",
        input_defaults={"enable": "false", "force": "false"},
        output_defaults={"active": "false"},
        scenario="forced_active",
    )
    model = parse_markup(mbd_text, tmp_path / "from_spec.model.mbd.md")
    report = compare_spec_to_mbd_model(spec, model, model.source_path)

    assert report.passed
    assert "port in enable: bool = false" in mbd_text
    assert "port in force: bool = false" in mbd_text
    assert "when enable == true or force == true then active=true" in mbd_text
    assert "when enable != true and force != true then active=false" in mbd_text
    assert model.controls[0].condition_expr.kind == "logical"
    assert model.controls[0].condition_expr.operator == "or"
    assert model.controls[1].condition_expr.kind == "logical"
    assert model.controls[1].condition_expr.operator == "and"


def test_generate_mbd_from_spec_supports_arithmetic_dataflow(tmp_path):
    spec = tmp_path / "spec.md"
    spec.write_text(
        """# Arithmetic Dataflow Specification

## Intent

- `CALC-001`: The model shall multiply `sampleValue` by `gain`.
- `CALC-002`: The model shall add `offset` to the gained value.
- `CALC-003`: The model shall multiply the sum by `scale`.
- `CALC-004`: The preview report shall show the final `processedValue`.

## Design Overview

```mermaid
flowchart LR
  source[ToyArithmeticSource] -->|sampleValue| sample[Input Port: sampleValue]
  gainParam[Parameter: gain] --> gainBlock[Gain]
  sample --> gainBlock
  gainBlock -->|amplified| sumBlock[Sum]
  offsetParam[Parameter: offset] --> sumBlock
  sumBlock -->|total| productBlock[Product]
  scaleParam[Parameter: scale] --> productBlock
  productBlock --> output[Output processedValue]
  output --> report[ScenarioReport.observedBehavior]
```
""",
        encoding="utf-8",
    )

    mbd_text = generate_mbd_from_spec(
        spec,
        component_name="ToyArithmeticDataflow",
        parameter_defaults={"gain": "2", "offset": "3", "scale": "5"},
        input_defaults={"sampleValue": "0"},
        output_defaults={"processedValue": "0"},
        scenario="nominal_math",
    )
    model = parse_markup(mbd_text, tmp_path / "from_spec.model.mbd.md")
    report = compare_spec_to_mbd_model(spec, model, model.source_path)
    result = run_preview(
        model,
        {
            "name": "nominal_math",
            "model": "ToyArithmeticDataflow",
            "steps": [{"atMs": 0, "setInput": {"name": "sampleValue", "value": 4}}],
            "expect": {"outputs": {"processedValue": 55}},
        },
    )

    assert report.passed
    assert result.passed
    assert "function Gain" in mbd_text
    assert "function Sum" in mbd_text
    assert "function Product" in mbd_text
    assert "when always then processedValue=(gain * sampleValue + offset) * scale" in mbd_text


def test_generate_mbd_from_spec_supports_saturation_and_lookup(tmp_path):
    spec = tmp_path / "spec.md"
    spec.write_text(
        """# Limit Lookup Specification

## Intent

- `LUT-001`: The model shall clamp `rawValue` between `lowerLimit` and `upperLimit`.
- `LUT-002`: The model shall map the limited value through fictional 1-D table points.
- `LUT-003`: The preview report shall show the final `commandValue`.

## Design Overview

```mermaid
flowchart LR
  source[ToyLookupSource] -->|rawValue| raw[Input Port: rawValue]
  lower[Parameter: lowerLimit] --> sat[Saturation]
  upper[Parameter: upperLimit] --> sat
  raw --> sat
  sat -->|limitedValue| lookup[Lookup1D]
  table[Constant: tablePoints = 0:0,50:10,100:20] --> lookup
  lookup --> output[Output commandValue]
  output --> report[ScenarioReport.observedBehavior]
```
""",
        encoding="utf-8",
    )

    mbd_text = generate_mbd_from_spec(
        spec,
        component_name="ToyLimitLookup",
        parameter_defaults={"lowerLimit": "0", "upperLimit": "100"},
        input_defaults={"rawValue": "0"},
        output_defaults={"commandValue": "0"},
        scenario="nominal_lookup",
    )
    model = parse_markup(mbd_text, tmp_path / "from_spec.model.mbd.md")
    report = compare_spec_to_mbd_model(spec, model, model.source_path)
    result = run_preview(
        model,
        {
            "name": "nominal_lookup",
            "model": "ToyLimitLookup",
            "steps": [{"atMs": 0, "setInput": {"name": "rawValue", "value": 60}}],
            "expect": {"outputs": {"commandValue": 12}},
        },
    )

    assert report.passed
    assert result.passed
    assert "function Saturation" in mbd_text
    assert "function Lookup1D" in mbd_text
    assert "when always then commandValue=lookup1d(clamp(rawValue, lowerLimit, upperLimit), tablePoints)" in mbd_text


def test_generate_mbd_from_spec_supports_structural_composition_subset(tmp_path):
    spec = tmp_path / "spec.md"
    spec.write_text(
        """# Structural Composition Specification

## Intent

- `STR-001`: The model shall show two functions in one subsystem-style group.
- `STR-002`: The model shall expose a vector input and vector output.
- `STR-003`: The generated MBD shall preserve the reviewable signal path.

## Design Overview

```mermaid
flowchart LR
  source[ToyVectorSource] -->|sampleVector| vector[Input Port: sampleVector[3]]
  gainParam[Parameter: gain] --> gainBlock[Conditioning/Gain]
  vector --> gainBlock
  gainBlock -->|conditionedVector| sumBlock[Conditioning/Sum]
  offsetParam[Parameter: offset] --> sumBlock
  sumBlock --> output[Output conditionedVector[3]]
  output --> report[ScenarioReport.observedBehavior]
```
""",
        encoding="utf-8",
    )

    mbd_text = generate_mbd_from_spec(
        spec,
        component_name="ToyVectorConditioning",
        parameter_defaults={"gain": "2", "offset": "1"},
        input_defaults={"sampleVector": "0"},
        output_defaults={"conditionedVector": "0"},
        scenario="vector_conditioning",
    )
    model = parse_markup(mbd_text, tmp_path / "from_spec.model.mbd.md")
    report = compare_spec_to_mbd_model(spec, model, model.source_path)

    assert report.passed
    assert "function Conditioning/Gain" in mbd_text
    assert "function Conditioning/Sum" in mbd_text
    assert "port in sampleVector: count[3] = 0" in mbd_text
    assert "port out conditionedVector: count[3] = 0" in mbd_text
    assert "Conditioning/Gain.conditionedVector -> Conditioning/Sum.conditionedVector" in mbd_text


def test_generate_mbd_from_spec_cli_writes_authoring_source(tmp_path):
    sample = load_sample("simple_threshold_indicator", ROOT)
    out = tmp_path / "from_spec.model.mbd.md"

    exit_code = main(
        [
            "generate-mbd-from-spec",
            "--spec",
            str(sample.paths.spec),
            "--component",
            "ToyThresholdIndicator",
            "--parameter-default",
            "limit=10",
            "--scenario",
            "above_limit",
            "--out",
            str(out),
        ]
    )

    assert exit_code == 0
    generated = parse_markup_file(out)
    assert generated.component.name == "ToyThresholdIndicator"
    assert compare_spec_to_mbd_model(sample.paths.spec, generated, out).passed is True


def test_render_spec_mbd_cli_uses_sample_metadata_from_spec_path(tmp_path):
    sample = load_sample("simple_threshold_indicator", ROOT)
    viewer = tmp_path / "viewer.html"
    converted = tmp_path / "from_spec.model.mbd.md"

    exit_code = main(
        [
            "render-spec-mbd",
            str(sample.paths.spec),
            "--out",
            str(viewer),
            "--mbd-out",
            str(converted),
        ]
    )

    assert exit_code == 0
    assert viewer.exists()
    assert converted.exists()
    assert parse_markup_file(converted).component.name == "ToyThresholdIndicator"
    assert "Alignment: PASS" in viewer.read_text(encoding="utf-8")
    assert "Script-generated by" in viewer.read_text(encoding="utf-8")


def test_export_sample_writes_converted_mbd_and_review_viewer():
    sample = load_sample("simple_threshold_indicator", ROOT)

    assert main(["export-sample", "simple_threshold_indicator"]) == 0

    converted = sample.paths.generated["convertedMbd"]
    viewer = sample.paths.generated["specMbdViewer"]
    assert converted.exists()
    assert viewer.exists()
    assert parse_markup_file(converted).component.name == "ToyThresholdIndicator"
    assert compare_spec_to_mbd(sample.paths.spec, converted).passed is True
    html = viewer.read_text(encoding="utf-8")
    assert "Spec Mermaid To MBD Review" in html
    assert "One-Minute Review" in html
    assert "python -m veph render-spec-mbd" in html
    assert "Alignment: PASS" in html
    assert "Spec Mermaid Semantic Graph" in html
    assert "Converted MBD Semantic Graph" in html
    assert "Interactive Review" in html
    assert "Matched edge details are omitted from this compact HTML view." in html
    assert 'data-input="sampleValue"' in html
    assert 'data-parameter="limit"' in html
    assert 'data-result="branch"' in html
    assert "Output active = true" in html


def test_spec_mbd_viewer_renders_alignment_evidence():
    sample = load_sample("simple_threshold_indicator", ROOT)
    mbd_text = generate_mbd_from_spec(
        sample.paths.spec,
        component_name="ToyThresholdIndicator",
        parameter_defaults={"limit": "10"},
        scenario="above_limit",
    )
    model = parse_markup(mbd_text, sample.paths.generated_dir / "from_spec.model.mbd.md")
    report = compare_spec_to_mbd_model(sample.paths.spec, model, model.source_path)

    html = export_spec_mbd_viewer(sample.paths.spec, model, report)

    assert "<svg" in html
    assert "ToyInputSource" in html
    assert "sampleValue &gt;= limit?" in html
    assert "Interactive Review" in html
    assert "One-Minute Review" in html
    assert "active-path" in html
    assert "data-node-role=\"decision\"" in html
    assert "data-result=\"output\"" in html
    assert "Missing MBD nodes" in html
    assert "Matched edges" not in html
    assert "None" in html
