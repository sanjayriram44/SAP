# probing_focus.py

PROBING_DATABASE = {
    "Sourcing Projects": {
        "Organizational Scope & Complexity": "Ask about multi-entity project governance, cross-ERP data consistency, and approval workflows spanning regions.",
        "Supply Chain & Procurement Complexity": "Probe project-specific sourcing templates, coordination with engineering teams, and handling of long-lead items.",
        "Compliance, Risk & Governance": "Explore regulatory requirements for sourcing projects, including HSE compliance and risk thresholds.",
        "Sustainability & Strategic Sourcing Objectives": "Explore inclusion of ESG criteria and supplier collaboration in capital sourcing projects."
    },
    "RFx Management": {
        "Organizational Scope & Complexity": "Ask about standardization of RFx templates, automation of supplier invitations, and centralized response management.",
        "Compliance, Risk & Governance": "Probe compliance enforcement in RFx events, audit logging, and segregation of duties in approvals.",
        "Sustainability & Strategic Sourcing Objectives": "Explore localization, supplier collaboration preferences, and sustainability-driven KPIs."
    },
    "Negotiation and Bidding": {
        "Supply Chain & Procurement Complexity": "Probe real-time integration with commodity markets and dynamic bid evaluation.",
        "Compliance, Risk & Governance": "Explore risk mitigation strategies during bidding processes.",
        "Sustainability & Strategic Sourcing Objectives": "Explore inclusion of ESG scoring, sustainability weighting, and diversity in bid evaluations."
    },
    "Supplier Evaluation": {
        "Organizational Scope & Complexity": "Ask about centralization of supplier master data across global entities.",
        "Compliance, Risk & Governance": "Probe automated HSE prequalification and insurance validation during onboarding.",
        "Sustainability & Strategic Sourcing Objectives": "Explore supplier risk scoring based on ESG, geopolitical, and financial risks."
    },
    "Contract Management": {
        "Organizational Scope & Complexity": "Ask about standardization of global master agreements and contract templates.",
        "Compliance, Risk & Governance": "Probe legal compliance, jurisdictional obligations, and approval workflows.",
        "Sustainability & Strategic Sourcing Objectives": "Explore tracking of sustainability KPIs and ESG terms in contract clauses."
    },
    "Task and Workflow Management": {
        "Organizational Scope & Complexity": "Ask about policy enforcement and sourcing coordination across decentralized teams.",
        "Compliance, Risk & Governance": "Explore conditional workflows triggered by regulatory thresholds.",
        "Sustainability & Strategic Sourcing Objectives": "Probe collaboration workflows aligned with sustainability governance models."
    },
    "Realize and Deploy": {
        "Organizational Scope & Complexity": "Ask about middleware strategies for integrating multiple ERPs and legacy systems.",
        "Supply Chain & Procurement Complexity": "Explore integration with asset management systems and readiness for UAT.",
        "Compliance, Risk & Governance": "Probe cutover validation, compliance testing, and audit traceability in deployment.",
        "Sustainability & Strategic Sourcing Objectives": "Explore training and localization for global teams with ESG awareness."
    }
}


def get_llm_probing_focus(subprocess: str, user_choices: dict) -> str:
    """
    Get a string of probing guidance lines based on the subprocess and dimension values chosen by the user.
    """
    probes = []
    subprocess_probes = PROBING_DATABASE.get(subprocess, {})

    for dimension, value in user_choices.items():
        if dimension in subprocess_probes:
            probes.append(subprocess_probes[dimension])

    return "\n".join(probes).strip()
