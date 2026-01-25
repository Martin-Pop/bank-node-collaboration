# BankNode Server

Concurrent TCP banking server simulation utilizing **multiprocessing** for parallel client handling and
**Flask** for real-time monitoring. Data is persistently stored in **SQLite**.

## Features

-   **Multiprocessing:** Non-blocking concurrent client handling.
-   **Persistence:** SQLite database storage.
-   **Monitoring:** Web dashboard for stats and control (Flask).
-   **Security:** Rate limiting & IP banning.

## Requirements
- Python 3.8+
- Pip (Python Package Installer)
- Libraries `flask`, `pyinstaller`

## Installation

### Option A: Download Release

Download the latest release from the Releases section and run it.

### Option B: Run from Source

1.  **Install Dependencies:**
    ```
    pip install -r requirements.txt
    ```
2.  **Run Application:**
    ```
    python src/main/app.py
    ```
3.  **Build Exe (Optional):**
    ```
    pyinstaller --noconfirm --onedir --windowed --name "BankNode" --paths "." --add-data "src/web/public;public" src/main.py
    ```
    Copy the config folder `config` inside your newly build folder `dist/BankNode`

## Commands
| Name                   | Code | Call Syntax                  | Success Response | Error Response |
|:-----------------------|:-----|:-----------------------------| :--- | :--- |
| Bank code              | BC   | `BC`                         | `BC <ip>` | `ER <message>` |
| Account create         | AC   | `AC`                         | `AC <account>/<ip>` | `ER <message>` |
| Account deposit        | AD   | `AD <account>/<ip> <number>` | `AD` | `ER <message>` |
| Account withdrawal     | AW   | `AW <account>/<ip> <number>` | `AW` | `ER <message>` |
| Account balance        | AB   | `AB <account>/<ip>`          | `AB <number>` | `ER <message>` |
| Account remove         | AR   | `AR <account>/<ip>`          | `AR` | `ER <message>` |
| Bank (total) amount    | BA   | `BA`                         | `BA <number>` | `ER <message>` |
| Bank number of clients | BN   | `BN`                         | `BN <number>` | `ER <message>` |
| Robbery Plan           | RP   | `RP <number>`                | `RP <message>` | `ER <message>` |

## Configuration

**Location:** `config/config.json`

* `host` - The IP address where bank listens for incoming connections.
* `port` - The port number the bank listens on.
* `storage_path` - The file system path to the SQLite database file, can be absolute or relative to root.
* `storage_timeout` - Maximum time (in seconds) to wait for the database lock to be released.
* `bank_workers` - The number of parallel worker processes dedicated to handling client requests.
* `client_timeout` - The maximum time (in seconds) to wait for data from a client before closing the connection.
* `max_requests_per_minute` - The rate limit threshold per IP address to prevent spam or DDoS.
* `max_bad_commands` - The number of invalid commands allowed from a client before they are banned (after a successful command the counter decrements).
* `ban_duration` - The duration (in seconds) a client remains banned after exceeding limits.
* `monitoring_host` - The IP address used to bind the web monitoring dashboard.
* `monitoring_port` - The port number for the web monitoring HTTP server.
* `network_scan_port_range` - A list `[start, end]` defining the port range to scan for other peers.
* `network_timeout` - The timeout (in seconds) for network operations and peer discovery scans.
* `network_scan_subnet` - The IP subnet prefix used when scanning for local peers.