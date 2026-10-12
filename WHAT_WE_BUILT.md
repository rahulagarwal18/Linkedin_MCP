# Connecting AI (Claude & Antigravity) with LinkedIn Safely: What We Built and Why

## 1. The Real Problem With Existing Options
When people want an AI like Claude to help them on LinkedIn, they usually hit a roadblock: **There is no official LinkedIn tool (MCP) available.**

Because of that, people are forced to pick between two flawed alternatives:
1. **The "Official API" tools:** They are safe from bans, but they can barely do anything. You can publish a simple text post, but you cannot search jobs, read user profiles, or send messages.
2. **The "Raw Scraper" tools:** They do everything, but they act like aggressive robots. They ask you for secret session cookies, send requests instantly in bursts, and very quickly get LinkedIn accounts flagged, restricted, or permanently banned.

We didn’t want to choose between **"safe but useless"** and **"powerful but banned"**. So we built a balanced, human-paced approach.

---

## 2. What We Actually Built
We created a custom connector (an MCP server) that sits right on your computer. When you ask Claude or Antigravity to do something on LinkedIn, it doesn’t blast LinkedIn with high-speed automated requests. 

Instead, it acts like a thoughtful human assistant sitting at a real browser:
- It uses a **normal browser profile** that stays logged in locally, just like your daily Chrome browser.
- It puts actions into a **waiting line (queue)** with random, natural pauses.
- It keeps track of how much you've done each day and **stops when you reach safe limits**.

---

## 3. Why This Is Better & Safer Than Typical 3rd-Party Tools

### 1. No Stealing or Pasting Session Cookies
- **Other tools:** Force you to go into your browser developer tools, hunt down a secret cookie (`li_at`), and copy-paste it into config files. If someone gets that cookie or if you paste it in the wrong place, your account is exposed.
- **Our tool:** Opens a real browser window once. You log in yourself with your password and Two-Factor Authentication (2FA). It saves your regular login state locally on your own computer, exactly like opening Chrome tomorrow.

### 2. Natural Pacing (Anti-Burst Protection)
- **Other tools:** When asked to message 5 people or connect with candidates, they fire all 5 requests in 2 seconds. LinkedIn’s security system instantly recognizes this as a bot.
- **Our tool:** Has a built-in waiting room. When Claude queues a connection or message, the server waits a random human duration (30 to 90 seconds) between actions.

### 3. Built-In Daily Speed Limits
- **Other tools:** Have no brakes. If you or an AI accidentally loop a command, it will scrape 500 profiles and LinkedIn will restrict your account.
- **Our tool:** Has hard daily caps (e.g., maximum 15 connection invites, 15 messages, and 50 profile views per day). Once you hit the safety ceiling, it politely pauses and tells Claude: *"We've reached today's safe limit. Try again tomorrow."*

### 4. Works Universally
- You can plug this exact tool into **Claude Desktop**, **Antigravity**, **Cursor**, or any other AI app that supports MCP standards.

---

## 4. What Features You Get

1. **Job Search:** Ask Claude to find AI or developer jobs in specific locations, and it brings back the titles, companies, and links.
2. **Profile Reading:** Claude can look up a profile to help you understand a person’s background before a meeting or interview.
3. **Drafting & Scheduling Posts:** Create content with Claude and schedule it to publish to your feed without manually copying and pasting.
4. **Paced Direct Messages:** Prepare messages to contacts that go out naturally one by one with safe waiting intervals.
5. **Connection Requests with Notes:** Queue invitations to connect with custom personalized notes at a safe, human rhythm.
6. **Safety Dashboard Check:** Ask Claude: *"How much quota do I have left today?"* and it will tell you exactly what you’ve used and what is safe to do next.

---

## 5. Honest Facts About Safety (What You Should Know)
We want to be completely honest:
- **Is this endorsed by LinkedIn?** No. LinkedIn does not officially support AI browser helpers on personal accounts.
- **Can any tool guarantee 100% zero risk?** No tool that automates browser actions can promise absolute zero risk, because LinkedIn regularly updates its detection rules.
- **Why is this the safest practical choice?** Because it mimics real human browsing habits (natural delays, persistent local logins, daily quotas) rather than acting like an aggressive scraper. As long as you stay within the built-in limits, your risk is kept as low as technically possible.
