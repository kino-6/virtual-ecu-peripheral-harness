% Generated from Mermaid-like MBD markup for ToyThermalFanController.
% Semantic handoff artifact for MATLAB/Simulink environments; not executed by this repo.
% Supported subset: Inport, Outport, Constant, Compare To Constant, Logical Operator, Switch.
model = 'ToyThermalFanControllerModel';
new_system(model);
open_system(model);
add_block('simulink/Sources/In1', [model '/In_temperatureC']);
set_param([model '/In_temperatureC'], 'Position', [40 70 90 95]);
set_param([model '/In_temperatureC'], 'OutDataTypeStr', 'double');
add_block('simulink/Sources/In1', [model '/In_temperatureValid']);
set_param([model '/In_temperatureValid'], 'Position', [40 140 90 165]);
set_param([model '/In_temperatureValid'], 'OutDataTypeStr', 'boolean');
add_block('simulink/Sinks/Out1', [model '/Out_fanDuty']);
set_param([model '/Out_fanDuty'], 'Position', [900 70 950 95]);
set_param([model '/Out_fanDuty'], 'OutDataTypeStr', 'double');
add_block('simulink/Sinks/Out1', [model '/Out_fault']);
set_param([model '/Out_fault'], 'Position', [900 140 950 165]);
set_param([model '/Out_fault'], 'OutDataTypeStr', 'boolean');
add_block('simulink/Sources/Constant', [model '/Param_fanOnThreshold']);
set_param([model '/Param_fanOnThreshold'], 'Value', '75');
set_param([model '/Param_fanOnThreshold'], 'OutDataTypeStr', 'double');
set_param([model '/Param_fanOnThreshold'], 'Position', [180 70 260 100]);
add_block('simulink/Sources/Constant', [model '/Param_fanOffThreshold']);
set_param([model '/Param_fanOffThreshold'], 'Value', '65');
set_param([model '/Param_fanOffThreshold'], 'OutDataTypeStr', 'double');
set_param([model '/Param_fanOffThreshold'], 'Position', [180 125 260 155]);
add_block('simulink/Sources/Constant', [model '/Param_coolingDuty']);
set_param([model '/Param_coolingDuty'], 'Value', '80');
set_param([model '/Param_coolingDuty'], 'OutDataTypeStr', 'double');
set_param([model '/Param_coolingDuty'], 'Position', [180 180 260 210]);
add_block('simulink/Sources/Constant', [model '/Param_safeDuty']);
set_param([model '/Param_safeDuty'], 'Value', '35');
set_param([model '/Param_safeDuty'], 'OutDataTypeStr', 'double');
set_param([model '/Param_safeDuty'], 'Position', [180 235 260 265]);
% Semantic control structure. Lower numeric priority wins.
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_sensorFault_Compare']);
set_param([model '/Rule_sensorFault_Compare'], 'relop', '==');
set_param([model '/Rule_sensorFault_Compare'], 'const', 'false');
set_param([model '/Rule_sensorFault_Compare'], 'Position', [420 360 540 405]);
add_line(model, 'In_temperatureValid/1', 'Rule_sensorFault_Compare/1', 'autorouting', 'on');
% state handoff sensorFault: next state FAULT
add_block('simulink/Sources/Constant', [model '/Default_fanDuty_0_0']);
set_param([model '/Default_fanDuty_0_0'], 'Value', '0');
set_param([model '/Default_fanDuty_0_0'], 'OutDataTypeStr', 'double');
set_param([model '/Default_fanDuty_0_0'], 'Position', [560 1120 660 1150]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_sensorFault_fanDuty_Switch']);
set_param([model '/Rule_sensorFault_fanDuty_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_sensorFault_fanDuty_Switch'], 'Position', [720 360 800 405]);
add_line(model, 'Param_safeDuty/1', 'Rule_sensorFault_fanDuty_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_sensorFault_Compare/1', 'Rule_sensorFault_fanDuty_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_fanDuty_0_0/1', 'Rule_sensorFault_fanDuty_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_sensorFault_fanDuty_Switch/1', 'Out_fanDuty/1', 'autorouting', 'on');
add_block('simulink/Sources/Constant', [model '/Rule_sensorFault_fault_true_Const']);
set_param([model '/Rule_sensorFault_fault_true_Const'], 'Value', 'true');
set_param([model '/Rule_sensorFault_fault_true_Const'], 'OutDataTypeStr', 'boolean');
set_param([model '/Rule_sensorFault_fault_true_Const'], 'Position', [560 955 660 985]);
add_block('simulink/Sources/Constant', [model '/Default_fault_0_1']);
set_param([model '/Default_fault_0_1'], 'Value', 'false');
set_param([model '/Default_fault_0_1'], 'OutDataTypeStr', 'boolean');
set_param([model '/Default_fault_0_1'], 'Position', [560 1155 660 1185]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_sensorFault_fault_Switch']);
set_param([model '/Rule_sensorFault_fault_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_sensorFault_fault_Switch'], 'Position', [720 386 800 431]);
add_line(model, 'Rule_sensorFault_fault_true_Const/1', 'Rule_sensorFault_fault_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_sensorFault_Compare/1', 'Rule_sensorFault_fault_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_fault_0_1/1', 'Rule_sensorFault_fault_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_sensorFault_fault_Switch/1', 'Out_fault/1', 'autorouting', 'on');
% priority 1000 sensorFault: owner unallocated from * when temperatureValid == false then {'state': 'FAULT', 'fanDuty': 'safeDuty', 'fault': 'true'} scenarios []
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_highTemperature_Compare']);
set_param([model '/Rule_highTemperature_Compare'], 'relop', '>=');
set_param([model '/Rule_highTemperature_Compare'], 'const', 'fanOnThreshold');
set_param([model '/Rule_highTemperature_Compare'], 'Position', [420 500 540 545]);
add_line(model, 'In_temperatureC/1', 'Rule_highTemperature_Compare/1', 'autorouting', 'on');
% state handoff highTemperature: next state COOLING
add_block('simulink/Sources/Constant', [model '/Default_fanDuty_1_0']);
set_param([model '/Default_fanDuty_1_0'], 'Value', '0');
set_param([model '/Default_fanDuty_1_0'], 'OutDataTypeStr', 'double');
set_param([model '/Default_fanDuty_1_0'], 'Position', [560 1200 660 1230]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_highTemperature_fanDuty_Switch']);
set_param([model '/Rule_highTemperature_fanDuty_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_highTemperature_fanDuty_Switch'], 'Position', [720 500 800 545]);
add_line(model, 'Param_coolingDuty/1', 'Rule_highTemperature_fanDuty_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_highTemperature_Compare/1', 'Rule_highTemperature_fanDuty_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_fanDuty_1_0/1', 'Rule_highTemperature_fanDuty_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_highTemperature_fanDuty_Switch/1', 'Out_fanDuty/1', 'autorouting', 'on');
add_block('simulink/Sources/Constant', [model '/Rule_highTemperature_fault_false_Const']);
set_param([model '/Rule_highTemperature_fault_false_Const'], 'Value', 'false');
set_param([model '/Rule_highTemperature_fault_false_Const'], 'OutDataTypeStr', 'boolean');
set_param([model '/Rule_highTemperature_fault_false_Const'], 'Position', [560 1035 660 1065]);
add_block('simulink/Sources/Constant', [model '/Default_fault_1_1']);
set_param([model '/Default_fault_1_1'], 'Value', 'false');
set_param([model '/Default_fault_1_1'], 'OutDataTypeStr', 'boolean');
set_param([model '/Default_fault_1_1'], 'Position', [560 1235 660 1265]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_highTemperature_fault_Switch']);
set_param([model '/Rule_highTemperature_fault_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_highTemperature_fault_Switch'], 'Position', [720 526 800 571]);
add_line(model, 'Rule_highTemperature_fault_false_Const/1', 'Rule_highTemperature_fault_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_highTemperature_Compare/1', 'Rule_highTemperature_fault_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_fault_1_1/1', 'Rule_highTemperature_fault_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_highTemperature_fault_Switch/1', 'Out_fault/1', 'autorouting', 'on');
% priority 1001 highTemperature: owner unallocated from * when temperatureC >= fanOnThreshold then {'state': 'COOLING', 'fanDuty': 'coolingDuty', 'fault': 'false'} scenarios []
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_lowTemperature_Compare']);
set_param([model '/Rule_lowTemperature_Compare'], 'relop', '<=');
set_param([model '/Rule_lowTemperature_Compare'], 'const', 'fanOffThreshold');
set_param([model '/Rule_lowTemperature_Compare'], 'Position', [420 640 540 685]);
add_line(model, 'In_temperatureC/1', 'Rule_lowTemperature_Compare/1', 'autorouting', 'on');
% state handoff lowTemperature: next state IDLE
add_block('simulink/Sources/Constant', [model '/Rule_lowTemperature_fanDuty_0_Const']);
set_param([model '/Rule_lowTemperature_fanDuty_0_Const'], 'Value', '0');
set_param([model '/Rule_lowTemperature_fanDuty_0_Const'], 'OutDataTypeStr', 'double');
set_param([model '/Rule_lowTemperature_fanDuty_0_Const'], 'Position', [560 1080 660 1110]);
add_block('simulink/Sources/Constant', [model '/Default_fanDuty_2_0']);
set_param([model '/Default_fanDuty_2_0'], 'Value', '0');
set_param([model '/Default_fanDuty_2_0'], 'OutDataTypeStr', 'double');
set_param([model '/Default_fanDuty_2_0'], 'Position', [560 1280 660 1310]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_lowTemperature_fanDuty_Switch']);
set_param([model '/Rule_lowTemperature_fanDuty_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_lowTemperature_fanDuty_Switch'], 'Position', [720 640 800 685]);
add_line(model, 'Rule_lowTemperature_fanDuty_0_Const/1', 'Rule_lowTemperature_fanDuty_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_lowTemperature_Compare/1', 'Rule_lowTemperature_fanDuty_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_fanDuty_2_0/1', 'Rule_lowTemperature_fanDuty_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_lowTemperature_fanDuty_Switch/1', 'Out_fanDuty/1', 'autorouting', 'on');
add_block('simulink/Sources/Constant', [model '/Rule_lowTemperature_fault_false_Const']);
set_param([model '/Rule_lowTemperature_fault_false_Const'], 'Value', 'false');
set_param([model '/Rule_lowTemperature_fault_false_Const'], 'OutDataTypeStr', 'boolean');
set_param([model '/Rule_lowTemperature_fault_false_Const'], 'Position', [560 1115 660 1145]);
add_block('simulink/Sources/Constant', [model '/Default_fault_2_1']);
set_param([model '/Default_fault_2_1'], 'Value', 'false');
set_param([model '/Default_fault_2_1'], 'OutDataTypeStr', 'boolean');
set_param([model '/Default_fault_2_1'], 'Position', [560 1315 660 1345]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_lowTemperature_fault_Switch']);
set_param([model '/Rule_lowTemperature_fault_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_lowTemperature_fault_Switch'], 'Position', [720 666 800 711]);
add_line(model, 'Rule_lowTemperature_fault_false_Const/1', 'Rule_lowTemperature_fault_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_lowTemperature_Compare/1', 'Rule_lowTemperature_fault_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_fault_2_1/1', 'Rule_lowTemperature_fault_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_lowTemperature_fault_Switch/1', 'Out_fault/1', 'autorouting', 'on');
% priority 1002 lowTemperature: owner unallocated from * when temperatureC <= fanOffThreshold then {'state': 'IDLE', 'fanDuty': '0', 'fault': 'false'} scenarios []
% Functional decomposition summary:
% Flow handoff summary:
% flow ToyTempSensorIC.temperatureC -> HAL_SPI.read_temperature: virtual sensor sample
% flow HAL_SPI.read_temperature -> ToyThermalFanController.temperatureC: HAL input
% flow ToyThermalFanController.fanDuty -> HAL_PWM.set_fan_duty: generated ECU command
% flow HAL_PWM.set_fan_duty -> ToyFanDriverIC.dutyCommand: virtual actuator command
% flow ToyThermalFanController.fault -> ScenarioReport.observedBehavior: fault observation
% State transition summary:
% RESET -> IDLE when powerOn
% IDLE -> COOLING when temperatureC >= fanOnThreshold
% COOLING -> IDLE when temperatureC <= fanOffThreshold
% IDLE -> FAULT when temperatureValid == false
% COOLING -> FAULT when temperatureValid == false
% FAULT -> IDLE when temperatureValid == true
save_system(model);
