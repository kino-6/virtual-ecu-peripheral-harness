% Generated from Mermaid-like MBD markup for ToyEnergyBufferMode.
% Semantic handoff artifact for MATLAB/Simulink environments; not executed by this repo.
% Supported subset: Inport, Outport, Constant, Compare To Constant, Logical Operator, Switch.
model = 'ToyEnergyBufferModeModel';
new_system(model);
open_system(model);
add_block('simulink/Sources/In1', [model '/In_externalPowerAvailable']);
set_param([model '/In_externalPowerAvailable'], 'Position', [40 70 90 95]);
set_param([model '/In_externalPowerAvailable'], 'OutDataTypeStr', 'boolean');
add_block('simulink/Sources/In1', [model '/In_emptyDetected']);
set_param([model '/In_emptyDetected'], 'Position', [40 140 90 165]);
set_param([model '/In_emptyDetected'], 'OutDataTypeStr', 'boolean');
add_block('simulink/Sinks/Out1', [model '/Out_supplyEnabled']);
set_param([model '/Out_supplyEnabled'], 'Position', [900 70 950 95]);
set_param([model '/Out_supplyEnabled'], 'OutDataTypeStr', 'boolean');
add_block('simulink/Sinks/Out1', [model '/Out_chargeIndicator']);
set_param([model '/Out_chargeIndicator'], 'Position', [900 140 950 165]);
set_param([model '/Out_chargeIndicator'], 'OutDataTypeStr', 'boolean');
% Semantic control structure. Lower numeric priority wins.
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_power_removed_discharge_1_Compare']);
set_param([model '/Rule_power_removed_discharge_1_Compare'], 'relop', '==');
set_param([model '/Rule_power_removed_discharge_1_Compare'], 'const', 'false');
set_param([model '/Rule_power_removed_discharge_1_Compare'], 'Position', [420 402 540 447]);
add_line(model, 'In_externalPowerAvailable/1', 'Rule_power_removed_discharge_1_Compare/1', 'autorouting', 'on');
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_power_removed_discharge_2_Compare']);
set_param([model '/Rule_power_removed_discharge_2_Compare'], 'relop', '==');
set_param([model '/Rule_power_removed_discharge_2_Compare'], 'const', 'false');
set_param([model '/Rule_power_removed_discharge_2_Compare'], 'Position', [420 444 540 489]);
add_line(model, 'In_emptyDetected/1', 'Rule_power_removed_discharge_2_Compare/1', 'autorouting', 'on');
add_block('simulink/Logic and Bit Operations/Logical Operator', [model '/Rule_power_removed_discharge_AND']);
set_param([model '/Rule_power_removed_discharge_AND'], 'Operator', 'AND');
set_param([model '/Rule_power_removed_discharge_AND'], 'Inputs', '2');
set_param([model '/Rule_power_removed_discharge_AND'], 'Position', [590 360 660 400]);
add_line(model, 'Rule_power_removed_discharge_1_Compare/1', 'Rule_power_removed_discharge_AND/1', 'autorouting', 'on');
add_line(model, 'Rule_power_removed_discharge_2_Compare/1', 'Rule_power_removed_discharge_AND/2', 'autorouting', 'on');
% state handoff power_removed_discharge: next state DISCHARGE
add_block('simulink/Sources/Constant', [model '/Rule_power_removed_discharge_supplyEnabled_true_Const']);
set_param([model '/Rule_power_removed_discharge_supplyEnabled_true_Const'], 'Value', 'true');
set_param([model '/Rule_power_removed_discharge_supplyEnabled_true_Const'], 'OutDataTypeStr', 'boolean');
set_param([model '/Rule_power_removed_discharge_supplyEnabled_true_Const'], 'Position', [560 920 660 950]);
add_block('simulink/Sources/Constant', [model '/Default_supplyEnabled_0_0']);
set_param([model '/Default_supplyEnabled_0_0'], 'Value', 'false');
set_param([model '/Default_supplyEnabled_0_0'], 'OutDataTypeStr', 'boolean');
set_param([model '/Default_supplyEnabled_0_0'], 'Position', [560 1120 660 1150]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_power_removed_discharge_supplyEnabled_Switch']);
set_param([model '/Rule_power_removed_discharge_supplyEnabled_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_power_removed_discharge_supplyEnabled_Switch'], 'Position', [720 360 800 405]);
add_line(model, 'Rule_power_removed_discharge_supplyEnabled_true_Const/1', 'Rule_power_removed_discharge_supplyEnabled_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_power_removed_discharge_AND/1', 'Rule_power_removed_discharge_supplyEnabled_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_supplyEnabled_0_0/1', 'Rule_power_removed_discharge_supplyEnabled_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_power_removed_discharge_supplyEnabled_Switch/1', 'Out_supplyEnabled/1', 'autorouting', 'on');
add_block('simulink/Sources/Constant', [model '/Rule_power_removed_discharge_chargeIndicator_false_Const']);
set_param([model '/Rule_power_removed_discharge_chargeIndicator_false_Const'], 'Value', 'false');
set_param([model '/Rule_power_removed_discharge_chargeIndicator_false_Const'], 'OutDataTypeStr', 'boolean');
set_param([model '/Rule_power_removed_discharge_chargeIndicator_false_Const'], 'Position', [560 955 660 985]);
add_block('simulink/Sources/Constant', [model '/Default_chargeIndicator_0_1']);
set_param([model '/Default_chargeIndicator_0_1'], 'Value', 'true');
set_param([model '/Default_chargeIndicator_0_1'], 'OutDataTypeStr', 'boolean');
set_param([model '/Default_chargeIndicator_0_1'], 'Position', [560 1155 660 1185]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_power_removed_discharge_chargeIndicator_Switch']);
set_param([model '/Rule_power_removed_discharge_chargeIndicator_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_power_removed_discharge_chargeIndicator_Switch'], 'Position', [720 386 800 431]);
add_line(model, 'Rule_power_removed_discharge_chargeIndicator_false_Const/1', 'Rule_power_removed_discharge_chargeIndicator_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_power_removed_discharge_AND/1', 'Rule_power_removed_discharge_chargeIndicator_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_chargeIndicator_0_1/1', 'Rule_power_removed_discharge_chargeIndicator_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_power_removed_discharge_chargeIndicator_Switch/1', 'Out_chargeIndicator/1', 'autorouting', 'on');
% priority 10 power_removed_discharge: owner ToyEnergyBufferModeController from CHARGE when externalPowerAvailable == false and emptyDetected == false then {'state': 'DISCHARGE', 'supplyEnabled': 'true', 'chargeIndicator': 'false'} scenarios ['source_loss_recovery']
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_discharge_empty_Compare']);
set_param([model '/Rule_discharge_empty_Compare'], 'relop', '==');
set_param([model '/Rule_discharge_empty_Compare'], 'const', 'true');
set_param([model '/Rule_discharge_empty_Compare'], 'Position', [420 500 540 545]);
add_line(model, 'In_emptyDetected/1', 'Rule_discharge_empty_Compare/1', 'autorouting', 'on');
% state handoff discharge_empty: next state EMPTY
add_block('simulink/Sources/Constant', [model '/Rule_discharge_empty_supplyEnabled_false_Const']);
set_param([model '/Rule_discharge_empty_supplyEnabled_false_Const'], 'Value', 'false');
set_param([model '/Rule_discharge_empty_supplyEnabled_false_Const'], 'OutDataTypeStr', 'boolean');
set_param([model '/Rule_discharge_empty_supplyEnabled_false_Const'], 'Position', [560 1000 660 1030]);
add_block('simulink/Sources/Constant', [model '/Default_supplyEnabled_1_0']);
set_param([model '/Default_supplyEnabled_1_0'], 'Value', 'false');
set_param([model '/Default_supplyEnabled_1_0'], 'OutDataTypeStr', 'boolean');
set_param([model '/Default_supplyEnabled_1_0'], 'Position', [560 1200 660 1230]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_discharge_empty_supplyEnabled_Switch']);
set_param([model '/Rule_discharge_empty_supplyEnabled_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_discharge_empty_supplyEnabled_Switch'], 'Position', [720 500 800 545]);
add_line(model, 'Rule_discharge_empty_supplyEnabled_false_Const/1', 'Rule_discharge_empty_supplyEnabled_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_discharge_empty_Compare/1', 'Rule_discharge_empty_supplyEnabled_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_supplyEnabled_1_0/1', 'Rule_discharge_empty_supplyEnabled_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_discharge_empty_supplyEnabled_Switch/1', 'Out_supplyEnabled/1', 'autorouting', 'on');
add_block('simulink/Sources/Constant', [model '/Rule_discharge_empty_chargeIndicator_false_Const']);
set_param([model '/Rule_discharge_empty_chargeIndicator_false_Const'], 'Value', 'false');
set_param([model '/Rule_discharge_empty_chargeIndicator_false_Const'], 'OutDataTypeStr', 'boolean');
set_param([model '/Rule_discharge_empty_chargeIndicator_false_Const'], 'Position', [560 1035 660 1065]);
add_block('simulink/Sources/Constant', [model '/Default_chargeIndicator_1_1']);
set_param([model '/Default_chargeIndicator_1_1'], 'Value', 'true');
set_param([model '/Default_chargeIndicator_1_1'], 'OutDataTypeStr', 'boolean');
set_param([model '/Default_chargeIndicator_1_1'], 'Position', [560 1235 660 1265]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_discharge_empty_chargeIndicator_Switch']);
set_param([model '/Rule_discharge_empty_chargeIndicator_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_discharge_empty_chargeIndicator_Switch'], 'Position', [720 526 800 571]);
add_line(model, 'Rule_discharge_empty_chargeIndicator_false_Const/1', 'Rule_discharge_empty_chargeIndicator_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_discharge_empty_Compare/1', 'Rule_discharge_empty_chargeIndicator_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_chargeIndicator_1_1/1', 'Rule_discharge_empty_chargeIndicator_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_discharge_empty_chargeIndicator_Switch/1', 'Out_chargeIndicator/1', 'autorouting', 'on');
% priority 20 discharge_empty: owner ToyEnergyBufferModeController from DISCHARGE when emptyDetected == true then {'state': 'EMPTY', 'supplyEnabled': 'false', 'chargeIndicator': 'false'} scenarios ['source_loss_recovery']
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_empty_reconnect_charge_Compare']);
set_param([model '/Rule_empty_reconnect_charge_Compare'], 'relop', '==');
set_param([model '/Rule_empty_reconnect_charge_Compare'], 'const', 'true');
set_param([model '/Rule_empty_reconnect_charge_Compare'], 'Position', [420 640 540 685]);
add_line(model, 'In_externalPowerAvailable/1', 'Rule_empty_reconnect_charge_Compare/1', 'autorouting', 'on');
% state handoff empty_reconnect_charge: next state CHARGE
add_block('simulink/Sources/Constant', [model '/Rule_empty_reconnect_charge_supplyEnabled_false_Const']);
set_param([model '/Rule_empty_reconnect_charge_supplyEnabled_false_Const'], 'Value', 'false');
set_param([model '/Rule_empty_reconnect_charge_supplyEnabled_false_Const'], 'OutDataTypeStr', 'boolean');
set_param([model '/Rule_empty_reconnect_charge_supplyEnabled_false_Const'], 'Position', [560 1080 660 1110]);
add_block('simulink/Sources/Constant', [model '/Default_supplyEnabled_2_0']);
set_param([model '/Default_supplyEnabled_2_0'], 'Value', 'false');
set_param([model '/Default_supplyEnabled_2_0'], 'OutDataTypeStr', 'boolean');
set_param([model '/Default_supplyEnabled_2_0'], 'Position', [560 1280 660 1310]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_empty_reconnect_charge_supplyEnabled_Switch']);
set_param([model '/Rule_empty_reconnect_charge_supplyEnabled_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_empty_reconnect_charge_supplyEnabled_Switch'], 'Position', [720 640 800 685]);
add_line(model, 'Rule_empty_reconnect_charge_supplyEnabled_false_Const/1', 'Rule_empty_reconnect_charge_supplyEnabled_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_empty_reconnect_charge_Compare/1', 'Rule_empty_reconnect_charge_supplyEnabled_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_supplyEnabled_2_0/1', 'Rule_empty_reconnect_charge_supplyEnabled_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_empty_reconnect_charge_supplyEnabled_Switch/1', 'Out_supplyEnabled/1', 'autorouting', 'on');
add_block('simulink/Sources/Constant', [model '/Rule_empty_reconnect_charge_chargeIndicator_true_Const']);
set_param([model '/Rule_empty_reconnect_charge_chargeIndicator_true_Const'], 'Value', 'true');
set_param([model '/Rule_empty_reconnect_charge_chargeIndicator_true_Const'], 'OutDataTypeStr', 'boolean');
set_param([model '/Rule_empty_reconnect_charge_chargeIndicator_true_Const'], 'Position', [560 1115 660 1145]);
add_block('simulink/Sources/Constant', [model '/Default_chargeIndicator_2_1']);
set_param([model '/Default_chargeIndicator_2_1'], 'Value', 'true');
set_param([model '/Default_chargeIndicator_2_1'], 'OutDataTypeStr', 'boolean');
set_param([model '/Default_chargeIndicator_2_1'], 'Position', [560 1315 660 1345]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_empty_reconnect_charge_chargeIndicator_Switch']);
set_param([model '/Rule_empty_reconnect_charge_chargeIndicator_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_empty_reconnect_charge_chargeIndicator_Switch'], 'Position', [720 666 800 711]);
add_line(model, 'Rule_empty_reconnect_charge_chargeIndicator_true_Const/1', 'Rule_empty_reconnect_charge_chargeIndicator_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_empty_reconnect_charge_Compare/1', 'Rule_empty_reconnect_charge_chargeIndicator_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_chargeIndicator_2_1/1', 'Rule_empty_reconnect_charge_chargeIndicator_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_empty_reconnect_charge_chargeIndicator_Switch/1', 'Out_chargeIndicator/1', 'autorouting', 'on');
% priority 30 empty_reconnect_charge: owner ToyEnergyBufferModeController from EMPTY when externalPowerAvailable == true then {'state': 'CHARGE', 'supplyEnabled': 'false', 'chargeIndicator': 'true'} scenarios ['source_loss_recovery']
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_discharge_reconnect_charge_Compare']);
set_param([model '/Rule_discharge_reconnect_charge_Compare'], 'relop', '==');
set_param([model '/Rule_discharge_reconnect_charge_Compare'], 'const', 'true');
set_param([model '/Rule_discharge_reconnect_charge_Compare'], 'Position', [420 780 540 825]);
add_line(model, 'In_externalPowerAvailable/1', 'Rule_discharge_reconnect_charge_Compare/1', 'autorouting', 'on');
% state handoff discharge_reconnect_charge: next state CHARGE
add_block('simulink/Sources/Constant', [model '/Rule_discharge_reconnect_charge_supplyEnabled_false_Const']);
set_param([model '/Rule_discharge_reconnect_charge_supplyEnabled_false_Const'], 'Value', 'false');
set_param([model '/Rule_discharge_reconnect_charge_supplyEnabled_false_Const'], 'OutDataTypeStr', 'boolean');
set_param([model '/Rule_discharge_reconnect_charge_supplyEnabled_false_Const'], 'Position', [560 1160 660 1190]);
add_block('simulink/Sources/Constant', [model '/Default_supplyEnabled_3_0']);
set_param([model '/Default_supplyEnabled_3_0'], 'Value', 'false');
set_param([model '/Default_supplyEnabled_3_0'], 'OutDataTypeStr', 'boolean');
set_param([model '/Default_supplyEnabled_3_0'], 'Position', [560 1360 660 1390]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_discharge_reconnect_charge_supplyEnabled_Switch']);
set_param([model '/Rule_discharge_reconnect_charge_supplyEnabled_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_discharge_reconnect_charge_supplyEnabled_Switch'], 'Position', [720 780 800 825]);
add_line(model, 'Rule_discharge_reconnect_charge_supplyEnabled_false_Const/1', 'Rule_discharge_reconnect_charge_supplyEnabled_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_discharge_reconnect_charge_Compare/1', 'Rule_discharge_reconnect_charge_supplyEnabled_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_supplyEnabled_3_0/1', 'Rule_discharge_reconnect_charge_supplyEnabled_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_discharge_reconnect_charge_supplyEnabled_Switch/1', 'Out_supplyEnabled/1', 'autorouting', 'on');
add_block('simulink/Sources/Constant', [model '/Rule_discharge_reconnect_charge_chargeIndicator_true_Const']);
set_param([model '/Rule_discharge_reconnect_charge_chargeIndicator_true_Const'], 'Value', 'true');
set_param([model '/Rule_discharge_reconnect_charge_chargeIndicator_true_Const'], 'OutDataTypeStr', 'boolean');
set_param([model '/Rule_discharge_reconnect_charge_chargeIndicator_true_Const'], 'Position', [560 1195 660 1225]);
add_block('simulink/Sources/Constant', [model '/Default_chargeIndicator_3_1']);
set_param([model '/Default_chargeIndicator_3_1'], 'Value', 'true');
set_param([model '/Default_chargeIndicator_3_1'], 'OutDataTypeStr', 'boolean');
set_param([model '/Default_chargeIndicator_3_1'], 'Position', [560 1395 660 1425]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_discharge_reconnect_charge_chargeIndicator_Switch']);
set_param([model '/Rule_discharge_reconnect_charge_chargeIndicator_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_discharge_reconnect_charge_chargeIndicator_Switch'], 'Position', [720 806 800 851]);
add_line(model, 'Rule_discharge_reconnect_charge_chargeIndicator_true_Const/1', 'Rule_discharge_reconnect_charge_chargeIndicator_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_discharge_reconnect_charge_Compare/1', 'Rule_discharge_reconnect_charge_chargeIndicator_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_chargeIndicator_3_1/1', 'Rule_discharge_reconnect_charge_chargeIndicator_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_discharge_reconnect_charge_chargeIndicator_Switch/1', 'Out_chargeIndicator/1', 'autorouting', 'on');
% priority 40 discharge_reconnect_charge: owner ToyEnergyBufferModeController from DISCHARGE when externalPowerAvailable == true then {'state': 'CHARGE', 'supplyEnabled': 'false', 'chargeIndicator': 'true'} scenarios ['source_loss_recovery']
% Functional decomposition summary:
% function ToyEnergyBufferModeController: owns ['CHARGE', 'DISCHARGE', 'EMPTY', 'supplyEnabled', 'chargeIndicator']; inputs ['externalPowerAvailable', 'emptyDetected']; outputs ['state', 'supplyEnabled', 'chargeIndicator']
% Flow handoff summary:
% flow ToyPowerSource.externalPowerAvailable -> ToyEnergyBufferModeController.externalPowerAvailable: source availability
% flow ToyEmptyMonitor.emptyDetected -> ToyEnergyBufferModeController.emptyDetected: empty indication
% flow ToyEnergyBufferModeController.supplyEnabled -> ToyEnergyBufferMode.supplyEnabled: supply command
% flow ToyEnergyBufferModeController.chargeIndicator -> ToyEnergyBufferMode.chargeIndicator: charge indication
% flow ToyEnergyBufferMode.supplyEnabled -> ScenarioReport.observedBehavior: reported supply command
% flow ToyEnergyBufferMode.chargeIndicator -> ScenarioReport.observedBehavior: reported charge indication
% State transition summary:
% CHARGE -> DISCHARGE when externalPowerAvailable == false and emptyDetected == false
% DISCHARGE -> EMPTY when emptyDetected == true
% EMPTY -> CHARGE when externalPowerAvailable == true
% DISCHARGE -> CHARGE when externalPowerAvailable == true
save_system(model);
