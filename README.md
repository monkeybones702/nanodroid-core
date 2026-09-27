# BastionAsset Citadel 🛡️🥚💰

> *"Secure the Asset. Defend the Future."*

**BastionAsset Citadel** is a lightweight, mobile-first security suite and automation toolkit designed for local AI agents, LLM pipelines, and developer environments (optimized for Termux and edge hardware). 

---

## 🏛️ Architecture & Component Suite

The repository consolidates three core modules into a single modular CLI and daemon package:

1. **AegisCore CLI (`aegis-cli`)**
   * Multi-layered payload inspection, rule evaluation, obfuscation detection, and canary token trapping (`CANARY_SECRET_KEY_999`).
   * Designed to scan static threat lists and flag injection vectors instantly.
2. **GatewayZero Live Proxy (`aegis-proxy`)**
   * A local HTTP proxy middleware that intercepts prompts *before* they reach local LLM backends (such as `llama.cpp`), dropping malicious inputs with standard HTTP 403 responses.
3. **Nanodroid Clipboard Daemon (`nanodroid`)**
   * A background worker daemon utilizing Termux API to poll clipboard states, detect instruction strings, and dispatch safe background processes autonomously.

---

## 🚀 Quickstart Installation

Ensure you are using Python 3.9+ and have your environment ready. Install the package in editable mode locally:

```bash
# Clone or navigate to your project directory
cd bastion-asset-citadel

# Install dependencies and register CLI entry points
pip install -e .