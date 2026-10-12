import readline from "node:readline";
import { BrowserEngine } from "./browser.js";

async function runLogin() {
  console.log("==================================================");
  console.log("   LinkedIn MCP: Browser Authentication Setup    ");
  console.log("==================================================");
  console.log("Opening an interactive Chromium window with persistent profile...");
  console.log("Please log in to your LinkedIn account manually (including 2FA if prompted).");
  console.log("Your cookies and session will be saved locally so Claude/Antigravity won't trigger re-logins.\n");

  const engine = new BrowserEngine();
  const page = await engine.getPage(false);

  await page.goto("https://www.linkedin.com/login", { waitUntil: "domcontentloaded" });

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  await new Promise<void>((resolve) => {
    rl.question("Press [Enter] here in terminal AFTER you have successfully logged in in the browser window: ", () => {
      rl.close();
      resolve();
    });
  });

  await engine.humanDelay(1500, 2500);
  const status = await engine.checkAuthStatus(page);

  if (status.authenticated) {
    console.log("\n[SUCCESS] LinkedIn session detected! Credentials saved in your local profile.");
    console.log("You can now connect this MCP server to Claude Desktop or Antigravity.");
  } else {
    console.log(`\n[WARNING] ${status.message}`);
    console.log("If needed, run 'npm run login' again once your network/login is ready.");
  }

  await engine.close();
  process.exit(0);
}

runLogin().catch((err) => {
  console.error("Error during login setup:", err);
  process.exit(1);
});
