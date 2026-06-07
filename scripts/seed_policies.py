"""Seed internal policy documents for compliance mapping."""
import asyncio
import uuid

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings
from app.models.policy import PolicyChunk, PolicyDocument

POLICIES = [
    {
        "title": "Data Privacy and Protection Policy",
        "category": "data_protection",
        "content": """1. Purpose and Scope
This Data Privacy and Protection Policy establishes the framework for handling personal and sensitive data within the organization. It applies to all employees, contractors, and third-party service providers.

2. Data Collection Principles
2.1 Personal data shall be collected only for specified, explicit, and legitimate purposes.
2.2 Data minimization principles shall be applied - only necessary data shall be collected.
2.3 Consent shall be obtained prior to data collection where required by applicable law.

3. Data Storage and Security
3.1 All personal data shall be stored in encrypted formats using AES-256 encryption.
3.2 Access to personal data shall be restricted on a need-to-know basis.
3.3 Data retention periods shall comply with regulatory requirements and shall not exceed 7 years unless otherwise specified.

4. Data Sharing and Disclosure
4.1 Personal data shall not be shared with third parties without explicit consent.
4.2 Data sharing agreements shall be executed with all data processors.
4.3 Cross-border data transfers shall comply with applicable data localization requirements.

5. Breach Notification
5.1 Data breaches shall be reported to the Data Protection Officer within 24 hours.
5.2 Regulatory authorities shall be notified within 72 hours of breach discovery.
5.3 Affected individuals shall be notified without undue delay.

6. Review and Audit
This policy shall be reviewed annually and updated to reflect changes in regulatory requirements.""",
    },
    {
        "title": "Anti-Money Laundering (AML) Policy",
        "category": "anti_money_laundering",
        "content": """1. Purpose and Scope
This Anti-Money Laundering Policy establishes measures to prevent, detect, and report money laundering activities.

2. Customer Due Diligence (CDD)
2.1 Enhanced due diligence shall be performed for high-risk customers.
2.2 Beneficial ownership identification is mandatory for all legal entity customers.
2.3 CDD documentation shall be updated every 12 months for high-risk customers.

3. Transaction Monitoring
3.1 Transactions exceeding INR 10 lakhs shall be subject to additional scrutiny.
3.2 Suspicious transaction reports shall be filed with FIU-IND within 7 days.
3.3 Cash transactions exceeding INR 50 lakhs shall be reported.

4. Record Keeping
4.1 All AML records shall be maintained for a minimum of 5 years.
4.2 Customer identification records shall be preserved for 5 years after account closure.

5. Training and Awareness
5.1 Annual AML training is mandatory for all employees.
5.2 Specialized training shall be provided to high-risk department staff.

6. Compliance and Reporting
6.1 The Compliance Officer shall submit quarterly AML compliance reports to the Board.
6.2 Internal audits of AML controls shall be conducted annually.""",
    },
    {
        "title": "Code of Conduct and Ethics",
        "category": "governance",
        "content": """1. Purpose and Scope
This Code of Conduct establishes ethical standards and governance principles for all employees.

2. Conflict of Interest
2.1 Employees shall disclose any actual or potential conflicts of interest.
2.2 No employee shall engage in activities that compete with the organization's interests.
2.3 Personal investments in competitor entities shall be disclosed.

3. Insider Trading
3.1 Employees with access to unpublished price-sensitive information shall not trade during designated trading windows.
3.2 All trades by designated persons shall be pre-cleared by the Compliance Officer.
3.3 A minimum 30-day holding period applies to all securities transactions.

4. Gift and Hospitality
4.1 Acceptance of gifts valued over INR 5,000 shall be reported.
4.2 No gifts shall be accepted from entities under regulatory investigation.

5. Whistleblower Protection
5.1 Anonymous reporting channels are available for ethical concerns.
5.2 Retaliation against whistleblowers is strictly prohibited.

6. Disciplinary Actions
Violations of this Code shall result in disciplinary action up to and including termination of employment.""",
    },
    {
        "title": "Risk Management Framework",
        "category": "risk_management",
        "content": """1. Purpose and Scope
This Risk Management Framework establishes the organization's approach to identifying, assessing, and mitigating risks.

2. Risk Governance
2.1 The Risk Management Committee shall meet quarterly to review risk exposure.
2.2 The Chief Risk Officer shall report directly to the Board Risk Committee.
2.3 Risk appetite limits shall be approved by the Board annually.

3. Risk Categories
3.1 Credit Risk: Exposure limits, collateral requirements, and credit rating thresholds.
3.2 Market Risk: Value-at-Risk limits, stress testing, and scenario analysis.
3.3 Operational Risk: Business continuity planning, disaster recovery, and internal controls.
3.4 Compliance Risk: Regulatory change monitoring, compliance testing, and reporting.
3.5 Reputational Risk: Media monitoring, stakeholder engagement, and crisis management.

4. Risk Assessment Methodology
4.1 Risks shall be assessed on a 5x5 impact-likelihood matrix.
4.2 Residual risk shall be calculated after applying control effectiveness ratings.
4.3 Risk registers shall be updated quarterly.

5. Capital Adequacy
5.1 The organization shall maintain capital above regulatory minimum requirements.
5.2 Internal Capital Adequacy Assessment Process (ICAAP) shall be conducted annually.

6. Reporting
Risk dashboards shall be submitted to the Board monthly and to regulators as required.""",
    },
    {
        "title": "Regulatory Compliance Policy",
        "category": "general",
        "content": """1. Purpose and Scope
This Regulatory Compliance Policy ensures adherence to all applicable laws, regulations, and regulatory guidelines.

2. Regulatory Monitoring
2.1 The Compliance team shall monitor regulatory developments across SEBI, RBI, IRDAI, and other applicable regulators.
2.2 Regulatory change impact assessments shall be completed within 15 working days of regulation publication.
2.3 A regulatory watch list shall be maintained and reviewed weekly.

3. Compliance Obligations
3.1 All regulatory filings shall be submitted within prescribed timelines.
3.2 Compliance checklists shall be maintained for each applicable regulation.
3.3 Third-party compliance audits shall be conducted biennially.

4. Reporting and Escalation
4.1 Material compliance breaches shall be escalated to the Board within 48 hours.
4.2 Quarterly compliance reports shall be submitted to the Board.
4.3 Regulatory correspondence shall be managed through a centralized system.

5. Training
5.1 Induction compliance training is mandatory for all new hires.
5.2 Annual refresher training on regulatory updates shall be provided.

6. Record Keeping
All compliance records shall be retained for the duration required by applicable regulations, typically 5-8 years.""",
    },
]


async def seed() -> None:
    engine = create_async_engine(str(settings.database_url))
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as session:
        existing = await session.get(PolicyDocument, "00000000-0000-0000-0000-000000000001")
        if existing:
            print("Policies already seeded, skipping.")
            await engine.dispose()
            return

        for policy_data in POLICIES:
            doc = PolicyDocument(
                id=str(uuid.uuid4()),
                title=policy_data["title"],
                category=policy_data["category"],
                content=policy_data["content"],
                version=1,
                is_active=True,
            )
            session.add(doc)
            await session.flush()

            content = policy_data["content"]
            chunks = [content[i:i + 2000] for i in range(0, len(content), 2000)]
            for idx, chunk_text in enumerate(chunks):
                chunk = PolicyChunk(
                    id=str(uuid.uuid4()),
                    policy_document_id=doc.id,
                    chunk_index=idx,
                    content=chunk_text,
                )
                session.add(chunk)

        await session.commit()
        print(f"Seeded {len(POLICIES)} policy documents with chunks.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
