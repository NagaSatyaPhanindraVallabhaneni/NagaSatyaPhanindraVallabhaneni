# Naga Satya Phanindra Vallabhaneni

**Validation Engineer** · Dayton, OH · +1 (984) 687-6001 · [phanindra.vns@gmail.com](mailto:phanindra.vns@gmail.com) · [LinkedIn](https://www.linkedin.com/in/satyavaiengineer/)

> Validation Engineer with an M.S. in Computer Science, a B.Tech in Electronics and Communication Engineering, and 2.5+ years of experience in post-silicon validation, telecom hardware bring-up, high-speed protocol testing, and lab automation. Proficient in validating Ethernet, PCIe, SerDes, SPI, I2C, UART, and JTAG interfaces across evaluation boards and HIL benches using Python (PyVISA/SCPI), C/C++, Embedded Linux, Oscilloscopes, and BERTs.

🛂 Authorized to work in the US on **OPT EAD** · will require future **H-1B sponsorship** · Open to full-time Validation / Embedded / Firmware roles in the USA

## 🛠️ Technical Skills

**Validation & Characterization:** Post-Silicon Validation, Silicon Bring-Up, PVT Characterization, Signal Integrity, BER Testing, Eye Diagram & Shmoo Analysis, Hardware-in-the-Loop (HIL), Functional & Electrical Validation, Regression & Stress Testing, Root-Cause Analysis (RCA), Requirements Traceability Matrix (RTM)

**Hardware Protocols:** Ethernet (10G/25G/100G), PCIe (Gen4/Gen5), SerDes (PAM4), SPI, I2C, UART, JTAG, MDIO, DDR, TCP/IP

**Lab Instrumentation:** Oscilloscopes, Bit Error Rate Testers (BERT), Logic Analyzers, Protocol Analyzers, Programmable Power Supplies, Thermal Chambers, Evaluation Boards (EVB)

**Programming & Automation:** Python, C, C++, Embedded Linux, PyVISA (SCPI), pytest, SQL, Pandas, NumPy, Bash

**CI/CD & Tooling:** Git, Jenkins, GitHub Actions, Docker, FastAPI, Jira, Confluence, AWS

## 💼 Experience

### Validation Engineer — Marvell Technology, Santa Clara, CA · June 2026 – Present

- Architected reusable C/C++ bring-up scripts over JTAG and MDIO for Post-Silicon Validation across 6 Ethernet (10G/25G/100G), PCIe (Gen4/Gen5), and SerDes (PAM4) EVBs, cutting Silicon Bring-Up from 9 to 3 days.
- Automated PVT Characterization, Signal Integrity, BER Testing, and Eye Diagram/Shmoo Analysis using Python and PyVISA across Oscilloscopes, BERTs, and Thermal Chambers, validating 48 lanes below 1e-12 BER in 34 hours.
- Developed SQL, Pandas, and NumPy analytics scripts correlating lane jitter against DDR traffic and rail droop, isolating 19 silicon and PCB marginalities via Root-Cause Analysis (RCA) in Jira and Confluence.
- Authored Requirements Traceability Matrices (RTM) mapping 340+ IEEE Ethernet and PCIe specifications to Protocol Analyzer checks, while enforcing peer review checklists that cut validation script review time to 8 hours.

### Validation Engineer — Accenture, Hyderabad, India · October 2022 – October 2023

- Designed a modular Hardware-in-the-Loop (HIL) validation framework in Python, pytest, and C/C++ across 14 telecom gateway benches, validating 3.5M+ daily network packets while maintaining 99.9% lab-bench uptime.
- Executed physical-layer and protocol validation on telecom router boards covering TCP/IP, Ethernet, SPI, I2C, and UART using Logic Analyzers and Protocol Analyzers, resolving 38 timing defects before carrier acceptance.
- Migrated overnight lab suites into Jenkins and Docker pipelines using Bash and Git, compressing release sign-off from 5 days to 4 hours and dropping escaped defects from 18 to 3.
- Led Root-Cause Analysis (RCA) across hardware and firmware teams in Jira and Confluence to close 65+ defects, mentoring 4 junior engineers and raising automated bench coverage from 54% to 88%.

### Associate Validation Engineer — Hexaware Technologies, Hyderabad, India · September 2021 – October 2022

- Established 480+ functional, boundary, and electrical validation test cases mapped to telecom hardware specifications via Requirements Traceability Matrices (RTM) in Jira, closing all coverage gaps before client audits.
- Scripted Python and C utilities controlling Oscilloscopes and Programmable Power Supplies to automate UART, I2C, and SPI voltage-margin sweeps across 6 controller boards, cutting validation from 24 to 6 hours.
- Consolidated log parsing and threshold alerting using Python, SQL, Pandas, and NumPy across 500K+ daily Embedded Linux soak-test logs, isolating clock-drift and watchdog-reset failures during 72-hour thermal runs.

## 🚀 Technical Projects

### [Automated PVT Characterization & Lab Instrument Control Suite](https://github.com/NagaSatyaPhanindraVallabhaneni/pvt-characterization-suite)

`Python` `PyVISA (SCPI)` `Pandas` `NumPy` `SQL` `pytest`

- Created a Python and PyVISA (SCPI) automation layer orchestrating Oscilloscopes, BERTs, and Programmable Power Supplies to run unattended voltage-temperature sweeps and generate Eye Diagram and Shmoo plots.
- Engineered a SQL, Pandas, and NumPy reporting pipeline validated with 32 pytest hardware-mock tests, reducing multi-rail characterization reporting turnaround from 8 hours to 45 minutes.

### [Telecom & Embedded Protocol Validation Harness](https://github.com/NagaSatyaPhanindraVallabhaneni/embedded-protocol-validation-harness)

`C/C++` `Python` `Embedded Linux` `UART` `SPI` `I2C` `TCP/IP` `Docker`

- Implemented a C/C++ and Python loopback stress harness on Embedded Linux injecting malformed frames, clock skew, and packet loss across UART, SPI, I2C, and TCP/IP links.
- Packaged bench runners in Docker with automated pass/fail telemetry summaries, confirming zero silent packet corruption across 1M+ continuous stress frames and edge-case error-recovery state transitions.

### [High-Throughput Hardware Telemetry & Validation Log Engine](https://github.com/NagaSatyaPhanindraVallabhaneni/hardware-telemetry-log-engine)

`Python` `FastAPI` `SQL` `Docker` `AWS` `pytest`

- Deployed a real-time lab telemetry ingestion service using FastAPI, SQL, and Docker on AWS to capture timestamped bench measurements and flag rail-voltage or BER violations automatically.
- Validated out-of-order event ingestion, historical backfill, and TTL data expiration across 59 automated pytest unit and integration tests while sustaining under 25ms p99 API response latency.

More on GitHub: [streaming-feature-store](https://github.com/NagaSatyaPhanindraVallabhaneni/streaming-feature-store) · [log-anomaly-detector](https://github.com/NagaSatyaPhanindraVallabhaneni/log-anomaly-detector) · [agentic-ai-toolkit](https://github.com/NagaSatyaPhanindraVallabhaneni/agentic-ai-toolkit) · [nl2sql-guardrails-api](https://github.com/NagaSatyaPhanindraVallabhaneni/nl2sql-guardrails-api) · [llm-evaluation-guardrails-framework](https://github.com/NagaSatyaPhanindraVallabhaneni/llm-evaluation-guardrails-framework)

## 🎓 Education

- **Master of Science in Computer Science** — University of Dayton, Dayton, OH
- **Bachelor of Technology in Electronics and Communication Engineering** — Gokaraju Rangaraju Institute of Engineering and Technology (GRIET), Hyderabad, India

## 🏅 Certifications

- AWS Certified Cloud Practitioner (2026)
- GitHub Foundations Badge (2025)
- Cisco — Introduction to Packet Tracer
- Cisco — Introduction to Cybersecurity
- NPTEL — Joy of Computing Using Python

## 📫 Let's Connect

[LinkedIn](https://www.linkedin.com/in/satyavaiengineer/) · [phanindra.vns@gmail.com](mailto:phanindra.vns@gmail.com)

*Building reliable hardware, one validated lane at a time.*
