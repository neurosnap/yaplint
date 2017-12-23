# yaplint (Yet Another Python Linter)

## Install

```bash
pip install yaplint
```

## Install rules

```bash
pip install yaplint_require_spaces
```

## Usage

```python
from yaplint import linter
from yaplint_require_spaces import RequireSpaces

rules = [RequireSpaces({}, None)]
src = 'test = 1\n'
out = linter(rules, src)
print(out)
```
