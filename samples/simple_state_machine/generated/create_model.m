% Generated from Mermaid-like MBD markup for ToyStateMachine.
% Semantic handoff artifact for MATLAB/Simulink environments; not executed by this repo.
% Supported subset: Inport, Outport, Constant, Compare To Constant, Logical Operator, Switch.
model = 'ToyStateMachineModel';
new_system(model);
open_system(model);
add_block('simulink/Sources/In1', [model '/In_startCommand']);
set_param([model '/In_startCommand'], 'Position', [40 70 90 95]);
set_param([model '/In_startCommand'], 'OutDataTypeStr', 'boolean');
add_block('simulink/Sources/In1', [model '/In_finishCommand']);
set_param([model '/In_finishCommand'], 'Position', [40 140 90 165]);
set_param([model '/In_finishCommand'], 'OutDataTypeStr', 'boolean');
add_block('simulink/Sources/In1', [model '/In_resetCommand']);
set_param([model '/In_resetCommand'], 'Position', [40 210 90 235]);
set_param([model '/In_resetCommand'], 'OutDataTypeStr', 'boolean');
add_block('simulink/Sinks/Out1', [model '/Out_busy']);
set_param([model '/Out_busy'], 'Position', [900 70 950 95]);
set_param([model '/Out_busy'], 'OutDataTypeStr', 'boolean');
add_block('simulink/Sinks/Out1', [model '/Out_complete']);
set_param([model '/Out_complete'], 'Position', [900 140 950 165]);
set_param([model '/Out_complete'], 'OutDataTypeStr', 'boolean');
% Semantic control structure. Lower numeric priority wins.
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_start_running_Compare']);
set_param([model '/Rule_start_running_Compare'], 'relop', '==');
set_param([model '/Rule_start_running_Compare'], 'const', 'true');
set_param([model '/Rule_start_running_Compare'], 'Position', [420 360 540 405]);
add_line(model, 'In_startCommand/1', 'Rule_start_running_Compare/1', 'autorouting', 'on');
% state handoff start_running: next state RUNNING
add_block('simulink/Sources/Constant', [model '/Rule_start_running_busy_true_Const']);
set_param([model '/Rule_start_running_busy_true_Const'], 'Value', 'true');
set_param([model '/Rule_start_running_busy_true_Const'], 'OutDataTypeStr', 'boolean');
set_param([model '/Rule_start_running_busy_true_Const'], 'Position', [560 920 660 950]);
add_block('simulink/Sources/Constant', [model '/Default_busy_0_0']);
set_param([model '/Default_busy_0_0'], 'Value', 'false');
set_param([model '/Default_busy_0_0'], 'OutDataTypeStr', 'boolean');
set_param([model '/Default_busy_0_0'], 'Position', [560 1120 660 1150]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_start_running_busy_Switch']);
set_param([model '/Rule_start_running_busy_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_start_running_busy_Switch'], 'Position', [720 360 800 405]);
add_line(model, 'Rule_start_running_busy_true_Const/1', 'Rule_start_running_busy_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_start_running_Compare/1', 'Rule_start_running_busy_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_busy_0_0/1', 'Rule_start_running_busy_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_start_running_busy_Switch/1', 'Out_busy/1', 'autorouting', 'on');
add_block('simulink/Sources/Constant', [model '/Rule_start_running_complete_false_Const']);
set_param([model '/Rule_start_running_complete_false_Const'], 'Value', 'false');
set_param([model '/Rule_start_running_complete_false_Const'], 'OutDataTypeStr', 'boolean');
set_param([model '/Rule_start_running_complete_false_Const'], 'Position', [560 955 660 985]);
add_block('simulink/Sources/Constant', [model '/Default_complete_0_1']);
set_param([model '/Default_complete_0_1'], 'Value', 'false');
set_param([model '/Default_complete_0_1'], 'OutDataTypeStr', 'boolean');
set_param([model '/Default_complete_0_1'], 'Position', [560 1155 660 1185]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_start_running_complete_Switch']);
set_param([model '/Rule_start_running_complete_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_start_running_complete_Switch'], 'Position', [720 386 800 431]);
add_line(model, 'Rule_start_running_complete_false_Const/1', 'Rule_start_running_complete_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_start_running_Compare/1', 'Rule_start_running_complete_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_complete_0_1/1', 'Rule_start_running_complete_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_start_running_complete_Switch/1', 'Out_complete/1', 'autorouting', 'on');
% priority 10 start_running: owner ToyStateController from IDLE when startCommand == true then {'state': 'RUNNING', 'busy': 'true', 'complete': 'false'} scenarios ['full_cycle']
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_finish_done_Compare']);
set_param([model '/Rule_finish_done_Compare'], 'relop', '==');
set_param([model '/Rule_finish_done_Compare'], 'const', 'true');
set_param([model '/Rule_finish_done_Compare'], 'Position', [420 500 540 545]);
add_line(model, 'In_finishCommand/1', 'Rule_finish_done_Compare/1', 'autorouting', 'on');
% state handoff finish_done: next state DONE
add_block('simulink/Sources/Constant', [model '/Rule_finish_done_busy_false_Const']);
set_param([model '/Rule_finish_done_busy_false_Const'], 'Value', 'false');
set_param([model '/Rule_finish_done_busy_false_Const'], 'OutDataTypeStr', 'boolean');
set_param([model '/Rule_finish_done_busy_false_Const'], 'Position', [560 1000 660 1030]);
add_block('simulink/Sources/Constant', [model '/Default_busy_1_0']);
set_param([model '/Default_busy_1_0'], 'Value', 'false');
set_param([model '/Default_busy_1_0'], 'OutDataTypeStr', 'boolean');
set_param([model '/Default_busy_1_0'], 'Position', [560 1200 660 1230]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_finish_done_busy_Switch']);
set_param([model '/Rule_finish_done_busy_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_finish_done_busy_Switch'], 'Position', [720 500 800 545]);
add_line(model, 'Rule_finish_done_busy_false_Const/1', 'Rule_finish_done_busy_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_finish_done_Compare/1', 'Rule_finish_done_busy_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_busy_1_0/1', 'Rule_finish_done_busy_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_finish_done_busy_Switch/1', 'Out_busy/1', 'autorouting', 'on');
add_block('simulink/Sources/Constant', [model '/Rule_finish_done_complete_true_Const']);
set_param([model '/Rule_finish_done_complete_true_Const'], 'Value', 'true');
set_param([model '/Rule_finish_done_complete_true_Const'], 'OutDataTypeStr', 'boolean');
set_param([model '/Rule_finish_done_complete_true_Const'], 'Position', [560 1035 660 1065]);
add_block('simulink/Sources/Constant', [model '/Default_complete_1_1']);
set_param([model '/Default_complete_1_1'], 'Value', 'false');
set_param([model '/Default_complete_1_1'], 'OutDataTypeStr', 'boolean');
set_param([model '/Default_complete_1_1'], 'Position', [560 1235 660 1265]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_finish_done_complete_Switch']);
set_param([model '/Rule_finish_done_complete_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_finish_done_complete_Switch'], 'Position', [720 526 800 571]);
add_line(model, 'Rule_finish_done_complete_true_Const/1', 'Rule_finish_done_complete_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_finish_done_Compare/1', 'Rule_finish_done_complete_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_complete_1_1/1', 'Rule_finish_done_complete_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_finish_done_complete_Switch/1', 'Out_complete/1', 'autorouting', 'on');
% priority 20 finish_done: owner ToyStateController from RUNNING when finishCommand == true then {'state': 'DONE', 'busy': 'false', 'complete': 'true'} scenarios ['full_cycle']
add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_reset_idle_Compare']);
set_param([model '/Rule_reset_idle_Compare'], 'relop', '==');
set_param([model '/Rule_reset_idle_Compare'], 'const', 'true');
set_param([model '/Rule_reset_idle_Compare'], 'Position', [420 640 540 685]);
add_line(model, 'In_resetCommand/1', 'Rule_reset_idle_Compare/1', 'autorouting', 'on');
% state handoff reset_idle: next state IDLE
add_block('simulink/Sources/Constant', [model '/Rule_reset_idle_busy_false_Const']);
set_param([model '/Rule_reset_idle_busy_false_Const'], 'Value', 'false');
set_param([model '/Rule_reset_idle_busy_false_Const'], 'OutDataTypeStr', 'boolean');
set_param([model '/Rule_reset_idle_busy_false_Const'], 'Position', [560 1080 660 1110]);
add_block('simulink/Sources/Constant', [model '/Default_busy_2_0']);
set_param([model '/Default_busy_2_0'], 'Value', 'false');
set_param([model '/Default_busy_2_0'], 'OutDataTypeStr', 'boolean');
set_param([model '/Default_busy_2_0'], 'Position', [560 1280 660 1310]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_reset_idle_busy_Switch']);
set_param([model '/Rule_reset_idle_busy_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_reset_idle_busy_Switch'], 'Position', [720 640 800 685]);
add_line(model, 'Rule_reset_idle_busy_false_Const/1', 'Rule_reset_idle_busy_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_reset_idle_Compare/1', 'Rule_reset_idle_busy_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_busy_2_0/1', 'Rule_reset_idle_busy_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_reset_idle_busy_Switch/1', 'Out_busy/1', 'autorouting', 'on');
add_block('simulink/Sources/Constant', [model '/Rule_reset_idle_complete_false_Const']);
set_param([model '/Rule_reset_idle_complete_false_Const'], 'Value', 'false');
set_param([model '/Rule_reset_idle_complete_false_Const'], 'OutDataTypeStr', 'boolean');
set_param([model '/Rule_reset_idle_complete_false_Const'], 'Position', [560 1115 660 1145]);
add_block('simulink/Sources/Constant', [model '/Default_complete_2_1']);
set_param([model '/Default_complete_2_1'], 'Value', 'false');
set_param([model '/Default_complete_2_1'], 'OutDataTypeStr', 'boolean');
set_param([model '/Default_complete_2_1'], 'Position', [560 1315 660 1345]);
add_block('simulink/Signal Routing/Switch', [model '/Rule_reset_idle_complete_Switch']);
set_param([model '/Rule_reset_idle_complete_Switch'], 'Threshold', '0.5');
set_param([model '/Rule_reset_idle_complete_Switch'], 'Position', [720 666 800 711]);
add_line(model, 'Rule_reset_idle_complete_false_Const/1', 'Rule_reset_idle_complete_Switch/1', 'autorouting', 'on');
add_line(model, 'Rule_reset_idle_Compare/1', 'Rule_reset_idle_complete_Switch/2', 'autorouting', 'on');
add_line(model, 'Default_complete_2_1/1', 'Rule_reset_idle_complete_Switch/3', 'autorouting', 'on');
add_line(model, 'Rule_reset_idle_complete_Switch/1', 'Out_complete/1', 'autorouting', 'on');
% priority 30 reset_idle: owner ToyStateController from DONE when resetCommand == true then {'state': 'IDLE', 'busy': 'false', 'complete': 'false'} scenarios ['full_cycle']
% Functional decomposition summary:
% function ToyStateController: owns ['IDLE', 'RUNNING', 'DONE', 'busy', 'complete']; inputs ['startCommand', 'finishCommand', 'resetCommand']; outputs ['state', 'busy', 'complete']
% Flow handoff summary:
% flow ToyCommandSource.startCommand -> ToyStateController.startCommand: start request
% flow ToyCommandSource.finishCommand -> ToyStateController.finishCommand: finish request
% flow ToyCommandSource.resetCommand -> ToyStateController.resetCommand: reset request
% flow ToyStateController.busy -> ToyStateMachine.busy: busy command
% flow ToyStateController.complete -> ToyStateMachine.complete: completion command
% flow ToyStateMachine.busy -> ScenarioReport.observedBehavior: reported busy output
% flow ToyStateMachine.complete -> ScenarioReport.observedBehavior: reported complete output
% State transition summary:
% IDLE -> RUNNING when startCommand == true
% RUNNING -> DONE when finishCommand == true
% DONE -> IDLE when resetCommand == true
save_system(model);
