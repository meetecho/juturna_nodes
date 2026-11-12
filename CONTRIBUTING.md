# Contributing to `juturna-nodes`

Thanks for your interest in contributing! Whether it's reporting a bug,
improving documentation, or submitting a pull request — you're welcome here.

## Code of Conduct

We expect everyone to be respectful and constructive. If you're a jerk, your PR
will be closed. Simple as that.

See our [CODE OF CONDUCT](CODE_OF_CONDUCT.md) for further details

## How to Contribute

1. **Fork the repository**
2. **Create a branch** for your changes:
   `git checkout -b feature/your-feature-name`
3. **Install dependencies**:
   See [Setup for Local Development](#setup-for-local-development)
4. **Write your code**
   Keep it clean, small, and focused.
5. **Open a pull request**
   Include a clear description of what you did and why.

## PR Guidelines
* Keep PRs focused and minimal.
* Explain why you're making the change.
* Avoid unrelated changes in the same PR.
* If you're not sure, open an issue before coding.

## Contributing a Node

Most contributions to this repository are new nodes, or fixes to existing ones.
Nodes in this repository are part of the `juturna.nodes` namespace, and are
used in a pipeline by class name (`"type": "AudioRtp"`).

> If you are writing nodes for your own project or organisation, you do not
> need to contribute them here: package them under
> `juturna.contrib.<author>.nodes` in your own repository (`juturna stub` sets
> up that layout for you).

### Node layout

Every node lives in its own underscore-prefixed folder, and the module has the
same name as the folder, without the underscore:

```
src/juturna/nodes/
  __init__.py                 # node registry
  _my_node/
    my_node.py                # node class
    config.toml               # default arguments
    README.md                 # node documentation
    *.template                # optional, files compiled at runtime
```

The simplest way to start is to copy an existing node with a similar role
(`_passthrough_identity` is a minimal one), and rename it.

### Node class

Nodes subclass `juturna.components.Node`, typed with their input and output
payloads:

```python
"""
MyNode

@ Author: Your Name
@ Email: your@email.com

One-line description of what the node does.
"""

from juturna.components import Message
from juturna.components import Node

from juturna.payloads import ObjectPayload


class MyNode(Node[ObjectPayload, ObjectPayload]):
    """Node implementation class"""

    def __init__(self, threshold: float, **kwargs):
        """
        Parameters
        ----------
        threshold : float
            What the threshold is used for.
        kwargs : dict
            Superclass arguments.

        """
        super().__init__(**kwargs)

        self._threshold = threshold

    def update(self, message: Message[ObjectPayload], **kwargs):
        """Receive a message, transmit a message"""
        to_send = Message[ObjectPayload](
            creator=self.name,
            version=message.version,
            payload=message.payload,
            timers_from=message,
        )

        self.transmit(to_send)
```

Keep in mind that:

- `__init__` must accept `**kwargs` and forward them to `super().__init__`;
- if you override `start()` or `stop()`, call `super().start()` and
  `super().stop()`;
- long-running work (servers, sockets, polling loops) goes in workers created
  with `self._transport.spawn(...)`, not with `threading` directly, and must be
  stopped in `stop()` or `destroy()`;
- use `self.logger` for logging;
- open resources (connections, servers, models) in `warmup()`, not in
  `__init__`, and release them in `destroy()`.

### Node configuration

`config.toml` declares the default value of **every** argument the node class
accepts:

```toml
[arguments]
threshold = 0.5

[meta]
```

Only the arguments listed in `[arguments]` are passed to the node: any key in
a pipeline configuration that is not declared here is silently ignored. Values
can be read from the environment, using the `$JT_ENV_` prefix in a pipeline
configuration (`"uri": "$JT_ENV_MONGO_URI"`).

### Node registration

Add the node to the `_AVAILABLE_PLUGINS` mapping in
`src/juturna/nodes/__init__.py`, in the section matching its role (source,
processing, or sink):

```python
_AVAILABLE_PLUGINS: dict[str, str] = {
    # ...
    'MyNode': '._my_node.my_node',
}
```

- The key must be **exactly** the class name.
- The module path is relative, and starts with a dot.

Nodes are imported lazily, only when they are used, so a node with missing
optional dependencies does not break the others.

### Node dependencies

Do not add a `requirements.txt` file to the node folder: dependencies are
declared in `pyproject.toml`.

- **Lightweight, pure-Python packages** (HTTP clients, websockets, database
  drivers, ...) go in the main `dependencies` list.
- **Heavy packages** (machine learning frameworks, models, media libraries)
  go in an optional extra. Use an existing extra when the node fits one
  (`av`, `warp`, `audio-ml`, `vision`), otherwise add a new one, and include
  it in `all`.

Always specify a minimum version you tested the node with.

### Node documentation

Each node folder contains a `README.md` file describing:

- what the node does, and its role in a pipeline (source, processing, sink);
- the input and output payload types;
- every argument in `config.toml`, with its meaning and default value;
- the extra required to use it, if any;
- an example pipeline node entry.

### Testing a node

Install the repository in editable mode, with the extras the node needs, and
check that the node can be imported from the namespace:

```bash
pip install -e ".[all,dev_full]"
python -c "from juturna.nodes import MyNode"
```

Run the test suite, which also checks that every registered node has a valid
`config.toml` matching its constructor, and a `README.md`:

```bash
pytest tests/
```

Tests of nodes whose extra is not installed are skipped. New nodes should come
with their own tests in `tests/`, whenever they can run without external
services.

Then run it in a small pipeline, using `juturna validate` and `juturna launch`
on a pipeline file that includes the node:

```json
{ "name": "my_node", "type": "MyNode", "configuration": { "threshold": 0.7 } }
```

### Node checklist

Before opening a pull request for a node, make sure that:

- [ ] the node folder and module follow the `_<name>/<name>.py` layout;
- [ ] `config.toml` declares every constructor argument;
- [ ] the node is registered in `_AVAILABLE_PLUGINS` with its class name;
- [ ] dependencies are declared in `pyproject.toml`;
- [ ] the node `README.md` is complete;
- [ ] the node is listed in the main [README](README.md#available-nodes);
- [ ] the node has a documentation page in `docs/source/nodes/`, listed in the
  toctree of its role and in `overview.rst`;
- [ ] `ruff check` and `ruff format --check` pass.

## Code Quality

This project enforces code quality standards through automated checks:
1. **Conventional Commits** - Consistent and meaningful commit messages
2. **Ruff** - Fast Python linter and formatter for code quality
3. **Pre-commit Hooks** - Standard checks for common issues
4. **Bandit** - Security vulnerability scanning (optional, manual)

All checks run automatically both locally (via pre-commit hooks) and in CI (via
GitHub Actions).

## Setup for Local Development

### 1. Install Development Dependencies

Install the project with full development dependencies:

```bash
# If using pip
pip install -U -e ".[dev_full]"

# Or if using a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -U -e ".[dev_full]"
```

This will install `juturna-nodes` including the following optional groups:

- `doc`: contains `sphinx` and all its required packages for documentation
- `dev`: contains `pre-commit`, `bandit`, and `conventional-pre-commit`
- `lint`: contains `ruff`
- `test`: contains `pytest`

If you are planning to work on a feature that does not come shipped with the
default `juturna-nodes` installation, make sure you install the relevant group.
If you just want a full installation, just run:

```bash
pip install -U -e ".[all,dev_full]"
```

### 2. Install Pre-commit Hooks

After installing dependencies, activate **both** types of hooks:

```bash
# Install BOTH hooks with a single command
pre-commit install && pre-commit install --hook-type commit-msg
```

You should see:
```
pre-commit installed at .git/hooks/pre-commit
pre-commit installed at .git/hooks/commit-msg
```

**Why two commands?**

Pre-commit uses two different Git hooks that run at different stages:

| Hook Type | When It Runs | What It Checks | Install Command |
|-----------|--------------|----------------|-----------------|
| `pre-commit` | **Before** you write the commit message | Code quality (Ruff linting/formatting) | `pre-commit install` |
| `commit-msg` | **After** you write the commit message | Commit message format (Conventional Commits) | `pre-commit install --hook-type commit-msg` |

**Commit Flow:**
```
git add file.py
git commit -m "feat: add feature"
    ↓
1. pre-commit hooks run:
   - Standard checks
    - Check merge conflicts
    - Validate YAML/JSON
    - Fix trailing whitespace
    - Fix end-of-file issues
    - Check for private keys
   - Ruff linter
    - Checks/formats code
    - Auto-fixes issues
   - Ruff formatter:
    - Formats code consistently
    ↓
2. You write or use the commit message
    ↓
3. commit-msg hook runs:
   - Validates message format
    ↓
4. Commit is created (if all checks pass)
```

You need **both** installed for complete validation!

## Automated Checks

### 1. Standard Pre-commit Hooks

The following checks run automatically on every commit:

| Hook | Description | Auto-fix |
|------|-------------|----------|
| **check-merge-conflict** | Detects merge conflict markers | ❌ No |
| **check-yaml** | Validates YAML file syntax | ❌ No |
| **check-json** | Validates JSON file syntax | ❌ No |
| **end-of-file-fixer** | Ensures files end with a newline | ✅ Yes |
| **trailing-whitespace** | Removes trailing whitespace | ✅ Yes |
| **detect-private-key** | Prevents committing private keys | ❌ No |

These checks help maintain code quality and prevent common mistakes.

### 2. Ruff - Code Linting and Formatting

Ruff enforces Python code quality standards:

**What Ruff Checks:**
- **Code quality**: pycodestyle (E, W), pyflakes (F), flake8-bugbear (B)
- **Import sorting**: isort-compatible import ordering (I)
- **Naming conventions**: PEP 8 naming standards (N)
- **Modern Python**: pyupgrade rules for Python 3.12+ (UP)
- **Code simplification**: flake8-simplify rules (SIM)
- **Path handling**: flake8-use-pathlib rules (PTH)

**What Ruff Auto-fixes:**
- Import sorting and organization
- Unused imports removal
- Code formatting (spacing, quotes, line breaks)
- Outdated syntax (e.g., `type()` → `isinstance()`)
- Unnecessary comprehensions

### 3. Conventional-pre-commit - Commit Linting

Commit message validator runs last
- Checks if your commit message follows Conventional Commits

## Commit Message Guidelines
Use clear, conventional commit messages:

### Basic Structure

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Required Format

- **type**: Must be one of the allowed types (see below)
- **scope** (optional): A noun describing the section of the codebase
- **subject**: Short description (imperative mood, no period at the end)

### Allowed Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(auth): add OAuth2 support` |
| `fix` | Bug fix | `fix(parser): handle empty strings` |
| `docs` | Documentation changes | `docs: update installation guide` |
| `style` | Code style changes (formatting, etc.) | `style: fix indentation` |
| `refactor` | Code refactoring | `refactor(api): simplify error handling` |
| `perf` | Performance improvements | `perf(db): add query caching` |
| `test` | Adding/updating tests | `test: add unit tests for parser` |
| `build` | Build system changes | `build: update dependencies` |
| `ci` | CI/CD configuration changes | `ci: add deployment workflow` |
| `chore` | Other changes (maintenance, etc.) | `chore: update .gitignore` |
| `revert` | Revert previous commit | `revert: revert "feat: add feature X"` |

### Breaking Changes

To indicate a breaking change, use one of these methods:

**Method 1: Add `!` after type/scope**
```bash
feat(api)!: change response format from XML to JSON
```

**Method 2: Use `BREAKING CHANGE` footer**
```bash
feat: migrate to new config system

BREAKING CHANGE: config.ini is no longer supported, use config.yaml instead
```

Both methods will:
- Trigger a major version bump (or minor if pre-1.0.0)
- Add the change to the "BREAKING CHANGES" section in the changelog

## Examples

### Good Commit Messages ✅

```bash
# Simple feature
git commit -m "feat: add user authentication"

# Feature with scope
git commit -m "feat(auth): add OAuth2 provider"

# Bug fix with scope
git commit -m "fix(parser): handle unicode characters correctly"

# Documentation update
git commit -m "docs: add API usage examples"

# Breaking change with !
git commit -m "feat(api)!: change endpoint response format"

# Multi-line commit with body
git commit -m "feat(database): add connection pooling

Implement connection pooling to improve performance
under high load. Pool size is configurable via environment
variable DB_POOL_SIZE."
```

### Bad Commit Messages ❌

```bash
# Missing type
git commit -m "add new feature"

# Invalid type
git commit -m "added: new feature"

# Capitalized subject
git commit -m "feat: Add new feature"

# Period at the end
git commit -m "feat: add new feature."

# Not imperative mood
git commit -m "feat: added new feature"
```

## Bypassing Hooks

### Temporary Bypass (Not Recommended)

If you need to bypass hooks temporarily:

```bash
# Skip all pre-commit hooks (but not commit-msg hook)
git commit --no-verify -m "your message"

# Skip specific hooks only
SKIP=ruff,ruff-format git commit -m "your message"
```

**Warning:** Commits that bypass local validation will still be rejected by CI when you open a PR.

### Disable Hooks Completely (Not Recommended)

If you want to work without any hooks temporarily:

```bash
# Uninstall all hooks
pre-commit uninstall
pre-commit uninstall --hook-type commit-msg

# To re-enable later
pre-commit install && pre-commit install --hook-type commit-msg
```

**Note:** This disables all automated checks. Use this only if you have a specific reason and remember to re-enable the hooks before committing.

## CI Validation

Even if you bypass local validation, all commits in a Pull Request are validated by GitHub Actions:

1. **Commit Lint** - Validates all commit messages in the PR
2. **Ruff Check** - Ensures code passes linting rules
3. **Ruff Format** - Ensures code is properly formatted
4. **Unit Tests** - Runs the test suite on every supported Python version

PRs that fail any check cannot be merged.

## Bandit - Optional Security Scanning (Manual)

Bandit scans Python code for common security vulnerabilities.
It's configured as a **manual** hook, meaning it doesn't run automatically on every commit.

**What Bandit Checks:**
- Hard-coded passwords and secrets
- Use of insecure functions (e.g., `eval()`, `exec()`)
- Insecure cryptographic practices
- File permission issues
- And many other security issues

**Running Bandit Manually:**

```bash
# Run bandit using pre-commit (recommended)
pre-commit run --hook-stage manual bandit --all-files

# Run bandit on specific files
pre-commit run --hook-stage manual bandit --files path/to/file.py
```

Bandit is configured via the `.bandit` file in the project root,
and by default it will scan only the project code, not dependencies

**When You Should Run Bandit:**
- Before opening a Pull Request

## Quick Reference

### Commit Format
```
Types:  feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
Format: <type>(<scope>): <subject>

Breaking: Add ! after type: feat!: breaking change
          Or add footer: BREAKING CHANGE: description

Example: feat(auth): add two-factor authentication
```

### Common Commands
```bash
# Setup
pip install -e ".[dev_full]"
pre-commit install && pre-commit install --hook-type commit-msg

# Run checks manually on all files
pre-commit run --all-files
ruff check --fix . && ruff format .
pre-commit run --hook-stage manual bandit --all-files

# Update hooks
pre-commit autoupdate
```

## Need Help?

- **Ruff Documentation**: https://docs.astral.sh/ruff/
- **Conventional Commits**: https://www.conventionalcommits.org/
- **Bandit Documentation**: https://bandit.readthedocs.io/


Open an issue and describe what you're trying to do — we're usually friendly and helpful.
