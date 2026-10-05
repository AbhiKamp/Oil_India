# Security Architecture & Data Governance Policy
## StrataSentry-NWIS (National Well Intelligence System)

---

## 1. Security Scope & Threat Posture

Upstream exploration and development operations represent critical national infrastructure. StrataSentry-NWIS adheres to strict security, air-gap defense, model integrity, and role-based data governance policies to protect sensitive reservoir assets, operational drilling parameters, and wellbore trajectories.

### Core Threat Mitigations:
1. **Telemetry Spoofing / Tampering**: Prevention of malicious or corrupted MWD/LWD sensor streams from manipulating drilling alerts or masking a wellbore kick.
2. **Model Poisoning & Supply Chain Attacks**: Validation of all neural networks and decision tree weights before deployment into rig-site microservers.
3. **Data Exfiltration**: Enforcing strict air-gapped isolation at remote rig sites, zero telemetry egress outside authorized corporate VPNs, and masking of proprietary geological tops.
4. **Denial of Service on Rig Floor**: Redundant local failovers ensuring the driller's tactical advisory displays function with sub-second responsiveness regardless of external network state.

---

## 2. Air-Gapped Rig-Site Architecture

```
+-----------------------------------------------------------+
|             REMOTE DRILLING RIG (AIR-GAPPED ZONE)         |
|                                                           |
|  +--------------------+       +------------------------+  |
|  | Rig Instrumentation| ----> | Local Edge Node        |  |
|  | (MWD/LWD, Sensors) |       | (FastAPI, Qdrant, PG)  |  |
|  +--------------------+       +------------------------+  |
|                                            |              |
|                               +------------v-----------+  |
|                               | Driller Tactical HUD   |  |
|                               | (Direct LAN connection)|  |
|                               +------------------------+  |
+-----------------------------------------------------------+
                             |
         [Periodic Encrypted Sync Bundle via Satellite/USB]
         [HMAC-SHA256 Signed / ChaCha20-Poly1305 Encrypted]
                             |
                             v
+-----------------------------------------------------------+
|          CENTRAL ENTERPRISE HEADQUARTERS CLOUD            |
|                                                           |
|  +--------------------+       +------------------------+  |
|  | Central Historian  | <---- | Cryptographic Ingest   |  |
|  | TimescaleDB Cluster|       | Verification Gateway   |  |
|  +--------------------+       +------------------------+  |
+-----------------------------------------------------------+
```

### Air-Gap Protocol Rules:
- **No Inbound Remote Shells**: Remote SSH and management interfaces on edge nodes are disabled on external interfaces.
- **Physical Key Token Authentication**: Physical YubiKey or hardware token required for local admin maintenance.
- **Encrypted Sync Bundles**: When satellite link is established or physical media used, all data bundles are packaged into signed archives containing telemetry deltas and incident logs.

---

## 3. Role-Based Access Control (RBAC) Matrix

| Role | Telemetry Read | Real-Time Alerts | AI Copilot Chat | Document Upload | Model Retraining | Admin / System Config |
|---|---|---|---|---|---|---|
| **Driller / Assistant Driller** | Read (Active Well) | Full Access (Acoustic + Visual) | SOP Query Only | Denied | Denied | Denied |
| **Toolpusher / Rig Superintendent** | Full Rig Operations | Full Access | Full Access | View Only | Denied | Local Rig Settings |
| **Operations Geologist / Wellsite Biostratigrapher** | Full Field Access | Advisory Alerts | Full Offset Access | Full Upload (Logs/WCR) | Calibration Only | Offset Well Linking |
| **Drilling Operations Center (DOC) Engineer** | Fleet-wide Streaming | Fleet-wide Alerts | Full Access | Full Access | Validation | Notification Routing |
| **Data Science / ML Engineer** | Fleet Historical | Read-Only | Testing Mode | Model Upload | Full Pipeline Access | Model Versioning |
| **System Security Administrator** | Audit Logs Only | Audit Logs Only | Audit Logs Only | Audit Logs Only | Audit Logs Only | Full Security Policies |

---

## 4. Model Integrity & Cryptographic Validation

All models in `models/` (`xgboost/` and `lstm/`) must have a corresponding cryptographically signed SHA-256 hash in `security/model-integrity/checksums.json`:

```bash
# Verify integrity before starting the inference server
python security/model-integrity/checksum_validator.py --verify-all
```

If any model binary diverges from the manifest, the risk engine immediately halts with an audit alarm and reverts to deterministic first-principles physics validation rules.

---

## 5. Audit Logging & Compliance

Every alert issued, driller acknowledgment, prompt query, and SOP recommendation is written to an append-only cryptographic audit log (`security/audit/decision_auditor.py`). The audit log hashes each record into a SHA-256 Merkle chain, preventing retrospective alteration in post-incident investigations.

---

## 6. Vulnerability Disclosure

To report a vulnerability or operational security concern, submit an encrypted report to `security@stratasentry.internal` using our PGP public key:
`4A9F 83B2 C11D 9042 E6F8 7751 A034 22BB 9F18 3E7A`.
