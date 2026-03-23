# AI Security Platform: Demo Script

This script guide walks through a 10-minute demo of the platform's core intelligence capabilities.

## Scene 1: The Command Center (Dashboard)
1. **Login**: Use `admin@platform.io` / `admin1234`.
2. **Overview**: Point out the **Alert Surface** (Recent Alerts) and **Exposure Ranking**.
3. **KPIs**: Show the **Mean Time to Triage** and **Critical Exposure Rate** cards.
4. **Summary**: Read the **AI-Generated Executive Summary** highlighting the SWIFT Router threat.

## Scene 2: The Agentic Triage (Alerts)
1. Navigate to **Alerts**.
2. Select **"Malicious Process Execution"** on SWIFT Router.
3. Click **"Run AI Triage"**.
4. **Narrative**: Explain how the SOC agent correlates the `mimikatz.exe` indicator against the SWIFT asset's criticality.
5. **Result**: Observe the **Rationale** and **Next Steps** (Isolate Host, Rotate SWIFT Credentials).

## Scene 3: Forensic Correlation (Incidents)
1. Navigate to **Incidents**.
2. Select the correlated incident (Bank-wide Credential Theft Attempt).
3. Click **"Run AI Investigation"**.
4. **Narrative**: The agent traces the lateral movement from the Brute Force on the Gateway to the Mimikatz on the SWIFT router.
5. **Timeline**: Show the reconstructed attack timeline.

## Scene 4: Strategic Defense (Policies & Copilot)
1. Navigate to **Policies**.
2. Use the **Q&A Panel**: Ask "What are the requirements for SWIFT administrator access?"
3. **Traceability**: Show the citations from the ISO 27001 Access Control Policy.
4. **Copilot**: Open the Copilot Page in `CISO Mode`.
5. **Query**: Ask "Summarize the current blast radius of Asset-02's compromise."
6. **Insight**: The CISO mode provides a risk-centric summary focusing on financial impact and regulatory compliance.

## Scene 5: Knowledge Context (Graph Explorer)
1. Navigate to **Knowledge**.
2. Search for `Asset-01`.
3. **Pivot**: Move from `Asset-01` -> `Alert-01` -> `Attacker IP`.
4. **Conclusion**: Show how the "Adjacency Rails" make complex forensics feel like light browsing.

---
*End of Demo.*
