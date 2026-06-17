% Generated from Mermaid-like MBD markup for ToyThermalFanController.
% Handoff artifact for MATLAB/Simulink environments; not executed by this repo.
model = 'ToyThermalFanControllerModel';
new_system(model);
open_system(model);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/HAL_PWM_set_fan_duty']);
set_param([model '/HAL_PWM_set_fan_duty'], 'Position', [80 80 230 140]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/HAL_SPI_read_temperature']);
set_param([model '/HAL_SPI_read_temperature'], 'Position', [300 80 450 140]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ScenarioReport_observedBehavior']);
set_param([model '/ScenarioReport_observedBehavior'], 'Position', [520 80 670 140]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ToyFanDriverIC_dutyCommand']);
set_param([model '/ToyFanDriverIC_dutyCommand'], 'Position', [80 200 230 260]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ToyTempSensorIC_temperatureC']);
set_param([model '/ToyTempSensorIC_temperatureC'], 'Position', [300 200 450 260]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ToyThermalFanController_fanDuty']);
set_param([model '/ToyThermalFanController_fanDuty'], 'Position', [520 200 670 260]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ToyThermalFanController_fault']);
set_param([model '/ToyThermalFanController_fault'], 'Position', [80 320 230 380]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ToyThermalFanController_temperatureC']);
set_param([model '/ToyThermalFanController_temperatureC'], 'Position', [300 320 450 380]);
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_sensorFault_Compare']);
set_param([model '/Rule_sensorFault_Compare'], 'Position', [80 420 230 480]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_sensorFault_Switch']);
set_param([model '/Rule_sensorFault_Switch'], 'Position', [300 420 430 480]);
% sensorFault: when temperatureValid == false then {'state': 'FAULT', 'fanDuty': 'safeDuty', 'fault': 'true'}
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_highTemperature_Compare']);
set_param([model '/Rule_highTemperature_Compare'], 'Position', [80 520 230 580]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_highTemperature_Switch']);
set_param([model '/Rule_highTemperature_Switch'], 'Position', [300 520 430 580]);
% highTemperature: when temperatureC >= fanOnThreshold then {'state': 'COOLING', 'fanDuty': 'coolingDuty', 'fault': 'false'}
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_lowTemperature_Compare']);
set_param([model '/Rule_lowTemperature_Compare'], 'Position', [80 620 230 680]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_lowTemperature_Switch']);
set_param([model '/Rule_lowTemperature_Switch'], 'Position', [300 620 430 680]);
% lowTemperature: when temperatureC <= fanOffThreshold then {'state': 'IDLE', 'fanDuty': '0', 'fault': 'false'}
add_line(model, 'ToyTempSensorIC_temperatureC/1', 'HAL_SPI_read_temperature/1', 'autorouting', 'on');
add_line(model, 'HAL_SPI_read_temperature/1', 'ToyThermalFanController_temperatureC/1', 'autorouting', 'on');
add_line(model, 'ToyThermalFanController_fanDuty/1', 'HAL_PWM_set_fan_duty/1', 'autorouting', 'on');
add_line(model, 'HAL_PWM_set_fan_duty/1', 'ToyFanDriverIC_dutyCommand/1', 'autorouting', 'on');
add_line(model, 'ToyThermalFanController_fault/1', 'ScenarioReport_observedBehavior/1', 'autorouting', 'on');
% State transition summary:
% RESET -> IDLE when powerOn
% IDLE -> COOLING when temperatureC >= fanOnThreshold
% COOLING -> IDLE when temperatureC <= fanOffThreshold
% IDLE -> FAULT when temperatureValid == false
% COOLING -> FAULT when temperatureValid == false
% FAULT -> IDLE when temperatureValid == true
save_system(model);
