import { chromium } from "playwright-extra";
import stealthPlugin from "puppeteer-extra-plugin-stealth";
import type { BrowserContext, Page } from "playwright";
import { CONFIG } from "./config.js";

chromium.use(stealthPlugin());

export class BrowserEngine {
  private context: BrowserContext | null = null;
  private page: Page | null = null;
  private isInitializing: boolean = false;

  public async getContext(headless: boolean = false): Promise<BrowserContext> {
    if (this.context) {
      try {
        // Quick health check to see if context is still active
        this.context.pages();
        return this.context;
      } catch {
        this.context = null;
        this.page = null;
      }
    }

    if (this.isInitializing) {
      while (this.isInitializing) {
        await new Promise((r) => setTimeout(r, 100));
      }
      if (this.context) return this.context;
    }

    this.isInitializing = true;
    try {
      this.context = await chromium.launchPersistentContext(CONFIG.userDataDir, {
        headless,
        viewport: { width: 1366, height: 768 },
        userAgent:
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        args: [
          "--disable-blink-features=AutomationControlled",
          "--no-sandbox",
          "--disable-setuid-sandbox",
          "--disable-infobars",
          "--disable-dev-shm-usage",
          "--no-first-run",
          "--no-default-browser-check",
        ],
      });

      this.context.on("close", () => {
        this.context = null;
        this.page = null;
      });

      return this.context;
    } finally {
      this.isInitializing = false;
    }
  }

  public async getPage(headless: boolean = false): Promise<Page> {
    if (this.page && !this.page.isClosed()) {
      return this.page;
    }

    const ctx = await this.getContext(headless);
    const pages = ctx.pages();
    this.page = pages.length > 0 ? pages[0] : await ctx.newPage();

    this.page.setDefaultTimeout(30000);
    this.page.setDefaultNavigationTimeout(35000);

    return this.page;
  }

  public async humanDelay(minMs = 1200, maxMs = 3200): Promise<void> {
    const ms = Math.floor(Math.random() * (maxMs - minMs + 1)) + minMs;
    await new Promise((resolve) => setTimeout(resolve, ms));
  }

  public async simulateHumanReading(page: Page): Promise<void> {
    try {
      // Natural small scroll down and up
      await page.mouse.wheel(0, Math.floor(Math.random() * 300) + 200);
      await this.humanDelay(800, 1500);
      await page.mouse.wheel(0, -Math.floor(Math.random() * 150) + 50);
      await this.humanDelay(500, 1000);
    } catch {
      // Ignore if page closed or frame detached
    }
  }

  public async checkAuthStatus(page: Page): Promise<{ authenticated: boolean; checkpoint: boolean; message: string }> {
    const url = page.url();
    if (url.includes("/checkpoint") || url.includes("/challenge")) {
      return {
        authenticated: false,
        checkpoint: true,
        message: "LinkedIn presented a security checkpoint or captcha challenge. Please complete it in your browser window.",
      };
    }
    if (url.includes("/login") || url.includes("/authwall") || url.includes("/signup")) {
      return {
        authenticated: false,
        checkpoint: false,
        message: "Not logged in to LinkedIn. Please run 'npm run login' to establish a persistent session.",
      };
    }
    return {
      authenticated: true,
      checkpoint: false,
      message: "Session is active and healthy.",
    };
  }

  public async close(): Promise<void> {
    if (this.context) {
      try {
        await this.context.close();
      } catch {
        // Safe ignore
      }
      this.context = null;
      this.page = null;
    }
  }
}
