# NanoDroid-Core OmniEngine (ApexArchitect-X) - Official Operator Manual
**Target Environment:** Samsung Galaxy A16 (ARM64, Android, Termux)  
**Version:** 4.2.2  
**Architecture:** Asynchronous Loopback FastAPI Daemon + Shizuku (`rish`) Privileged IPC  

---

## 1. System Architecture Overview
NanoDroid-Core is a zero-cloud, high-performance on-device automation and intent-parsing engine. It bypasses resource-heavy user-space C++ LLM binaries by leveraging native system integration, FastAPI asynchronous routing, and accessibility tree parsing.

- **FastAPI Core Daemon (`core_server.py`):** Runs locally on `127.0.0.1:8000`. Handles routing, schema validation (Pydantic), and translation of high-level automation triggers into low-level Android shell instructions.
- **Privilege & Binder Bridge (`rish`):** Routes system-level commands (input injection, package management, window dumping) securely through the Shizuku binder without requiring full root access.
- **UI Automation & Self-Healing Parser (`uiautomator`):** Dumps active window XML hierarchies to `/data/local/tmp/window_dump.xml`, parses interactive node bounds, and dynamically calculates center tap coordinates.

---

## 2. Daemon Lifecycle Management (`nanodroidctl`)
The background service controller manages the OmniEngine process state, PID tracking, and log redirection.

- **Start Daemon:** `./nanodroidctl start`
- **Stop Daemon:** `./nanodroidctl stop`
- **Restart Daemon:** `./nanodroidctl restart`
- **Check Status & Tail Logs:** `./nanodroidctl status` / `./nanodroidctl logs`

---

## 3. REST API Endpoint Reference
Base URL: `http://127.0.0.1:8000`

### `GET /`
Returns engine status, version, and target hardware spec.

### `GET /system/packages`
Enumerates all installed package names on the device via Shizuku `rish`.

### `GET /ui/context`
Wakes the device screen, dismisses the keyguard, executes a live `uiautomator dump`, and returns up to 50 active interactive nodes with text, resource IDs, and bounds.

### `POST /ui/execute`
Executes structured action payloads. Supported actions:
- `keyevent`: Requires `key_code` (e.g., `3` for Home, `4` for Back).
- `swipe`: Requires `x`, `y`, `end_x`, `end_y`, `duration_ms`.
- `launch`: Requires `package_name`.
- `click`: Requires `target_text` for self-healing node lookup and tapping.

### `GET /manual`
Returns this complete operator manual in text/markdown format.

---

## 4. Automation Scripts & Intent Bridges
- **Intent Bridge (`ai_intent_bridge.py`):** Parses natural language commands (e.g., `"open loophero"`, `"click 'Continue'"`) and translates them into API payloads.
- **Autonomous Agent (`nanodroid_agent.py`):** Executes closed-loop OODA cycles with self-healing scroll pagination if target nodes are below the fold.
- **System Doctor (`nanodroid_doctor.py` & `verify_pipeline.py`):** Validates loopback routing, Shizuku bindings, and UI dump integrity.
