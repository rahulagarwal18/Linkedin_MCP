import path from "node:path";
import os from "node:os";

export const CONFIG = {
  // Safe default action limits per 24-hour cycle
  dailyLimits: {
    profileViews: 50,
    connectionInvites: 15,
    messages: 15,
    posts: 3,
  },
  // Delay windows (in milliseconds) for human-like pauses
  delays: {
    minActionDelayMs: 35000, // 35 seconds
    maxActionDelayMs: 95000, // 95 seconds
    minClickDelayMs: 800,
    maxClickDelayMs: 2500,
  },
  // Dedicated user-data directory for persistent session and cookies
  userDataDir: path.join(
    os.homedir(),
    ".linkedin_mcp_browser_profile"
  ),
  dataDir: path.join(
    os.homedir(),
    ".linkedin_mcp_data"
  ),
};
