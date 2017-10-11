# flake8-eyeo

A [flake8](https://flake8.readthedocs.io) extension that checks for compliance
with the
[Adblock Plus coding style guide](https://adblockplus.org/coding-style#python)
which is used for all eyeo projects, and some bad practices which flake8 doesn't
handle by default.


## Installation

Run `python setup.py install`.


## Usage

Just run `flake8` (you have to install it seperately) on your source files.
After installation the `flake8-eyeo` extension is active by default.


## Warnings

### Readability and consistency

* `A101`: Loop over a tuple or set literal; use lists for data that have order
* `A102`: Membership check on a tuple or list literal; use a set here
* `A103`: Yoda condition
* `A104`: `map()` or `filter()` called with lambda function
* `A105`: Type called with literal or comprehension where a
          literal/comprehension of that type can be used directly
* `A106`: Use augment assignment
* `A107`: `%` operator used for string formatting; this mechanism
          has been superseded by the string's `format()` method
* `A108`: `+` operator to concatenate more than two strings
* `A110`: Write single-line string literals as represented by `repr()`
* `A111`: Redundant parantheses around if or while condition
* `A112`: Use `from __future__ import unicode_literals` instead of
          prefixing literals with "u"


### Redundancy and complexity

* `A201`: Redundant or superfluos `global` or `nonlocal` declaration
* `A202`: Dead code after block is left
* `A303`: Unused expression
* `A204`: Redundant or superfluos pass statement
* `A205`: Superfluos empty block
* `A206`: Extraneous `else` statement after block is left
* `A207`: Duplicate key in dict or set


### Error-prone practices

* `A301`: Discouraged APIs
* `A302`: Redefinition of built-in name
* `A303`: Non-default source file encoding
