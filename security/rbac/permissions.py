"""
StrataSentry-NWIS: Permission Matrix
"""

from .roles import UserRole

ROLE_PERMISSIONS = {
    UserRole.DRILLER: [
        "telemetry:read",
        "alerts:read",
        "alerts:acknowledge",
        "copilot:query"
    ],
    UserRole.TOOLPUSHER: [
        "telemetry:read",
        "alerts:read",
        "alerts:acknowledge",
        "copilot:query",
        "evidence:read",
        "drilling_params:configure"
    ],
    UserRole.OPERATIONS_GEOLOGIST: [
        "telemetry:read",
        "alerts:read",
        "formations:manage",
        "documents:upload",
        "copilot:query"
    ],
    UserRole.DRILLING_ENGINEER: [
        "telemetry:read",
        "alerts:read",
        "hydraulics:calibrate",
        "trajectories:manage",
        "copilot:query"
    ],
    UserRole.DATA_SCIENTIST: [
        "models:evaluate",
        "models:retrain",
        "telemetry:export"
    ],
    UserRole.SECURITY_ADMIN: [
        "audit:read",
        "users:manage",
        "edge:configure"
    ]
}

def has_permission(role: UserRole, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, [])
