/**
 * Visual Blocks Language
 *
 * Copyright 2012 Google Inc.
 * http://blockly.googlecode.com/
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

'use strict';

goog.provide('Blockly.Python.variables');

goog.require('Blockly.Python');

Blockly.Python['panya_pin_digital'] = function(block) {
  var value_pin = Blockly.Python.valueToCode(block, 'pin', Blockly.Python.ORDER_NONE) || '0';
  var dropdown_state = block.getFieldValue('logicstate');
  var code = 'panya.PanyaPin('+"\'"+value_pin+''+"\'"+"\,"+"\'"+dropdown_state+""+"\'"+"\,"+"None"+")\n";
  return code;
};

Blockly.Python['panya_motors'] = function(block) {
  var dropdown_direction = block.getFieldValue('DIRECTION');
  var value_duration = Blockly.Python.valueToCode(block, 'DURATION', Blockly.Python.ORDER_NONE) || '0';
  var code = 'panya.PanyaMotors('+"\'"+dropdown_direction+''+"\'"+"\,"+"\'"+value_duration+""+"\')\n";
  return code;
};

Blockly.Python['panya_lcd_print'] = function(block) {
  var text_lcdprint = block.getFieldValue('LCDPRINT');
  var code = 'panya.PanyaLCD('+"\'"+text_lcdprint+"\'"+"\,"+"None"+")\n";
  return code;
};

Blockly.Python['panya_lcd_rgb'] = function(block) {
  var colour_lcdcolour = block.getFieldValue('LCDCOLOUR');
  var code = 'panya.PanyaLCD('+"None"+"\,"+"\'"+colour_lcdcolour+"\')\n";
  return code;
};

Blockly.Python['panya_reset'] = function(block) {
  // Stop the panyabot. Change the value of code to the appropriate python function
  var code = 'panya.PanyaReset()\n';
  return code;
};
