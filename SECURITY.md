# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a vulnerability, please report it responsibly:

1.  **Do NOT** open a public GitHub issue.
2.  Email `security@hypercode.dev` (or the maintainer).
3.  Include details:
    *   Description of the vulnerability.
    *   Steps to reproduce.
    *   Potential impact.

We will acknowledge receipt within 48 hours and strive to provide a fix within 14 days.

## Scope

*   **In Scope**:
    *   Core API (`src/hypercode-core`)
    *   Agent Auth Mechanisms
    *   Docker Configuration (production profiles)
*   **Out of Scope**:
    *   Local development tools
    *   Experimental agents (unless critical risk)
    *   DDoS attacks

## Security Best Practices

*   **Secrets**: Always use `.env` files. Never commit secrets.
*   **Images**: Use pinned Docker image versions.
*   **Access**: Run containers as non-root where possible.
