# 🛡️ LinkedIn Guardrail MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![MCP Standard](https://img.shields.io/badge/MCP-2024--11--05-green.svg)](https://modelcontextprotocol.io)
[![Playwright Stealth](https://img.shields.io/badge/Playwright-Stealth%20Anti--Ban-orange.svg)](https://github.com/berstend/puppeteer-extra)

An **anti-ban, human-paced, high-capability** Model Context Protocol (MCP) server for LinkedIn. Connects your AI agent directly to LinkedIn with native profile inspection, job searches, post publishing, and direct messaging—**without putting your account at risk**.

Built by **[Rahul Agarwal](https://github.com/rahulagarwal18)**.

---

## 📸 Architecture Overview

![LinkedIn Guardrail MCP Architecture](architecture.jpg)

---

## ⚡ Yes, Universal AI Client Support!
This MCP server implements the official **Model Context Protocol (JSON-RPC)** standard. It works out-of-the-box with:
- **Claude Desktop**
- **Cursor IDE**
- **Google Antigravity**
- **Windsurf**
- **Any MCP-compliant LLM interface**

---

## 💡 The Problem with Existing LinkedIn MCPs

When developers try to connect AI models to LinkedIn, they typically face two bad options:
1. **Official OAuth API Servers:** Extremely restricted. You can post plain text, but you **cannot** read arbitrary profiles, search jobs, or message connections.
2. **Raw Scraping / Cookie-Based Servers:** High capability, but dangerous. They require you to hunt down and copy-paste your private `li_at` session cookie into plain text files, fire rapid-fire requests in milliseconds, and get accounts flagged or restricted by LinkedIn's bot detection.

---

## 🚀 Why This MCP is Better & Safer

| Feature | Typical 3rd-Party MCPs | **LinkedIn Guardrail MCP** |
| :--- | :--- | :--- |
| **Authentication** | Insecure copy-pasting of private `li_at` cookies | **Persistent Local Chrome Profile** (Login normally once with 2FA; no credentials saved in code) |
| **Detection Defense** | Default browser automation flags exposed (`navigator.webdriver = true`) | **Playwright Stealth evasion** + realistic human reading delays |
| **Messaging Pacing** | Instant burst spam (5 requests in 2 seconds) | **Human-like pacing intervals** (30s – 90s) & direct native inbox resolution |
| **Rate Limit Protection** | None (can scrape until your account is locked) | **Daily Safety Quotas** (hard ceiling for profile views, invites, and messages) |
| **Universal Compatibility** | Often tied to one environment | **Works with Claude Desktop, Cursor, Antigravity, and any MCP client** |

---

## 🛠️ Included Tools

| Tool Name | Description |
| :--- | :--- |
| `linkedin_get_safety_status` | View real-time daily quota usage, remaining safe actions, and connection health. |
| `linkedin_search_jobs` | Search live LinkedIn jobs by title, keywords, location, and date posted. |
| `linkedin_get_profile` | Inspect public LinkedIn profiles (experience, headline, summary) with human-paced reading. |
| `linkedin_schedule_post` | Publish or queue content directly to your LinkedIn feed. |
| `linkedin_send_message` | Send a direct message to a connection by name or profile URL with automatic typeahead resolution. |
| `linkedin_queue_connection_invite` | Queue connection requests with personalized notes under safe daily caps. |

---

## 📦 Quick Setup

### 1. Clone & Install
```bash
git clone https://github.com/rahulagarwal18/Linkedin_MCP.git
cd Linkedin_MCP
npm install
npm run build
```

### 2. One-Time Secure Login
Launch the interactive login helper:
```bash
npm run login
```
A Chromium window will open. Log into LinkedIn (complete 2FA if enabled). Once you see your feed, hit `[Enter]` in the terminal. Your session profile is stored locally on your machine and never leaves your laptop.

---

## 🔌 Client Configurations

### 1. Claude Desktop
Add this to your `claude_desktop_config.json` (`%APPDATA%\Claude\claude_desktop_config.json` on Windows or `~/Library/Application Support/Claude/claude_desktop_config.json` on Mac):

```json
{
  "mcpServers": {
    "linkedin": {
      "command": "node",
      "args": [
        "/path/to/Linkedin_MCP/dist/index.js"
      ]
    }
  }
}
```

### 2. Cursor IDE
In Cursor settings under **Features → MCP Servers → Add New MCP Server**:
- **Name:** `linkedin`
- **Type:** `command`
- **Command:** `node /path/to/Linkedin_MCP/dist/index.js`

### 3. Google Antigravity
Add to `~/.gemini/config/mcp_config.json`:
```json
{
  "mcpServers": {
    "linkedin": {
      "command": "node",
      "args": [
        "/path/to/Linkedin_MCP/dist/index.js"
      ]
    }
  }
}
```

---

## ⚖️ License
MIT License. Created by [Rahul Agarwal](https://github.com/rahulagarwal18).
