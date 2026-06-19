% Generated from Mermaid-like MBD markup for ToyPowerMonitorIC.
% Semantic handoff artifact for MATLAB/Simulink environments; not executed by this repo.
% Supported subset: Inport, Outport, Constant, Compare To Constant, Logical Operator, Switch.
model = 'ToyPowerMonitorICModel';
new_system(model);
open_system(model);
add_block('simulink/Sources/In1', [model '/In_voltage']);
set_param([model '/In_voltage'], 'Position', [40 70 90 95]);
set_param([model '/In_voltage'], 'OutDataTypeStr', 'double');
add_block('simulink/Sinks/Out1', [model '/Out_ready']);
set_param([model '/Out_ready'], 'Position', [900 70 950 95]);
set_param([model '/Out_ready'], 'OutDataTypeStr', 'boolean');
add_block('simulink/Sinks/Out1', [model '/Out_fault']);
set_param([model '/Out_fault'], 'Position', [900 140 950 165]);
set_param([model '/Out_fault'], 'OutDataTypeStr', 'boolean');
add_block('simulink/Sources/Constant', [model '/Param_undervoltageThreshold']);
set_param([model '/Param_undervoltageThreshold'], 'Value', '7.0');
set_param([model '/Param_undervoltageThreshold'], 'OutDataTypeStr', 'double');
set_param([model '/Param_undervoltageThreshold'], 'Position', [180 70 260 100]);
add_block('simulink/Sources/Constant', [model '/Default_ready']);
set_param([model '/Default_ready'], 'Value', '0');
set_param([model '/Default_ready'], 'OutDataTypeStr', 'boolean');
set_param([model '/Default_ready'], 'Position', [520 480 620 510]);
add_line(model, 'Default_ready/1', 'Out_ready/1', 'autorouting', 'on');
add_block('simulink/Sources/Constant', [model '/Default_fault']);
set_param([model '/Default_fault'], 'Value', '0');
set_param([model '/Default_fault'], 'OutDataTypeStr', 'boolean');
set_param([model '/Default_fault'], 'Position', [520 525 620 555]);
add_line(model, 'Default_fault/1', 'Out_fault/1', 'autorouting', 'on');
% Semantic control structure. Lower numeric priority wins.
% Functional decomposition summary:
% Flow handoff summary:
% flow ECU_App.control_task -> HAL_SPI: write CONTROL.enable
% flow HAL_SPI -> ToyPowerMonitorIC.CONTROL: spi write
% flow ToyPowerMonitorIC.STATUS -> HAL_SPI: spi read
% flow HAL_SPI -> ECU_App.diagnostics: STATUS.ready, STATUS.undervoltageFault
% flow ToyPowerMonitorIC.ready -> ECU_App.diagnostics: ready signal
% flow ToyPowerMonitorIC.fault -> ECU_App.diagnostics: fault signal
% State transition summary:
% RESET -> INIT when powerOn
% INIT -> NORMAL when initSequenceOk
% NORMAL -> FAULT_LATCHED when voltage < undervoltageThreshold
% FAULT_LATCHED -> RESET when clearFault
save_system(model);
