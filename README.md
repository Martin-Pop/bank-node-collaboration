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