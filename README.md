# Naga Satya Phanindra Vallabhaneni

**Embedded Software Engineer** · Dayton, OH · +1 (984) 687-6001 · [phanindra.vns@gmail.com](mailto:phanindra.vns@gmail.com) · [LinkedIn](https://www.linkedin.com/in/nagasatyaphanindravallabhaneni/)

> Embedded Software Engineer with an M.S. in Computer Science, a B.Tech in Electronics and Communication Engineering, and 3.5+ years of experience developing bare-metal firmware, Embedded Linux BSPs, RTOS applications, and low-level hardware drivers for networking and telecom systems. Experienced in C/C++, ARM Cortex architectures, Linux Kernel/U-Boot bring-up, DMA/ISR optimization, and high-speed interfaces (Ethernet, PCIe, SerDes, SPI, I2C, UART, JTAG) with hands-on hardware-firmware debugging using GDB, Oscilloscopes, and Logic Analyzers.

🛂 Authorized to work in the US on **OPT EAD** · will require future **H-1B sponsorship** · Open to full-time Embedded / Firmware roles in the USA

## 🛠️ Technical Skills

**Languages:** C (C99/C11), C++ (C++14/17), Python, Bash/Shell, SQL

**Embedded Systems & OS:** Embedded Linux, Linux Kernel Drivers (Network/Character), FreeRTOS, Bare-Metal Firmware, Yocto Project, U-Boot, Device Tree (DTS), Board Support Packages (BSP), Hardware Abstraction Layer (HAL)

**Architecture & Low-Level Systems:** ARM Cortex-A/M, SoC Bring-Up, Zero-Copy DMA, Interrupt Service Routines (ISR), DDR Memory Timing, Multi-Threading, Lock-Free Queues, Watchdog Timers, State Machines, Power/Brown-Out Management

**Protocols & Interfaces:** Ethernet (10G/25G/100G), PCIe (Gen4/Gen5), SerDes, MDIO, SPI, I2C, UART, GPIO, JTAG/SWD, TCP/IP

**Hardware Bring-Up & Debugging:** GDB, OpenOCD, Oscilloscopes, Logic Analyzers, Protocol Analyzers, Programmable Power Supplies, Hardware-in-the-Loop (HIL), Static Code Analysis

**CI/CD & Tooling:** GCC, CMake, Make, Cross-Compilation, Git, Jenkins, GitHub Actions, Docker, pytest, FastAPI, AWS, Jira, Confluence

## 💼 Experience

### Embedded Software Engineer — Marvell Technology, Santa Clara, CA · June 2026 – Present

- Architected bare-metal and Embedded Linux Board Support Packages (BSP), U-Boot bootloaders, and Device Tree overlays in C and C++ across 6 ARM Cortex SoC evaluation boards, choosing modular HAL abstractions over board-specific forks to cut new silicon bring-up from 9 to 3 days.
- Engineered interrupt-driven Linux Kernel drivers for Ethernet (10G/25G/100G), PCIe (Gen4/Gen5), MDIO, and SerDes PHYs using zero-copy DMA ring buffers instead of polled I/O, lowering CPU utilization by 38% while sustaining line-rate packet throughput.
- Debugged DDR memory timing faults, rail-droop resets, and bus contention via JTAG, GDB, and Oscilloscopes, isolating 19 silicon-firmware race conditions and documenting hardware workarounds in Jira and Confluence.
- Standardized firmware static analysis and peer review gates in Git and GitHub Actions mapped to 340+ IEEE Ethernet and PCIe specifications, reducing PR review turnaround from 3 days to 8 hours.

### Embedded Systems Engineer — Accenture, Hyderabad, India · October 2022 – October 2023

- Developed multi-threaded C++ and FreeRTOS firmware for 14 telecom gateway controllers, decoupling time-critical packet-forwarding tasks from management threads via lock-free queues to handle 3.5M+ daily TCP/IP packets at 99.9% uptime.
- Implemented deterministic SPI, I2C, and UART peripheral drivers with hardware CRC checks and exponential backoff retries, verifying timing margins on Logic Analyzers and Protocol Analyzers to resolve 38 field-blocking bus defects.
- Containerized cross-compilation (GCC, CMake) and Hardware-in-the-Loop (HIL) firmware regression suites in Jenkins, Docker, and Bash using Python and pytest, compressing release qualification from 5 days to 4 hours and dropping escaped firmware defects from 18 to 3.
- Led cross-functional Root-Cause Analysis (RCA) across hardware and firmware teams in Jira and Confluence to close 65+ defects, mentoring 4 junior engineers and raising automated firmware test coverage from 54% to 88%.

### Associate Embedded Engineer — Hexaware Technologies, Hyderabad, India · September 2020 – October 2022

- Built low-level C firmware drivers for UART, I2C, SPI, and GPIO peripherals across 6 telecom controller boards, refactoring blocking busy-wait loops into ISR-driven state machines to keep worst-case interrupt latency under 15 µs.
- Designed Watchdog Timer recovery routines and brown-out detection handlers validated with Oscilloscopes and Programmable Power Supplies, eliminating silent system hangs across 72-hour thermal soak tests.
- Wrote Python and SQL diagnostic parsers processing 500K+ daily Embedded Linux kernel and syslog entries, isolating clock-drift anomalies and memory leaks prior to carrier acceptance audits.

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

[LinkedIn](https://www.linkedin.com/in/nagasatyaphanindravallabhaneni/) · [phanindra.vns@gmail.com](mailto:phanindra.vns@gmail.com)

*Building reliable firmware, from bare metal to boot.*
