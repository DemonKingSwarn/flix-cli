# Contribution Guidelines

## Pull Requests

- **Appease the linter**: Run `uv run ruff check .` and `uv run ruff format .` before submitting
- Bump the version
- Adjust the Readme according to your changes (if applicable)
- No extra dependencies unless absolutely necessary
- If you're fixing an issue, open an issue as well or link existing one

## Development Setup

1. Install [UV](https://docs.astral.sh/uv/getting-started/installation/) (Rust-powered Python package manager)
2. Clone the repository
3. Run `uv sync` to install dependencies
4. Make your changes
5. Run linting: `uv run ruff check . && uv run ruff format .`
6. Test your changes locally: `uv pip install -e .`

## Issues

- Use the issue templates (Pending)
- Provide screenshot if applicable

## How else can I help?

- Join the [discord](https://discord.gg/YKHtmNJh)
- Take part in troubleshooting and testing
- Star the repo
- Follow the maintainers