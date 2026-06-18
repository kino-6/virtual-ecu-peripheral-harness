% Generated from Mermaid-like MBD markup for ToyThermalProtectionController.
% Handoff artifact for MATLAB/Simulink environments; not executed by this repo.
model = 'ToyThermalProtectionControllerModel';
new_system(model);
open_system(model);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/HAL_LIMITER_set_derating']);
set_param([model '/HAL_LIMITER_set_derating'], 'Position', [80 80 230 140]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/HAL_PWM_set_fan_duty']);
set_param([model '/HAL_PWM_set_fan_duty'], 'Position', [300 80 450 140]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/HAL_SPI_read_temperature']);
set_param([model '/HAL_SPI_read_temperature'], 'Position', [520 80 670 140]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ScenarioReport_observedBehavior']);
set_param([model '/ScenarioReport_observedBehavior'], 'Position', [80 200 230 260]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ScenarioReport_passFailResult']);
set_param([model '/ScenarioReport_passFailResult'], 'Position', [300 200 450 260]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ToyFanDriverIC_dutyCommand']);
set_param([model '/ToyFanDriverIC_dutyCommand'], 'Position', [520 200 670 260]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ToyLoadLimiterIC_limitCommand']);
set_param([model '/ToyLoadLimiterIC_limitCommand'], 'Position', [80 320 230 380]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ToyTempSensorIC_invalidDebounced']);
set_param([model '/ToyTempSensorIC_invalidDebounced'], 'Position', [300 320 450 380]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ToyTempSensorIC_temperatureC']);
set_param([model '/ToyTempSensorIC_temperatureC'], 'Position', [520 320 670 380]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ToyTempSensorIC_temperatureValid']);
set_param([model '/ToyTempSensorIC_temperatureValid'], 'Position', [80 440 230 500]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ToyThermalProtectionController_deratingCommand']);
set_param([model '/ToyThermalProtectionController_deratingCommand'], 'Position', [300 440 450 500]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ToyThermalProtectionController_diagnosticFault']);
set_param([model '/ToyThermalProtectionController_diagnosticFault'], 'Position', [520 440 670 500]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ToyThermalProtectionController_fanDuty']);
set_param([model '/ToyThermalProtectionController_fanDuty'], 'Position', [80 560 230 620]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ToyThermalProtectionController_invalidDebounced']);
set_param([model '/ToyThermalProtectionController_invalidDebounced'], 'Position', [300 560 450 620]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ToyThermalProtectionController_safeCommandActive']);
set_param([model '/ToyThermalProtectionController_safeCommandActive'], 'Position', [520 560 670 620]);
add_block('simulink/Commonly Used Blocks/Subsystem', [model '/ToyThermalProtectionController_temperatureC']);
set_param([model '/ToyThermalProtectionController_temperatureC'], 'Position', [80 680 230 740]);
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_recoverFromLatch_Compare']);
set_param([model '/Rule_recoverFromLatch_Compare'], 'Position', [80 420 230 480]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_recoverFromLatch_Switch']);
set_param([model '/Rule_recoverFromLatch_Switch'], 'Position', [300 420 430 480]);
% priority 10 recoverFromLatch: from FAULT_LATCHED when temperatureValid == true and invalidDebounced == false and recoveryRequest == true then {'state': 'IDLE', 'fanDuty': '0', 'deratingCommand': '0', 'diagnosticFault': 'false', 'safeCommandActive': 'false'} scenarios ['thermal_protection_recovery']
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_faultLatch_Compare']);
set_param([model '/Rule_faultLatch_Compare'], 'Position', [80 520 230 580]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_faultLatch_Switch']);
set_param([model '/Rule_faultLatch_Switch'], 'Position', [300 520 430 580]);
% priority 20 faultLatch: from * when invalidDebounced == true then {'state': 'FAULT_LATCHED', 'fanDuty': 'safeDuty', 'deratingCommand': '0', 'diagnosticFault': 'true', 'safeCommandActive': 'true'} scenarios ['thermal_protection_fault_latch', 'thermal_protection_recovery']
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_holdLatchedFault_Compare']);
set_param([model '/Rule_holdLatchedFault_Compare'], 'Position', [80 620 230 680]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_holdLatchedFault_Switch']);
set_param([model '/Rule_holdLatchedFault_Switch'], 'Position', [300 620 430 680]);
% priority 30 holdLatchedFault: from FAULT_LATCHED when always then {'state': 'FAULT_LATCHED', 'fanDuty': 'safeDuty', 'deratingCommand': '0', 'diagnosticFault': 'true', 'safeCommandActive': 'true'} scenarios ['thermal_protection_fault_latch', 'thermal_protection_recovery']
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_sensorInvalid_Compare']);
set_param([model '/Rule_sensorInvalid_Compare'], 'Position', [80 720 230 780]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_sensorInvalid_Switch']);
set_param([model '/Rule_sensorInvalid_Switch'], 'Position', [300 720 430 780]);
% priority 40 sensorInvalid: from * when temperatureValid == false then {'state': 'SENSOR_FAULT', 'fanDuty': 'safeDuty', 'deratingCommand': '0', 'diagnosticFault': 'true', 'safeCommandActive': 'true'} scenarios ['thermal_protection_fault_latch', 'thermal_protection_recovery']
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_derating_Compare']);
set_param([model '/Rule_derating_Compare'], 'Position', [80 820 230 880]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_derating_Switch']);
set_param([model '/Rule_derating_Switch'], 'Position', [300 820 430 880]);
% priority 50 derating: from * when temperatureC >= deratingEntryThreshold then {'state': 'DERATING', 'fanDuty': 'deratingFanDuty', 'deratingCommand': 'deratingLimit', 'diagnosticFault': 'false', 'safeCommandActive': 'false'} scenarios ['thermal_protection_derating', 'thermal_protection_recovery']
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_highCooling_Compare']);
set_param([model '/Rule_highCooling_Compare'], 'Position', [80 920 230 980]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_highCooling_Switch']);
set_param([model '/Rule_highCooling_Switch'], 'Position', [300 920 430 980]);
% priority 60 highCooling: from * when temperatureC >= coolingOnThreshold then {'state': 'COOLING', 'fanDuty': 'coolingDuty', 'deratingCommand': '0', 'diagnosticFault': 'false', 'safeCommandActive': 'false'} scenarios ['thermal_protection_normal']
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_lowCooling_Compare']);
set_param([model '/Rule_lowCooling_Compare'], 'Position', [80 1020 230 1080]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_lowCooling_Switch']);
set_param([model '/Rule_lowCooling_Switch'], 'Position', [300 1020 430 1080]);
% priority 70 lowCooling: from * when temperatureC <= coolingOffThreshold then {'state': 'IDLE', 'fanDuty': '0', 'deratingCommand': '0', 'diagnosticFault': 'false', 'safeCommandActive': 'false'} scenarios ['thermal_protection_boundary']
add_line(model, 'ToyTempSensorIC_temperatureC/1', 'HAL_SPI_read_temperature/1', 'autorouting', 'on');
add_line(model, 'ToyTempSensorIC_temperatureValid/1', 'HAL_SPI_read_temperature/1', 'autorouting', 'on');
add_line(model, 'ToyTempSensorIC_invalidDebounced/1', 'ToyThermalProtectionController_invalidDebounced/1', 'autorouting', 'on');
add_line(model, 'HAL_SPI_read_temperature/1', 'ToyThermalProtectionController_temperatureC/1', 'autorouting', 'on');
add_line(model, 'ToyThermalProtectionController_fanDuty/1', 'HAL_PWM_set_fan_duty/1', 'autorouting', 'on');
add_line(model, 'ToyThermalProtectionController_deratingCommand/1', 'HAL_LIMITER_set_derating/1', 'autorouting', 'on');
add_line(model, 'HAL_PWM_set_fan_duty/1', 'ToyFanDriverIC_dutyCommand/1', 'autorouting', 'on');
add_line(model, 'HAL_LIMITER_set_derating/1', 'ToyLoadLimiterIC_limitCommand/1', 'autorouting', 'on');
add_line(model, 'ToyThermalProtectionController_diagnosticFault/1', 'ScenarioReport_observedBehavior/1', 'autorouting', 'on');
add_line(model, 'ToyThermalProtectionController_safeCommandActive/1', 'ScenarioReport_passFailResult/1', 'autorouting', 'on');
% State transition summary:
% RESET -> IDLE when temperatureValid == true
% IDLE -> COOLING when temperatureC >= coolingOnThreshold
% COOLING -> IDLE when temperatureC <= coolingOffThreshold
% COOLING -> DERATING when temperatureC >= deratingEntryThreshold
% DERATING -> COOLING when temperatureC < deratingEntryThreshold
% IDLE -> SENSOR_FAULT when temperatureValid == false
% COOLING -> SENSOR_FAULT when temperatureValid == false
% DERATING -> SENSOR_FAULT when temperatureValid == false
% SENSOR_FAULT -> FAULT_LATCHED when invalidDebounced == true
% FAULT_LATCHED -> IDLE when temperatureValid == true and invalidDebounced == false and recoveryRequest == true
save_system(model);
