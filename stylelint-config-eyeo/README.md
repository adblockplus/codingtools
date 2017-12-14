# stylelint-config-eyeo

A [Stylelint](https://stylelint.io) configuration that checks for compliance
with the [Adblock Plus coding style guide](https://adblockplus.org/coding-style#html-css)
which is used for all eyeo projects.

## Installation

    npm install -g stylelint

This command requires administrator privileges so you might need to use `sudo`.

Next, either install stylelint-config-eyeo within your project. For example:

    npm install --save-dev stylelint-config-eyeo

Or, install stylelint-config-eyeo globally. For example:

    npm install -g stylelint-config-eyeo

## Usage

To lint a CSS (or CSS-like, e.g. SCSS, SugarCSS, Less) file using Stylelint
you run the `stylelint` command with the file as an argument. For example:

    stylelint example.css

For advanced usage see `stylelint --help`.

In order to use stylelint-config-eyeo, your project's Stylelint configuration
should extend from it. A minimal example looks like this:

    {
      "extends": "stylelint-config-eyeo"
    }

If you've globally installed stylelint-config-eyeo using the `-g` flag, then
you'll need to use the absolute path to stylelint-config-eyeo in your config.

    {
      "extends": "/absolute/path/to/stylelint-config-eyeo"
    }

For projects without a Stylelint configuration you can create your own
personal configuration in `~/.stylelintrc.json`.
