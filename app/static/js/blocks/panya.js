/**
 * Visual Blocks Editor
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

goog.provide('Blockly.Blocks.variables');

goog.require('Blockly.Blocks');

Blockly.Blocks['panya_pin_digital'] = {
  init: function() {
    this.appendValueInput("pin")
        .setCheck("Number")
        .appendTitle("switch pin")
        .appendField("");
    this.appendDummyInput()
        .appendField(new Blockly.FieldDropdown([["ON", "1"], ["OFF", "0"]]), "logicstate");
    this.setInputsInline(true);
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setColour(160);
    this.setTooltip('Turn on or off the chosen pin');
    this.setHelpUrl('http://www.example.com/');
  }
};

Blockly.Blocks['panya_motors'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Move webot")
        .appendField(new Blockly.FieldDropdown([["Forward", "F"], ["Backward", "B"], ["Left", "L"], ["Right", "R"]]), "DIRECTION");
    this.appendValueInput("DURATION")
        .setCheck("Number")
        .appendField("for");
    this.appendDummyInput()
        .appendField("seconds");
    this.setInputsInline(true);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(330);
    this.setTooltip('');
    this.setHelpUrl('http://www.example.com/');
  }
};

Blockly.Blocks['panya_lcd_print'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Print")
        .appendField(new Blockly.FieldTextInput("hello"), "LCDPRINT")
        .appendField("on LCD");
    this.setInputsInline(true);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(330);
    this.setTooltip('');
    this.setHelpUrl('http://www.example.com/');
  }
};

Blockly.Blocks['panya_lcd_rgb'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Set LCD Color to")
        .appendField(new Blockly.FieldColour("#ff0000"), "LCDCOLOUR");
    this.setInputsInline(true);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(330);
    this.setTooltip('');
    this.setHelpUrl('http://www.example.com/');
  }
};

Blockly.Blocks['panya_reset'] = {
  init: function() {
    this.appendDummyInput()
        .appendTitle("Stop")
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip('Stop the PanyaBot');
    this.setHelpUrl('http://www.example.com/');
    this.setColour(160);
  }
};
