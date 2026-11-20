"""
Engineering Incident Forensics Engine for Silicon Odyssey.
Deep-dive post-mortem analysis of the Comdex Series-4 Prototype thermal disaster.
"""

from typing import Dict, Any, List


class ForensicsEngine:
    @staticmethod
    def get_comdex_forensic_report() -> Dict[str, Any]:
        return {
            "incident_id": "INC-198X-COMDEX-01",
            "title": "Series-4 Prototype Keynote Thermal Failure",
            "system": "Series-4 Flagship Microprocessor Prototype",
            "venue": "Comdex Keynote Live Demonstration, Las Vegas, Nevada",
            "document_coordinates": {
                "page": 23,
                "header_label": "Chapter 3",
                "narrative_label": "Chapter 5: DISASTER ON THE LAS VEGAS SHOW FLOOR",
                "discrepancy_alert": "Header cites Chapter 3 while author specifies Chapter 5."
            },
            "incident_timeline": [
                {
                    "time_mark": "T+00:00",
                    "event": "Live keynote demonstration initiated on Las Vegas show floor.",
                    "status": "Normal Operations"
                },
                {
                    "time_mark": "T+02:00",
                    "event": "Processor instruction decoding workload applied; voltage regulators active.",
                    "status": "Nominal"
                },
                {
                    "time_mark": "T+04:00",
                    "event": "Catastrophic thermal failure; prototype billowed smoke on stage.",
                    "status": "CRITICAL FAILURE / SHUTDOWN"
                },
                {
                    "time_mark": "Post-Mortem",
                    "event": "Hardware teardown reveals technician inverted fan connector and omitted thermal paste.",
                    "status": "Root Cause Verified"
                }
            ],
            "root_causes": [
                {
                    "component": "12V Cooling Fan Power Connector",
                    "defect": "Plugged in inverted (backwards polarity)",
                    "impact": "Cooling fan failed to spin or reversed airflow, preventing convective heat dissipation across the casing.",
                    "severity": "CRITICAL"
                },
                {
                    "component": "Primary Voltage Regulator Heatsink",
                    "defect": "Total omission of thermal interface material (thermal paste)",
                    "impact": "Extremely high thermal interface resistance (Rth) between regulator package and heatsink, triggering rapid junction thermal runaway.",
                    "severity": "CRITICAL"
                }
            ],
            "forensic_quote": (
                "Post-mortem inspection revealed the exact cause: a technician had plugged the 12V cooling fan "
                "power connector in inverted (backwards) and forgot to apply thermal paste to the primary voltage regulator heatsink."
            ),
            "corrective_actions_checklist": [
                {
                    "action": "Implement mechanically keyed Molex/header fan connectors preventing reverse insertion.",
                    "status": "MANDATORY"
                },
                {
                    "action": "Institute two-person dual-signoff QA checklist on all demonstration hardware before stage release.",
                    "status": "MANDATORY"
                },
                {
                    "action": "Standardize pre-applied thermal pads or calibrated thermal compound syringes with weight checks.",
                    "status": "MANDATORY"
                },
                {
                    "action": "Integrate thermal shutdown sensor circuit on board to prevent catastrophic smoke.",
                    "status": "RECOMMENDED"
                }
            ]
        }

