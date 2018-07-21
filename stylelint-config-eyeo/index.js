/*
 * This file is part of Adblock Plus <https://adblockplus.org/>,
 * Copyright (C) 2006-present eyeo GmbH
 *
 * Adblock Plus is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3 as
 * published by the Free Software Foundation.
 *
 * Adblock Plus is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Adblock Plus.  If not, see <http://www.gnu.org/licenses/>.
 */

"use strict";

module.exports = {
  extends: "stylelint-config-recommended",
  plugins: [
    "stylelint-order"
  ],
  rules: {
    // Opening braces go on their own line
    "block-opening-brace-newline-before": "always-multi-line",
    "block-opening-brace-newline-after": "always-multi-line",
    "block-closing-brace-newline-before": "always-multi-line",
    "block-closing-brace-newline-after": "always",
    "block-closing-brace-empty-line-before": "never",

    // Use a space between the last selector and the declaration block
    "block-opening-brace-space-before": "always-single-line",

    // Use a space after a property name’s colon
    "declaration-colon-space-after": "always",

    // Selectors and declarations should be on their own line
    "selector-list-comma-newline-after": "always",
    "declaration-block-semicolon-newline-after": "always-multi-line",

    // Separate rules by an empty line
    "rule-empty-line-before": ["always", {
      "ignore": ["after-comment"],
      "except": ["first-nested"]
    }],

    // Use double over single quotation marks
    "string-quotes": "double",

    // CSS color values should be specified in hexadecimal where possible
    "color-named": "never",

    // Use short hexadecimal notation where possible
    "color-hex-length": "short",

    // Don't omit the optional leading 0 for decimal numbers
    "number-leading-zero": "always",
    "number-no-trailing-zeros": true,

    // Two spaces per logic level
    "indentation": 2,

    // Line length should be 80 characters or less
    "max-line-length": 80,

    // Avoid qualifying ID and class names with type selectors
    "selector-no-qualifying-type": [true, {
      "ignore": ["attribute"]
    }],

    // Font weight values should be specified in relative or numerical notation
    "font-weight-notation": ["numeric", {
      "ignore": ["relative"]
    }],

    // CSS rule declaration order should follow the WordPress CSS
    // Coding Standards
    "order/properties-order": require("./css-properties-order")
  }
};
