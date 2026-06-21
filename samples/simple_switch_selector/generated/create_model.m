% Generated from Mermaid-like MBD markup for ToySwitchSelector.
% Semantic handoff artifact for MATLAB/Simulink environments; not executed by this repo.
% Supported subset: Inport, Outport, Constant, Compare To Constant, Logical Operator, Switch.
model = 'ToySwitchSelectorModel';
new_system(model);
open_system(model);
add_block('simulink/Sources/In1', [model '/In_selectHigh']);
set_param([model '/In_selectHigh'], 'Position', [40 70 90 95]);
set_param([model '/In_selectHigh'], 'OutDataTypeStr', 'boolean');
add_block('simulink/Sinks/Out1', [model '/Out_selectedValue']);
set_param([model '/Out_selectedValue'], 'Position', [900 70 950 95]);
set_param([model '/Out_selectedValue'], 'OutDataTypeStr', 'double');
add_block('simulink/Sources/Constant', [model '/Param_highValue']);
set_param([model '/Param_highValue'], 'Value', '100');
set_param([model '/Param_highValue'], 'OutDataTypeStr', 'double');
set_param([model '/Param_highValue'], 'Position', [180 70 260 100]);
add_block('simulink/Sources/Constant', [model '/Param_lowValue']);
set_param([model '/Param_lowValue'], 'Value', '25');
set_param([model '/Param_lowValue'], 'OutDataTypeStr', 'double');
set_param([model '/Param_lowValue'], 'Position', [180 125 260 155]);
% Semantic control structure. Lower numeric priority wins.
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_select_high_value_Compare']);
set_param([model '/Rule_select_high_value_Compare'], 'relop', '==');
set_param([model '/Rule_select_high_value_Compare'], 'const', 'true');
set_param([model '/Rule_select_high_value_Compare'], 'Position', [420 360 540 405]);
add_line(model, 'In_selectHigh/1', 'Rule_select_high_value_Compare/1', 'autorouting', 'on');
add_block('simulink/Sources/Constant', [model '/Default_selectedValue_0_0']);
set_param([model '/Default_selectedValue_0_0'], 'Value', '25');
set_param([model '/Default_selectedValue_0_0'], 'OutDataTypeStr', 'double');
set_param([model '/Default_selectedValue_0_0'], 'Position', [560 1120 660 1150]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_select_high_value_selectedValue_Switch']);
set_param([model '/Rule_select_high_value_selectedValue_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_select_high_value_selectedValue_Switch'], 'Position', [720 360 800 405]);
add_line(model, 'Param_highValue/1', 'Rule_select_high_value_selectedValue_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_select_high_value_Compare/1', 'Rule_select_high_value_selectedValue_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_selectedValue_0_0/1', 'Rule_select_high_value_selectedValue_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_select_high_value_selectedValue_Switch/1', 'Out_selectedValue/1', 'autorouting', 'on');
% priority 10 select_high_value: owner SwitchSelector from * when selectHigh == true then {'selectedValue': 'highValue'} scenarios ['select_high']
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_select_low_value_Compare']);
set_param([model '/Rule_select_low_value_Compare'], 'relop', '!=');
set_param([model '/Rule_select_low_value_Compare'], 'const', 'true');
set_param([model '/Rule_select_low_value_Compare'], 'Position', [420 500 540 545]);
add_line(model, 'In_selectHigh/1', 'Rule_select_low_value_Compare/1', 'autorouting', 'on');
add_block('simulink/Sources/Constant', [model '/Default_selectedValue_1_0']);
set_param([model '/Default_selectedValue_1_0'], 'Value', '25');
set_param([model '/Default_selectedValue_1_0'], 'OutDataTypeStr', 'double');
set_param([model '/Default_selectedValue_1_0'], 'Position', [560 1200 660 1230]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_select_low_value_selectedValue_Switch']);
set_param([model '/Rule_select_low_value_selectedValue_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_select_low_value_selectedValue_Switch'], 'Position', [720 500 800 545]);
add_line(model, 'Param_lowValue/1', 'Rule_select_low_value_selectedValue_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_select_low_value_Compare/1', 'Rule_select_low_value_selectedValue_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_selectedValue_1_0/1', 'Rule_select_low_value_selectedValue_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_select_low_value_selectedValue_Switch/1', 'Out_selectedValue/1', 'autorouting', 'on');
% priority 20 select_low_value: owner SwitchSelector from * when selectHigh != true then {'selectedValue': 'lowValue'} scenarios ['select_high']
% Functional decomposition summary:
% function SwitchSelector: owns ['selectedValue']; inputs ['selectHigh', 'highValue', 'lowValue']; outputs ['selectedValue']
% Flow handoff summary:
% flow ToySelectorSource.selectHigh -> SwitchSelector.selectHigh: selector input
% flow ToySwitchSelector.highValue -> SwitchSelector.highValue: high constant value
% flow ToySwitchSelector.lowValue -> SwitchSelector.lowValue: low constant value
% flow SwitchSelector.selectedValue -> ToySwitchSelector.selectedValue: selected output
% flow ToySwitchSelector.selectedValue -> ScenarioReport.observedBehavior: reported selected value
% State transition summary:
save_system(model);
