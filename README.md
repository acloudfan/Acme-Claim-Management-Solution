<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/rsakhuja/Acme-Claim-Management-Solution">
    <img src="src/common/assets/ACME-logo.png" alt="ACME Logo" width="80" height="80">
  </a>

  <h3 align="center">ACME Insurance - AI Claims Management System</h3>

  <p align="center">
    Demonstration of AI-based auto claim adjudication that reduces claim processing time from days to minutes
    <br />
    <a href="specifications/"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="#demo-scenarios">View Demo Scenarios</a>
    ·
    <a href="https://github.com/rsakhuja/Acme-Claim-Management-Solution/issues">Report Bug</a>
    ·
    <a href="https://github.com/rsakhuja/Acme-Claim-Management-Solution/issues">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#key-features">Key Features</a></li>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#configuration">Configuration</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#demo-scenarios">Demo Scenarios</a></li>
    <li><a href="#documentation">Documentation</a></li>
    <li><a href="#faq">FAQ</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project
This project builds a complete **AI-powered auto insurance claims management system** with multiple portals serving different stakeholders. It showcases how AI can streamline insurance claims processing through automated damage detection, fraud analysis, cost estimation, and intelligent routing. The system demonstrates reducing claim processing time from days to minutes while maintaining accuracy and fraud prevention.

**What Gets Built:**
- **Admin Portal** (shown below) - Central configuration hub for managing AI thresholds, business rules, and launching all portals
- **FastAPI Backend** - REST API with AI agents for damage detection (YOLO), fraud analysis (VLM), cost estimation, and customer chatbot
- **Customer Portal** - Self-service claim filing with photo upload, real-time AI damage analysis, and instant estimates
- **Adjustor Portal** - Review flagged claims, manual damage assessment, fraud investigation, and estimate adjustments
- **Executive Portal** - Analytics dashboards with KPIs, fraud metrics, and 6-month historical insights

The screenshot below shows the **Admin Portal**, which serves as the central configuration hub where users can manage system settings and launch the three operational portals for auto insurance customers, insurance adjustors, and executives.

**Key Technologies**: YOLO damage detection, Vision Language Models for fraud detection, multi-portal architecture for different user roles.

