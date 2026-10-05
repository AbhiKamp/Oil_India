# StrataSentry-NWIS Threat Model & Risk Analysis
## STRIDE Threat Modeling for Upstream Petroleum Cyber-Physical Systems

---

## 1. Scope & Assets Under Protection

- **Downhole Telemetry Streams**: MWD/LWD directional data, pressure-while-drilling (PWD).
- **Sub-surface Reservoir Intelligence**: Proprietary formation tops, pore pressure profiles.
- **Driller Tactical Advisory System**: Display screens, alert tones, and recommendation engines.
- **Model Checkpoints**: XGBoost classifiers and LSTM Autoencoders deployed on rig edge hardware.

---

## 2. STRIDE Threat Matrix & Defenses

| Threat Category | Specific Attack Vector | Impact Severity | StrataSentry Mitigation |
|---|---|---|---|
| **Spoofing** | Adversary injects false WITSML sensor packets over rig LAN | CRITICAL | Mutual TLS 1.3 authentication, HMAC-SHA256 sensor frame signatures |
| **Tampering** | Malicious tampering with ML model weights on edge server | CRITICAL | SHA-256 weight checksums verified at boot; automated physics fallback |
| **Repudiation** | Operator claims alert was never received after stuck pipe event | HIGH | Cryptographic append-only Merkle audit trail logging all alerts and driller ACKs |
| **Information Disclosure** | Exfiltration of proprietary reservoir seismic/tops | HIGH | Air-gapped network zoning, data masking engine, ChaCha20-Poly1305 encryption |
| **Denial of Service** | Flooding telemetry ingestion port to crash Driller HUD | CRITICAL | In-memory token bucket rate limiting, zero external internet dependencies |
| **Elevation of Privilege** | Rig contractor attempts to alter well control threshold limits | HIGH | Strict Role-Based Access Control (RBAC) enforced at API gateway |
