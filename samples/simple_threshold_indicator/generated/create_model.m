% Generated from Mermaid-like MBD markup for ToyThresholdIndicator.
% Semantic handoff artifact for MATLAB/Simulink environments; not executed by this repo.
% Supported subset: Inport, Outport, Constant, Compare To Constant, Logical Operator, Switch.
model = 'ToyThresholdIndicatorModel';
new_system(model);
open_system(model);
add_block('simulink/Sources/In1', [model '/In_sampleValue']);
set_param([model '/In_sampleValue'], 'Position', [40 70 90 95]);
set_param([model '/In_sampleValue'], 'OutDataTypeStr', 'double');
add_block('simulink/Sinks/Out1', [model '/Out_active']);
set_param([model '/Out_active'], 'Position', [900 70 950 95]);
set_param([model '/Out_active'], 'OutDataTypeStr', 'boolean');
add_block('simulink/Sources/Constant', [model '/Param_limit']);
set_param([model '/Param_limit'], 'Value', '10');
set_param([model '/Param_limit'], 'OutDataTypeStr', 'double');
set_param([model '/Param_limit'], 'Position', [180 70 260 100]);
% Semantic control structure. Lower numeric priority wins.
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_activate_Compare']);
set_param([model '/Rule_activate_Compare'], 'relop', '>=');
set_param([model '/Rule_activate_Compare'], 'const', 'limit');
set_param([model '/Rule_activate_Compare'], 'Position', [420 360 540 405]);
add_line(model, 'In_sampleValue/1', 'Rule_activate_Compare/1', 'autorouting', 'on');
% state handoff activate: next state ACTIVE
add_block('simulink/Sources/Constant', [model '/Rule_activate_active_true_Const']);
set_param([model '/Rule_activate_active_true_Const'], 'Value', 'true');
set_param([model '/Rule_activate_active_true_Const'], 'OutDataTypeStr', 'boolean');
set_param([model '/Rule_activate_active_true_Const'], 'Position', [560 920 660 950]);
add_block('simulink/Sources/Constant', [model '/Default_active_0_0']);
set_param([model '/Default_active_0_0'], 'Value', 'false');
set_param([model '/Default_active_0_0'], 'OutDataTypeStr', 'boolean');
set_param([model '/Default_active_0_0'], 'Position', [560 1120 660 1150]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_activate_active_Switch']);
set_param([model '/Rule_activate_active_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_activate_active_Switch'], 'Position', [720 360 800 405]);
add_line(model, 'Rule_activate_active_true_Const/1', 'Rule_activate_active_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_activate_Compare/1', 'Rule_activate_active_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_active_0_0/1', 'Rule_activate_active_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_activate_active_Switch/1', 'Out_active/1', 'autorouting', 'on');
% priority 1000 activate: owner unallocated from * when sampleValue >= limit then {'state': 'ACTIVE', 'active': 'true'} scenarios ['above_limit']
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_clear_Compare']);
set_param([model '/Rule_clear_Compare'], 'relop', '<');
set_param([model '/Rule_clear_Compare'], 'const', 'limit');
set_param([model '/Rule_clear_Compare'], 'Position', [420 500 540 545]);
add_line(model, 'In_sampleValue/1', 'Rule_clear_Compare/1', 'autorouting', 'on');
% state handoff clear: next state IDLE
add_block('simulink/Sources/Constant', [model '/Rule_clear_active_false_Const']);
set_param([model '/Rule_clear_active_false_Const'], 'Value', 'false');
set_param([model '/Rule_clear_active_false_Const'], 'OutDataTypeStr', 'boolean');
set_param([model '/Rule_clear_active_false_Const'], 'Position', [560 1000 660 1030]);
add_block('simulink/Sources/Constant', [model '/Default_active_1_0']);
set_param([model '/Default_active_1_0'], 'Value', 'false');
set_param([model '/Default_active_1_0'], 'OutDataTypeStr', 'boolean');
set_param([model '/Default_active_1_0'], 'Position', [560 1200 660 1230]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_clear_active_Switch']);
set_param([model '/Rule_clear_active_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_clear_active_Switch'], 'Position', [720 500 800 545]);
add_line(model, 'Rule_clear_active_false_Const/1', 'Rule_clear_active_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_clear_Compare/1', 'Rule_clear_active_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_active_1_0/1', 'Rule_clear_active_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_clear_active_Switch/1', 'Out_active/1', 'autorouting', 'on');
% priority 1001 clear: owner unallocated from * when sampleValue < limit then {'state': 'IDLE', 'active': 'false'} scenarios []
% Functional decomposition summary:
% Flow handoff summary:
% flow ToyInputSource.sampleValue -> ToyThresholdIndicator.sampleValue: scenario input
% flow ToyThresholdIndicator.active -> ScenarioReport.observedBehavior: reported output
% State transition summary:
% IDLE -> ACTIVE when sampleValue >= limit trace SIMPLE-001
% ACTIVE -> IDLE when sampleValue < limit trace SIMPLE-002
save_system(model);
