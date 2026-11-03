# Bright Tech International - AI Lead Intelligence & Acquisition Pipeline

**Target Markets:** United Kingdom (UK) & United States (US) | **Version:** 1.0 (Production-Ready)

---

## 📌 Executive Summary

An automated B2B lead intelligence, dynamic prospecting, and explainable qualification engine built for **Bright Tech International**. The pipeline discovers active businesses across UK and US markets, analyzes public operational evidence, maps specific operational pain points to Bright Tech service offerings, and enforces strict **Human-in-the-Loop** governance before CRM ingestion.

---

## 🛡️ Core Governance & Architectural Principles

1. **Zero Hallucination:** Zero fabricated contacts, buying intent, or fake needs. Every match is grounded in public operational data and explicitly labeled as a **Hypothesis**.
2. **Transparent 100-Point Fit Scoring:** Programmatic scoring across 7 objective categories:
   - Target Industry Fit: 20 pts
   - Target Geography (UK/US): 15 pts
   - Service Fit Relevance: 25 pts
   - Active Business Verification: 10 pts
   - Official Public Contact Route: 10 pts
   - ICP Model / Company Size: 10 pts
   - Operational Intent Signals: 10 pts
3. **Persistent Deduplication:** Domain and market composite keys (`domain#country`) ensure infinite runs append fresh leads without duplicate records.
4. **Human-in-the-Loop & Compliance:** Direct autonomous outreach (cold SMS/email/calls) is strictly disabled. Records are staged as `Pending Human Review` ensuring full UK GDPR and PECR compliance.

---

## 🛠️ Tech Stack & Dependencies

- **Core Engine:** Python 3 (Native standard libraries: `urllib`, `re`, `csv`, `datetime`, `random`)
- **Web App / Dashboard:** `streamlit`
- **Data Analytics:** `pandas`
- **Presentation Export:** `openpyxl`

---

## 📂 Project Structure

```text
bright_tech_lead_ai/
│
├── app.py                         # Continuous discovery & deterministic scoring engine
├── dashboard.py                   # Streamlit interactive monitoring & qualification UI
├── export_clean.py                # Formatter generating executive-ready styled Excel
│
├── bright_tech_qualified_leads.csv # Complete technical database (20+ audit columns)
├── Bright_Tech_Clean_Leads.xlsx   # Styled presentation sheet (8 core business columns)
├── requirements.txt               # Lightweight dependency list
└── README.md                      # System documentation & execution guide
```

---

## 🚀 Execution & Usage (How to Run)

Follow these steps to run each component of the pipeline:

### Step 1: Install Dependencies

Install all required lightweight packages in one command:

```bash
pip install -r requirements.txt
```

### Step 2: Run Discovery & Scoring Engine (CLI / Backend)

Executes the live web intelligence engine, analyzes prospect data, applies the 100-point scoring formula, and appends newly discovered leads without duplicates:

```bash
python app.py
```

### Step 3: Launch Web Dashboard (Interactive UI)

Opens an interactive web application in your browser with real-time metrics, priority filters, on-demand discovery triggers, and direct file export:

```bash
streamlit run dashboard.py
```

### Step 4: Generate Clean Presentation Excel

Converts the technical CSV data into a styled, professional Excel report with bold headers and green score highlights:

```bash
python export_clean.py
```

---

## 📊 Deliverables & Files Explained

This system produces two distinct deliverables tailored for different operational needs:

| Deliverable File | Target Audience | Purpose & Contents |
| :--- | :--- | :--- |
| **`bright_tech_qualified_leads.csv`** | **CRM & Technical Pipeline** | Complete technical audit database containing 20+ columns (individual category points, source URLs, timestamps, deduplication keys, and staging flags) for automated ingestion into GoHighLevel (GHL) or internal databases. |
| **`Bright_Tech_Clean_Leads.xlsx`** | **Executives & Stakeholders** | Presentation-ready Excel spreadsheet filtered down to 8 core business columns with bold styled headers, auto-adjusted column widths, and visual color highlights for high-priority (80-100) scores. |

---

## 👤 Author &  Developer

- **Sehar Tahir** - Team Lead
- **Role:** Full Stack Developer | GHL CRM Automation Specialist
- **Project:** Bright Tech International Lead Intelligence System
  