% Generated from fictional Textual MBD model ToyPowerMonitorIC.
% Canonical source: Textual MBD YAML. Regenerate instead of editing as source.
% This best-effort script requires MATLAB/Simulink if executed.
model = 'ToyPowerMonitorModel';
new_system(model);
open_system(model);
add_block('simulink/Sources/Constant', [model '/Voltage']);
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/UndervoltageThreshold']);
set_param([model '/UndervoltageThreshold'], 'const', '7.0');
add_block('simulink/Sinks/Display', [model '/StatusDisplay']);
add_line(model, 'Voltage/1', 'UndervoltageThreshold/1');
add_line(model, 'UndervoltageThreshold/1', 'StatusDisplay/1');
% State machine summary:
% RESET -> INIT when powerOn
% INIT -> NORMAL when initSequenceOk
% NORMAL -> FAULT_LATCHED when voltage < undervoltageThreshold
save_system(model);
