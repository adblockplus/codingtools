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

/* eslint-env commonjs */

"use strict";

module.exports = {
  extends: "eslint:recommended",
  parserOptions: {
    ecmaVersion: 2017
  },
  env: {
    es6: true
  },
  rules: {
    "array-bracket-spacing": "error",
    "arrow-spacing": "error",
    "block-scoped-var": "error",
    "block-spacing": "error",
    "brace-style": ["error", "allman", {allowSingleLine: true}],
    "camelcase": ["error", {properties: "never"}],
    "comma-dangle": "error",
    "comma-spacing": "error",
    "comma-style": "error",
    "computed-property-spacing": "error",
    "eol-last": "error",
    "func-call-spacing": "error",
    "indent-legacy": ["error", 2, {SwitchCase: 1, ArrayExpression: "first"}],
    "key-spacing": "error",
    "keyword-spacing": "error",
    "linebreak-style": "error",
    "lines-around-directive": "error",
    "max-len": ["error", 80, {ignoreUrls: true, ignoreRegExpLiterals: true}],
    "new-parens": "error",
    "no-array-constructor": "error",
    "no-caller": "error",
    "no-case-declarations": "off",
    "no-catch-shadow": "error",
    "no-cond-assign": "off",
    "no-console": ["error", {allow: ["warn", "error", "trace"]}],
    "no-constant-condition": ["error", {checkLoops: false}],
    "no-control-regex": "off",
    "no-else-return": "error",
    "no-empty": "off",
    "no-eval": "error",
    "no-extra-bind": "error",
    "no-extra-label": "error",
    "no-implied-eval": "error",
    "no-labels": ["error", {allowLoop: true}],
    "no-lone-blocks": "error",
    "no-lonely-if": "error",
    "no-multi-spaces": ["error", {ignoreEOLComments: true}],
    "no-new-func": "error",
    "no-new-object": "error",
    "no-proto": "error",
    "no-self-compare": "error",
    "no-shadow": "error",
    "no-trailing-spaces": "error",
    "no-unneeded-ternary": "error",
    "no-unused-vars": ["error", {vars: "local", args: "none"}],
    "no-useless-computed-key": "error",
    "no-useless-concat": "error",
    "no-useless-escape": "error",
    "no-useless-return": "error",
    "no-var": "error",
    "no-warning-comments": "error",
    "no-whitespace-before-property": "error",
    "no-with": "error",
    "object-curly-spacing": "error",
    "object-shorthand": ["error", "always", {
      avoidExplicitReturnArrows: true
    }],
    "one-var": ["error", "never"],
    "operator-assignment": "error",
    "operator-linebreak": ["error", "after"],
    "padded-blocks": ["error", "never"],
    "prefer-arrow-callback": "error",
    "prefer-destructuring": ["error", {array: false}],
    "prefer-numeric-literals": "error",
    "prefer-rest-params": "error",
    "prefer-spread": "error",
    "quote-props": ["error", "consistent-as-needed"],
    "quotes": ["error", "double", {avoidEscape: true}],
    "radix": "error",
    "rest-spread-spacing": "error",
    "semi": "error",
    "semi-spacing": "error",
    "space-before-function-paren": ["error", "never"],
    "space-in-parens": "error",
    "space-infix-ops": "error",
    "space-unary-ops": "error",
    "spaced-comment": "error",
    "strict": ["error", "global"],
    "valid-jsdoc": ["error", {
      requireParamDescription: false,
      requireReturn: false,
      requireReturnDescription: false
    }],
    "yield-star-spacing": "error",
    "yoda": "error"
  }
};
