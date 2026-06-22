model ToyEnergyBufferMode
  // Generated from Mermaid-like MBD markup.
  // Readable Modelica handoff artifact; not a complete physical model.
  input Boolean externalPowerAvailable(start=true);
  input Boolean emptyDetected(start=false);
  output Boolean supplyEnabled(start=false);
  output Boolean chargeIndicator(start=true);
  discrete Integer state;
equation
  // State placeholders generated from markup:
  // 0: CHARGE
  // 1: DISCHARGE
  // 2: EMPTY
  // Functional decomposition handoff summary:
  // function ToyEnergyBufferModeController: owns CHARGE, DISCHARGE, EMPTY, supplyEnabled, chargeIndicator trace EBUF-001, EBUF-002, EBUF-003, EBUF-004, EBUF-005, EBUF-006 scenarios source_loss_recovery
  // Control rule handoff summary:
  // priority 10 power_removed_discharge: owner ToyEnergyBufferModeController from CHARGE when externalPowerAvailable == false and emptyDetected == false then state=DISCHARGE, supplyEnabled=true, chargeIndicator=false trace EBUF-001, EBUF-006 scenarios source_loss_recovery
  // priority 20 discharge_empty: owner ToyEnergyBufferModeController from DISCHARGE when emptyDetected == true then state=EMPTY, supplyEnabled=false, chargeIndicator=false trace EBUF-002, EBUF-006 scenarios source_loss_recovery
  // priority 30 empty_reconnect_charge: owner ToyEnergyBufferModeController from EMPTY when externalPowerAvailable == true then state=CHARGE, supplyEnabled=false, chargeIndicator=true trace EBUF-003, EBUF-006 scenarios source_loss_recovery
  // priority 40 discharge_reconnect_charge: owner ToyEnergyBufferModeController from DISCHARGE when externalPowerAvailable == true then state=CHARGE, supplyEnabled=false, chargeIndicator=true trace EBUF-004, EBUF-006 scenarios source_loss_recovery
end ToyEnergyBufferMode;
