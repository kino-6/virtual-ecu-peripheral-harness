% Generated from Mermaid-like MBD markup for ToyPowerMonitorIC.
% Handoff artifact for MATLAB/Simulink environments; not executed by this repo.
model = 'ToyPowerMonitorICModel';
new_system(model);
open_system(model);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ECU_App_control_task']);
set_param([model '/ECU_App_control_task'], 'Position', [80 80 230 140]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ECU_App_diagnostics']);
set_param([model '/ECU_App_diagnostics'], 'Position', [300 80 450 140]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/HAL_SPI']);
set_param([model '/HAL_SPI'], 'Position', [520 80 670 140]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ToyPowerMonitorIC_CONTROL']);
set_param([model '/ToyPowerMonitorIC_CONTROL'], 'Position', [80 200 230 260]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ToyPowerMonitorIC_STATUS']);
set_param([model '/ToyPowerMonitorIC_STATUS'], 'Position', [300 200 450 260]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ToyPowerMonitorIC_fault']);
set_param([model '/ToyPowerMonitorIC_fault'], 'Position', [520 200 670 260]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ToyPowerMonitorIC_ready']);
set_param([model '/ToyPowerMonitorIC_ready'], 'Position', [80 320 230 380]);
add_line(model, 'ECU_App_control_task/1', 'HAL_SPI/1', 'autorouting', 'on');
add_line(model, 'HAL_SPI/1', 'ToyPowerMonitorIC_CONTROL/1', 'autorouting', 'on');
add_line(model, 'ToyPowerMonitorIC_STATUS/1', 'HAL_SPI/1', 'autorouting', 'on');
add_line(model, 'HAL_SPI/1', 'ECU_App_diagnostics/1', 'autorouting', 'on');
add_line(model, 'ToyPowerMonitorIC_ready/1', 'ECU_App_diagnostics/1', 'autorouting', 'on');
add_line(model, 'ToyPowerMonitorIC_fault/1', 'ECU_App_diagnostics/1', 'autorouting', 'on');
% State transition summary:
% RESET -> INIT when powerOn
% INIT -> NORMAL when initSequenceOk
% NORMAL -> FAULT_LATCHED when voltage < undervoltageThreshold
% FAULT_LATCHED -> RESET when clearFault
save_system(model);
