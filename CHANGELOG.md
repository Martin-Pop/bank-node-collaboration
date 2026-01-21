## [0.0.2] - 21. 1. 2026 - Jakub Šrámek

### Added
- Implemented core banking logic for AW (Withdraw), AB (Balance), BA (Total Amount), and BN (Client Count).
- Connected bank commands with the storage layer and shared memory cache for real-time updates.
- Ensured thread-safe account operations using locks during database transactions.
- Added input validation for account addresses and withdrawal amounts in command classes.
- Registered new banking and statistics commands in the CommandFactory.

## [0.0.1] - 20. 1. 2026 - Martin Pop

### Added
- this changelog file
- initial migration from the old / legacy repository.
