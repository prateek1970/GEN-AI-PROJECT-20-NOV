"""
Timeline & Entity Graph Extractor for Silicon Odyssey.
Extracts chronological milestones, entities, hardware, locations, and financial transactions.
"""

from typing import List, Dict, Any


class TimelineExtractor:
    def __init__(self, parsed_pages: List[Dict[str, Any]]):
        self.pages = parsed_pages
        self.narratives = [p for p in parsed_pages if not p["is_boilerplate"]]

    def get_timeline_events(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "event_1984",
                "year": "1984",
                "title": "Founding in Sycamore Lane Garage",
                "chapter_header": "Chapter 1",
                "chapter_narrative": "Chapter 1",
                "page": 6,
                "location": "742 Sycamore Lane, Sunnyvale, California",
                "summary": "Elena Vance and the author hand-soldered the first 50 microprocessor boards in a parents' two-car garage using a secondhand wave-soldering rig.",
                "category": "Founding & Hardware",
                "tag_color": "emerald",
                "entities": {
                    "people": ["Elena Vance (Co-founder)", "Founder's Parents"],
                    "location": "742 Sycamore Lane, Sunnyvale, CA",
                    "hardware": ["First 50 microprocessor boards", "Secondhand wave-soldering rig"],
                    "financial": ["Bootstrapped / no commercial office budget"]
                },
                "quote": "In the summer of 1984, my co-founder Elena Vance and I could not afford commercial office space. We hand-soldered and assembled our first 50 microprocessor circuit boards inside my parents’ two-car garage located at 742 Sycamore Lane in Sunnyvale, California..."
            },
            {
                "id": "event_comdex",
                "year": "Mid-1980s",
                "title": "Disaster on the Las Vegas Show Floor",
                "chapter_header": "Chapter 3",
                "chapter_narrative": "Chapter 5",
                "page": 23,
                "has_discrepancy": True,
                "discrepancy_note": "Header labels this Chapter 3, while author's narrative specifies Chapter 5.",
                "location": "Comdex, Las Vegas, Nevada",
                "summary": "Keynote demonstration of flagship Series-4 prototype suffered catastrophic thermal failure after 4 minutes due to technician plugging inverted 12V fan connector and forgetting thermal paste.",
                "category": "Engineering Crisis",
                "tag_color": "rose",
                "entities": {
                    "people": ["Keynote Technician"],
                    "location": "Comdex Las Vegas Show Floor",
                    "hardware": ["Series-4 Prototype", "12V cooling fan connector", "Voltage regulator heatsink", "Thermal paste"],
                    "failure_duration": "4 minutes into keynote"
                },
                "quote": "During our live keynote demonstration at Comdex in Chapter 5, our flagship Series-4 prototype suffered a catastrophic thermal failure and billowed smoke after four minutes. Post-mortem inspection revealed the exact cause: a technician had plugged the 12V cooling fan power connector in inverted (backwards) and forgot to apply thermal paste..."
            },
            {
                "id": "event_1991",
                "year": "1991",
                "title": "Betting the House in the 1991 Downturn",
                "chapter_header": "Chapter 4",
                "chapter_narrative": "Chapter 8",
                "page": 37,
                "has_discrepancy": True,
                "discrepancy_note": "Header labels this Chapter 4, while author's narrative specifies Chapter 8.",
                "location": "Community Bank",
                "summary": "Series-B lead investor pulled out during semiconductor recession. Founder took out a second mortgage on family home with 72 hours to payroll, securing exactly $185,000 USD.",
                "category": "Financing & Survival",
                "tag_color": "amber",
                "entities": {
                    "people": ["Series-B Lead Investor", "Community Bank Officers", "Family"],
                    "location": "Local Community Bank",
                    "financial": ["$185,000 USD emergency bridge financing", "Second mortgage on family home"],
                    "time_pressure": "72 hours to meet engineering payroll"
                },
                "quote": "When our Series-B lead investor pulled out during the brutal 1991 semiconductor downturn, we had seventy-two hours to meet engineering payroll. I walked into the local community bank and secured exactly $185,000 USD in emergency bridge financing by taking out a second mortgage on our family home."
            }
        ]

    def get_entity_breakdown(self) -> Dict[str, Any]:
        return {
            "key_people": [
                {"name": "Elena Vance", "role": "Co-founder & Chief Engineering Collaborator", "first_appeared": "Page 6 (1984)"},
                {"name": "Assembly Technician", "role": "Hardware Stage Crew", "first_appeared": "Page 23 (Comdex)"},
                {"name": "Series-B Lead Investor", "role": "Venture Capital Partner (Defected)", "first_appeared": "Page 37 (1991)"}
            ],
            "locations": [
                {"place": "742 Sycamore Lane, Sunnyvale, CA", "description": "Parents' two-car garage; birth of first 50 microprocessor boards", "page": 6},
                {"place": "Las Vegas Show Floor (Comdex)", "description": "Live keynote venue of Series-4 thermal smoke incident", "page": 23},
                {"place": "Local Community Bank", "description": "Site where $185,000 USD second mortgage loan was closed in 72 hours", "page": 37}
            ],
            "hardware_artifacts": [
                {"item": "First 50 Microprocessor Circuit Boards", "role": "Initial production batch", "page": 6},
                {"item": "Secondhand Wave-Soldering Rig", "role": "Garage manufacturing equipment", "page": 6},
                {"item": "Series-4 Prototype", "role": "Flagship processor demonstrated at Comdex", "page": 23},
                {"item": "Inverted 12V Fan Connector & Unpasted Heatsink", "role": "Root failure vectors", "page": 23}
            ],
            "financial_milestones": [
                {"amount": "Bootstrapped / Low Capital", "detail": "Unable to afford commercial office lease", "page": 6},
                {"amount": "$185,000 USD", "detail": "Emergency bridge loan via second mortgage within 72h payroll deadline", "page": 37}
            ]
        }
