# Clippy for Mac �

Your AI-powered desktop companion.

Clippy brings a smart, interactive friend to your macOS workspace. Inspired by the nostalgia of desktop assistants but powered by modern AI, Clippy lives on your screen to keep you company.

## Key Features

*   **Intelligent Chat**: Clippy is connected to OpenAI-compatible APIs, allowing him to greet you, chat, and offer witty remarks.
*   **Alive on Your Screen**: Watch Clippy explore your desktop, walk around, and interact with your windows.
*   **Your Personal Sidekick**: Customize Clippy's size, appearance, and personality to fit your vibe.

## Getting Started

### Prerequisites

Ensure you have `uv` installed for dependency management.

### Installation

**Local Setup:**

```bash
uv sync
```

**Global Installation:**

Install Clippy globally to access him from anywhere:

```bash
uv tool install .
```

## How to Run

Wake Clippy up:

```bash
uv run clippy
```

Alternatively, run as a module:

```bash
uv run python -m clippy.main
```

## Customization

### Personality & Brains
You can give Clippy a unique personality by connecting him to a local LLM server (default: `http://127.0.0.1:8080`).

1.  Access the settings via the system tray icon.
2.  Modify the "System Prompt" to define how Clippy speaks and behaves.
3.  Save your changes to update his brain.

## Acknowledgements

Built with inspiration from [vscode-pets](https://github.com/tonybaloney/vscode-pets) by [tonybaloney](https://github.com/tonybaloney), utilizing their delightful pixel art assets.
