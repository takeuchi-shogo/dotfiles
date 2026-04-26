---
name: devbox
description: Reference for the devbox development environment manager. Covers Nix-based reproducible dev environments and GitHub Actions usage examples.
origin: external
---

# devbox Skill

devbox is a Nix-based development environment manager. It provides isolated, reproducible environments per project.

## Installation

```bash
curl -fsSL https://get.jetify.com/devbox | bash
```

## Basic Commands

```bash
# Initialize project (creates devbox.json)
devbox init

# Add packages
devbox add nodejs@20
devbox add python@3.12 go@1.22

# Remove a package
devbox rm nodejs

# Enter the devbox shell
devbox shell

# Run a command (without entering the shell)
devbox run -- npm test

# Run a script
devbox run test

# Start services (process-compose)
devbox services start

# Search packages
devbox search nodejs
```

## devbox.json

```json
{
  "$schema": "https://raw.githubusercontent.com/jetify-com/devbox/main/.schema/devbox.schema.json",
  "packages": [
    "nodejs@20",
    "python@3.12"
  ],
  "shell": {
    "init_hook": [
      "echo 'Welcome to devbox!'",
      "export FOO=bar"
    ],
    "scripts": {
      "test": "npm test",
      "dev": "npm run dev",
      "build": "npm run build"
    }
  }
}
```

## Package Specification

```json
{
  "packages": [
    "nodejs@20",
    "python@3.12.0",
    "go@latest",
    "github:NixOS/nixpkgs#hello"
  ]
}
```

Package search: https://www.nixhub.io

## Scripts

```json
{
  "shell": {
    "scripts": {
      "test": "npm test",
      "dev": "npm run dev",
      "lint": [
        "eslint .",
        "prettier --check ."
      ]
    }
  }
}
```

```bash
devbox run test
devbox run dev
```

## Services (process-compose)

Create `process-compose.yaml`:

```yaml
processes:
  web:
    command: npm run dev
  db:
    command: postgres -D /tmp/pgdata
```

```bash
devbox services start      # Start all services
devbox services stop       # Stop all services
devbox services ls         # List services
```

## Environment Variables

```json
{
  "env": {
    "DATABASE_URL": "postgresql://localhost:5432/dev",
    "NODE_ENV": "development"
  },
  "shell": {
    "init_hook": [
      "export API_KEY=$(<.api_key)"
    ]
  }
}
```

## GitHub Actions

Use `jetify-com/devbox-install-action`. See `assets/gh_action_example.yaml` for a complete example.

```yaml
steps:
  - uses: actions/checkout@v4

  - uses: jetify-com/devbox-install-action@v0.12.0
    # with:
    #   enable-cache: true  # Nix store cache

  - run: devbox run test
```

## Common Options

| Option | Description |
|-----------|------|
| `--config` | Path to devbox.json |
| `--quiet` | Suppress output |
| `--print-env` | Print environment variables |

## References

- https://github.com/jetify-com/devbox
- https://www.jetify.com/devbox/docs/
- https://www.nixhub.io
