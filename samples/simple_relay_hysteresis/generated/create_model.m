% Generated from Mermaid-like MBD markup for ToyRelayHysteresis.
% Semantic handoff artifact for MATLAB/Simulink environments; not executed by this repo.
% Supported subset: Inport, Outport, Constant, Compare To Constant, Logical Operator, Switch.
model = 'ToyRelayHysteresisModel';
new_system(model);
open_system(model);
add_block('simulink/Sources/In1', [model '/In_level']);
set_param([model '/In_level'], 'Position', [40 70 90 95]);
set_param([model '/In_level'], 'OutDataTypeStr', 'double');
add_block('simulink/Sinks/Out1', [model '/Out_active']);
set_param([model '/Out_active'], 'Position', [900 70 950 95]);
set_param([model '/Out_active'], 'OutDataTypeStr', 'boolean');
add_block('simulink/Sources/Constant', [model '/Param_onThreshold']);
set_param([model '/Param_onThreshold'], 'Value', '70');
set_param([model '/Param_onThreshold'], 'OutDataTypeStr', 'double');
set_param([model '/Param_onThreshold'], 'Position', [180 70 260 100]);
add_block('simulink/Sources/Constant', [model '/Param_offThreshold']);
set_param([model '/Param_offThreshold'], 'Value', '30');
set_param([model '/Param_offThreshold'], 'OutDataTypeStr', 'double');
set_param([model '/Param_offThreshold'], 'Position', [180 125 260 155]);
% Semantic control structure. Lower numeric priority wins.
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_off_to_on_Compare']);
set_param([model '/Rule_off_to_on_Compare'], 'relop', '>=');
set_param([model '/Rule_off_to_on_Compare'], 'const', 'onThreshold');
set_param([model '/Rule_off_to_on_Compare'], 'Position', [420 360 540 405]);
add_line(model, 'In_level/1', 'Rule_off_to_on_Compare/1', 'autorouting', 'on');
% state handoff off_to_on: next state ON
add_block('simulink/Sources/Constant', [model '/Rule_off_to_on_active_true_Const']);
set_param([model '/Rule_off_to_on_active_true_Const'], 'Value', 'true');
set_param([model '/Rule_off_to_on_active_true_Const'], 'OutDataTypeStr', 'boolean');
set_param([model '/Rule_off_to_on_active_true_Const'], 'Position', [560 920 660 950]);
add_block('simulink/Sources/Constant', [model '/Default_active_0_0']);
set_param([model '/Default_active_0_0'], 'Value', 'false');
set_param([model '/Default_active_0_0'], 'OutDataTypeStr', 'boolean');
set_param([model '/Default_active_0_0'], 'Position', [560 1120 660 1150]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_off_to_on_active_Switch']);
set_param([model '/Rule_off_to_on_active_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_off_to_on_active_Switch'], 'Position', [720 360 800 405]);
add_line(model, 'Rule_off_to_on_active_true_Const/1', 'Rule_off_to_on_active_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_off_to_on_Compare/1', 'Rule_off_to_on_active_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_active_0_0/1', 'Rule_off_to_on_active_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_off_to_on_active_Switch/1', 'Out_active/1', 'autorouting', 'on');
% priority 10 off_to_on: owner ToyRelayController from OFF when level >= onThreshold then {'state': 'ON', 'active': 'true'} scenarios ['hysteresis_cycle']
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_on_to_off_Compare']);
set_param([model '/Rule_on_to_off_Compare'], 'relop', '<=');
set_param([model '/Rule_on_to_off_Compare'], 'const', 'offThreshold');
set_param([model '/Rule_on_to_off_Compare'], 'Position', [420 500 540 545]);
add_line(model, 'In_level/1', 'Rule_on_to_off_Compare/1', 'autorouting', 'on');
% state handoff on_to_off: next state OFF
add_block('simulink/Sources/Constant', [model '/Rule_on_to_off_active_false_Const']);
set_param([model '/Rule_on_to_off_active_false_Const'], 'Value', 'false');
set_param([model '/Rule_on_to_off_active_false_Const'], 'OutDataTypeStr', 'boolean');
set_param([model '/Rule_on_to_off_active_false_Const'], 'Position', [560 1000 660 1030]);
add_block('simulink/Sources/Constant', [model '/Default_active_1_0']);
set_param([model '/Default_active_1_0'], 'Value', 'false');
set_param([model '/Default_active_1_0'], 'OutDataTypeStr', 'boolean');
set_param([model '/Default_active_1_0'], 'Position', [560 1200 660 1230]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_on_to_off_active_Switch']);
set_param([model '/Rule_on_to_off_active_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_on_to_off_active_Switch'], 'Position', [720 500 800 545]);
add_line(model, 'Rule_on_to_off_active_false_Const/1', 'Rule_on_to_off_active_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_on_to_off_Compare/1', 'Rule_on_to_off_active_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_active_1_0/1', 'Rule_on_to_off_active_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_on_to_off_active_Switch/1', 'Out_active/1', 'autorouting', 'on');
% priority 20 on_to_off: owner ToyRelayController from ON when level <= offThreshold then {'state': 'OFF', 'active': 'false'} scenarios ['hysteresis_cycle']
% Functional decomposition summary:
% function ToyRelayController: owns ['OFF', 'ON', 'active']; inputs ['level', 'onThreshold', 'offThreshold']; outputs ['state', 'active']
% Flow handoff summary:
% flow ToyLevelSource.level -> ToyRelayController.level: scenario input
% flow ToyRelayHysteresis.onThreshold -> ToyRelayController.onThreshold: switch-on threshold
% flow ToyRelayHysteresis.offThreshold -> ToyRelayController.offThreshold: switch-off threshold
% flow ToyRelayController.active -> ToyRelayHysteresis.active: relay output
% flow ToyRelayHysteresis.active -> ScenarioReport.observedBehavior: reported active output
% State transition summary:
% OFF -> ON when level >= onThreshold
% ON -> OFF when level <= offThreshold
save_system(model);