[![ACME Admin Portal][product-screenshot]](https://github.com/rsakhuja/Acme-Claim-Management-Solution)




### Key Features

* **Real-time Damage Detection** - YOLO v8 analyzes vehicle damage during image upload
* **AI Fraud Detection** - Detects make/model mismatches and AI-generated images
* **Instant Cost Estimation** - Automated repair cost calculation based on AI damage analysis
* **Customer Chatbot** - Claude-powered assistant with RAG for policy questions
* **Human Review Workflow** - Seamless handoff to adjustors for complex cases
* **Executive Analytics** - Comprehensive dashboards with 6-month historical insights
* **Configurable Business Rules** - Real-time parameter adjustments via Admin Portal
* **Complete Audit Trail** - Track all claim activities and decisions

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* [![Python][Python.org]][Python-url]
* [![FastAPI][FastAPI.com]][FastAPI-url]
* [![React][React.js]][React-url]
* [![Vite][Vite.js]][Vite-url]
* [![TailwindCSS][Tailwind.com]][Tailwind-url]
* [![SQLite][SQLite.org]][SQLite-url]
* [![AWS][AWS.amazon.com]][AWS-url]
* [![Anthropic][Anthropic.com]][Anthropic-url]

These components were chosen for speed and ease of development. **SQLite** simplifies setup and cleanup during prototyping with zero configuration. **FastAPI** and **Vite** provide hot-reloading, allowing code changes to reflect instantly without server restarts—critical for rapid iteration. Since UI is essential for effective demos, **React** and **TailwindCSS** enable building polished interfaces quickly with reusable components. 

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

Complete setup in 5 steps to get your local environment running.

### Prerequisites

* **Python 3.11+**
  ```bash
  python3 --version  # Should be 3.11 or higher
  ```

* **uv** (Python Package Manager)
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  uv --version
  ```

* **Node.js 18+ and npm 9+**
  ```bash
  node --version  # Should be v18.x or higher
  npm --version   # Should be 9.x or higher
  ```

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/rsakhuja/Acme-Claim-Management-Solution.git
   cd Acme-Claim-Management-Solution
   ```

2. Install UI dependencies for all portals
   ```bash
   ./scripts/install-ui-dependencies.sh --clean
   ```

3. Create `.env` file with your LLM provider API keys
   ```bash
   touch .env
   ```

4. Add at least one LLM provider configuration to `.env`:

   **AWS Bedrock (Default)**
   ```env
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_DEFAULT_REGION=us-east-1
   ```
   
   > **Note**: If you already have AWS credentials in `~/.aws/credentials`, you can skip adding AWS variables to `.env`. The system checks `~/.aws/credentials` first, then falls back to `.env`.

   **Anthropic Claude**
   ```env
   ANTHROPIC_API_KEY=sk-ant-api03-your_key_here
   ```

   **OpenAI**
   ```env
   OPENAI_API_KEY=sk-your_key_here
   ```

5. Start the API server
   ```bash
   ./scripts/start-api-server.sh --clean
   ```
   
   > **Note**: Wait for the API server to start before proceeding to the next step. You will see the message in console: "INFO:     Application startup complete."

6. Start all UI portals
   ```bash
   ./scripts/start-portals.sh
   ```

7. Open the Admin portal in your browser
   ```
   http://localhost:5170/dashboard
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Configuration

The system uses **AWS Bedrock** by default. To switch LLM providers:

**Method 1: Configuration File**
```yaml
# Edit api-config.yaml
llm:
  default_provider: "anthropic"  # Options: "bedrock" | "anthropic" | "openai"
```

**Method 2: Admin Portal**
1. Open http://localhost:5170
2. Navigate to **Technical Parameters**
3. Select provider from **Default LLM Provider** dropdown
4. Click **Save Configuration** (changes take effect immediately)

For detailed configuration options, see [Configuration Management](#configuration-management) in the full documentation.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE -->
## Usage

### Access the Portals

* **Customer Portal**: http://localhost:5173 - File claims, upload damage photos, chat with AI assistant
* **Adjustor Portal**: http://localhost:5174 - Review flagged claims, adjust estimates, fraud analysis
* **Admin Portal**: http://localhost:5170 - Configure AI thresholds, manage business rules
* **Executive Portal**: http://localhost:5175 - View analytics dashboards and KPIs

**Default password for all portals**: `password`

### What's Built

**Backend API (FastAPI)**
- YOLO-based damage detection (real-time during upload)
- AI fraud detection (VLM + multi-signal analysis)
- Cost estimation engine
- Customer chatbot (Claude + RAG)
- Complete claim lifecycle management

**Customer Portal**
- File claims with photo upload
- Real-time AI damage analysis
- Instant repair estimates
- Appeal decisions
- Mobile QR code support

**Adjustor Portal**
- Review flagged claims
- Manual damage assessment
- Fraud signal analysis
- Cost estimate adjustments
- SOP reference viewer

**Admin Portal**
- Configure AI thresholds
- Toggle fraud detection features
- Manage business rules
- View demo scenarios

**Executive Portal**
- 6-month historical analytics
- KPI dashboards
- Fraud detection metrics
- Cost savings analysis

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## AI Enabled Claims Process Flow

The video below walks throught AI enabled claim process implemented in the prototype.

[![Process flow](https://img.youtube.com/vi/htb47B7IDjw/0.jpg)](https://www.youtube.com/watch?v=htb47B7IDjw)


<a href="https://youtu.be/htb47B7IDjw">
  <img src="https://img.youtube.com/vi/htb47B7IDjw/0.jpg" alt="AI Claims Process Demo" width="560" />
</a>

<!-- DEMO SCENARIOS -->
## Demo Scenarios

Test images are provided in the `images/` directory. Use these when filing claims through the Customer Portal.

### 1. Happy Path - Auto-Approved
- **Customer**: John Doe (#100)
- **Vehicle**: 2015 Toyota Corolla (Red)
- **Image**: `images/red-toyota-2015-rear-end-damage.png`
- **Expected**: Auto-approved with AI estimate
- **Outcome**: Customer accepts estimate

### 2. Customer Appeal - Human Review
- **Customer**: Jane Smith (#101)
- **Vehicle**: 2006 BMW 1 Series E87 (Silver)
- **Image**: `images/bmw-silver-2006-front-damaged.png`
- **Expected**: AI estimate presented, customer appeals
- **Appeal Reason**: "Radiator seems to be damaged beyond repair"
- **Outcome**: Adjustor adds manual damage and revises estimate

### 3. Fraud Detection - Make Mismatch
- **Customer**: Bob Johnson (#102)
- **Vehicle**: 2012 Chevy Silverado (Red)
- **Images**: `images/red-ford-f150-ai-generated-damage.jpg` (Ford F-150)
- **Expected**: Fraud signals detected (Chevy ≠ Ford)
- **Outcome**: Routed to adjustor for fraud review

### 4. Fraud Detection - AI Generated Image
- **Customer**: Alice Williams (#103)
- **Vehicle**: 2022 Honda Accord (Black)
- **Image**: `images/honda-acord-ex-2022-ai-generated-damage.jpg`
- **Expected**: AI-generated damage detected by VLM
- **Outcome**: Routed to fraud review with AI generation analysis

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- DOCUMENTATION -->
## Documentation

- [Quick Start Guide](specifications/QUICK-START-UV.md)
- [API Design](specifications/API-BACKEND-DESIGN.md)
- [Customer Portal](specifications/UI-CUSTOMER-PORTAL-DESIGN.md)
- [Adjustor Portal](specifications/UI-ADJUSTOR-PORTAL-DESIGN.md)
- [Admin Portal](specifications/UI-ADMIN-PORTAL-DESIGN.md)
- [Executive Portal](specifications/UI-EXECUTIVES-PORTAL-DESIGN.md)
- [SOP - Damage Triage](specifications/policies/sop_damage_triage.md)
- [Dependency Management](DEPENDENCY-MANAGEMENT.md)
- [Portal Setup Guide](PORTAL-SETUP-GUIDE.md)

### Technical Diagrams

- [AI-Powered Claim Flow](specifications/diagrams/claim-flow-with-ai.mmd)
- [Traditional Claims Process](specifications/diagrams/traditional-claims.mmd)
- [Claim State Machine](specifications/diagrams/claims-state-machine.mmd)
- [Image Upload Flow](specifications/diagrams/claim_image_upload.mmd)
- [Fraud Detection Agent](specifications/diagrams/customer-fraud-ai-agent.mmd)
- [Database ERD](specifications/diagrams/claim-database-erd.mmd)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- FAQ -->
## FAQ

**Q: How long did it take to build this prototype?**

A: Approximately 2 days, with most time spent waiting for Claude to finish thinking.

**Q: Is this production-ready?**

A: No, this is a demonstration and starting point. Production use requires enhanced security, scalability, compliance, and integration with existing systems.

**Q: Can I use my own images?**

A: Yes! Upload any clear vehicle damage photos through the Customer Portal.

**Q: Which YOLO version is used?**

A: YOLO v8 from HuggingFace (vineetsarpal/yolov11n-car-damage), pre-trained on vehicle damage datasets.

**Q: Is the Executive Portal data real?**

A: No, it uses synthetically generated data based on auto industry averages to demonstrate analytics capabilities.

**Q: How do I completely reset and start fresh?**

A:
```bash
# Clean UI dependencies
./scripts/install-ui-dependencies.sh --clean

# Clean API and database
./scripts/start-api-server.sh --clean
```

For more FAQs, see the [full documentation](README-1.md#faq).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` file for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Raj - [raj@acloudfan.com](raj@acloudfan.com)

Project Link: [https://github.com/acloudfan/Acme-Claim-Management-Solution](https://github.com/acloudfan/Acme-Claim-Management-Solution)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Car Damage Assessment AI](https://github.com/artemxdata/Car-Damage-Assessment-AI)
* [AAA Mechanic Labor Rates](https://www.aaa.com/autorepair/articles/average-mechanic-labor-rate-repair-costs-in-your-state-2026)
* [COCO Car Damage Dataset](https://www.kaggle.com/datasets/lplenka/coco-car-damage-detection-dataset)
* [Mitchell International](https://www.mitchell.com/) - Industry standard repair time database
* [CCC Intelligent Solutions](https://cccis.com/) - Claims and collision repair platform
* [Best-README-Template](https://github.com/othneildrew/Best-README-Template)
* [Claude Code](https://claude.com/claude-code) - AI-assisted development

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
[license-shield]: https://img.shields.io/github/license/rsakhuja/Acme-Claim-Management-Solution.svg?style=for-the-badge
[license-url]: https://github.com/rsakhuja/Acme-Claim-Management-Solution/blob/main/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/rsakhuja
[product-screenshot]: docs/images/admin-portal.png
[Python.org]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://python.org/
[FastAPI.com]: https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white
[FastAPI-url]: https://fastapi.tiangolo.com/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vite.js]: https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white
[Vite-url]: https://vitejs.dev/
[Tailwind.com]: https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white
[Tailwind-url]: https://tailwindcss.com/
[SQLite.org]: https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white
[SQLite-url]: https://sqlite.org/
[AWS.amazon.com]: https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white
[AWS-url]: https://aws.amazon.com/
[Anthropic.com]: https://img.shields.io/badge/Anthropic-191919?style=for-the-badge&logo=anthropic&logoColor=white
[Anthropic-url]: https://anthropic.com/
