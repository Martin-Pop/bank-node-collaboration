## [0.0.6] - 21. 1. 2026 - Martin Pop

### Added
- New security feature to limit client requests with timed ban mechanism.

## [0.0.5] - 22. 1. 2026 - Jakub Šrámek

### Added
- Complete configuration validation for all parameters.
- Added path existence validation, and timeout limits.

### Changed
- client_timeout is now mandatory in config (previously hardcoded to 60s).
- ClientConnection uses client_timeout from configuration.

### Fixed
- Application now validates config before startup, preventing runtime errors.

## [0.0.4] - 21. 1. 2026 - Jakub Šrámek

### Added
- Web Monitoring Dashboard: Created a full GUI for real-time bank monitoring (account balances, total capital, and client count).
- Live Data Updates: Integrated AJAX logic for automatic dashboard refreshes without reloading the page.
- Safe Shutdown Mechanism: Added a dedicated button and API to safely terminate all processes and close database connections.
- Connection Tracking: Implemented a shared counter using multiprocessing.Value to track active socket connections across workers.

## [0.0.3] - 21. 1. 2026 - Martin Pop

### Fixed
- Cache locking.

### Added
- Account Withdraw (AW) command.
- Implemented work distribution between workers.


## [0.0.2] - 21. 1. 2026 - Jakub Šrámek

### Added
- Implemented core banking logic for AW (Withdraw), AB (Balance), BA (Total Amount), and BN (Client Count).
- Connected bank commands with the storage layer and shared memory cache for real-time updates.
- Ensured thread-safe account operations using locks during database transactions.
- Added input validation for account addresses and withdrawal amounts in command classes.
- Registered new banking and statistics commands in the CommandFactory.

## [0.0.1] - 20. 1. 2026 - Martin Pop

### Added
- This changelog file.
- Initial migration from the old / legacy repository.
