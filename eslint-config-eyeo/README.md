# eslint-config-eyeo

An [ESLint](http://eslint.org) configuration that checks for compliance with the
[Adblock Plus coding style guide](https://adblockplus.org/coding-style#javascript)
which is used for all eyeo projects.

## Installation

    npm install -g eslint eslint-config-eyeo

This command requires administrator privileges so you might need to use `sudo`.

## Usage

To lint a JavaScript file using ESLint you run the `eslint` command with the
file as an argument. For example:

    eslint some-file.js

For advanced usage see `eslint --help`.

In order to use eslint-config-eyeo your project's ESLint configuration
should extend from it. A minimal example looks like this:

    {
      "extends": "eslint-config-eyeo",
      "root": true
    }

For projects without an ESLint configuration you can create your own
personal configuration in `~/.eslintrc.json`, but take care to remove
the `"root": true` section from the above example.
