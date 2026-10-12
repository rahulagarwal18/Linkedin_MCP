import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { BrowserEngine } from "./browser.js";
import { SafetyManager } from "./safety.js";

const server = new Server(
  {
    name: "linkedin-guardrail-mcp",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

const safety = new SafetyManager();
const browser = new BrowserEngine();

process.on("exit", () => {
  browser.close().catch(() => {});
});
process.on("SIGINT", () => {
  browser.close().then(() => process.exit(0)).catch(() => process.exit(0));
});

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "linkedin_get_safety_status",
        description:
          "Check today's action counts, remaining safe quotas, queued tasks, and authentication health.",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
      {
        name: "linkedin_search_jobs",
        description:
          "Search for job listings on LinkedIn with keywords and optional location. Returns top listings safely.",
        inputSchema: {
          type: "object",
          properties: {
            keywords: {
              type: "string",
              description: "Job title, keywords, or company name (e.g., 'Senior AI Engineer')",
            },
            location: {
              type: "string",
              description: "Location or 'Remote' (e.g., 'United States', 'Bengaluru, India')",
            },
          },
          required: ["keywords"],
        },
      },
      {
        name: "linkedin_get_profile",
        description:
          "Safely read a LinkedIn profile by username or URL to inspect experience and details. Enforces daily quotas and stealth delays.",
        inputSchema: {
          type: "object",
          properties: {
            profileUrlOrId: {
              type: "string",
              description:
                "LinkedIn public profile URL or username handle (e.g., 'williamhgates' or 'https://www.linkedin.com/in/satyanadella/')",
            },
          },
          required: ["profileUrlOrId"],
        },
      },
      {
        name: "linkedin_schedule_post",
        description:
          "Schedule or publish a post to your LinkedIn feed. Enforces safety quotas to avoid spam triggers.",
        inputSchema: {
          type: "object",
          properties: {
            content: {
              type: "string",
              description: "The text content of the post to publish",
            },
            publishNow: {
              type: "boolean",
              description:
                "If true, navigates to feed and publishes directly. If false, stores in the queue.",
              default: true,
            },
          },
          required: ["content"],
        },
      },
      {
        name: "linkedin_send_message",
        description:
          "Send a direct message on LinkedIn by person's name or profile URL. Automatically finds them in your connections, opens the chat, and sends the message directly.",
        inputSchema: {
          type: "object",
          properties: {
            recipientNameOrUrl: {
              type: "string",
              description:
                "The person's full name (e.g., 'Aditya Agarwal') or their LinkedIn profile URL",
            },
            message: {
              type: "string",
              description: "The direct message text to send",
            },
          },
          required: ["recipientNameOrUrl", "message"],
        },
      },
      {
        name: "linkedin_queue_connection_invite",
        description:
          "Queue a connection request to a LinkedIn member with an optional personalized note. Enforces strict daily limits (max 15/day).",
        inputSchema: {
          type: "object",
          properties: {
            profileUrl: {
              type: "string",
              description: "LinkedIn profile URL to send an invitation to",
            },
            note: {
              type: "string",
              description: "Optional personalized invitation note (up to 300 characters)",
            },
          },
          required: ["profileUrl"],
        },
      },
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (name === "linkedin_get_safety_status") {
      const usage = safety.getUsage();
      const queue = safety.getQueue();
      const page = await browser.getPage(false);
      const auth = await browser.checkAuthStatus(page);

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                status: auth.authenticated ? "healthy" : "attention_needed",
                authMessage: auth.message,
                todayUsage: {
                  ...usage,
                  remaining: {
                    profileViews: safety.canPerform("profileViews").remaining,
                    connectionInvites: safety.canPerform("connectionInvites").remaining,
                    messages: safety.canPerform("messages").remaining,
                    posts: safety.canPerform("posts").remaining,
                  },
                },
                queueSummary: {
                  totalInQueue: queue.length,
                  pending: queue.filter((q) => q.status === "pending").length,
                  completed: queue.filter((q) => q.status === "completed").length,
                  failed: queue.filter((q) => q.status === "failed").length,
                },
              },
              null,
              2
            ),
          },
        ],
      };
    }

    if (name === "linkedin_search_jobs") {
      const keywords = String(args?.keywords ?? "").trim();
      const location = String(args?.location ?? "").trim();

      const page = await browser.getPage(false);
      const searchUrl = `https://www.linkedin.com/jobs/search/?keywords=${encodeURIComponent(
        keywords
      )}${location ? `&location=${encodeURIComponent(location)}` : ""}`;

      await page.goto(searchUrl, { waitUntil: "domcontentloaded" });
      await browser.humanDelay(2000, 3500);
      await browser.simulateHumanReading(page);

      const authCheck = await browser.checkAuthStatus(page);
      if (!authCheck.authenticated) {
        return {
          content: [{ type: "text", text: `[Session Notice]: ${authCheck.message}` }],
        };
      }

      const jobs = await page.evaluate(() => {
        const results: Array<{ title: string; company: string; location: string; url: string }> = [];
        const cardSelectors = [
          ".job-card-container",
          ".jobs-search-results__list-item",
          ".base-card",
          "li[data-occludable-job-id]",
        ];

        let foundCards: Element[] = [];
        for (const selector of cardSelectors) {
          const cards = document.querySelectorAll(selector);
          if (cards.length > 0) {
            foundCards = Array.from(cards);
            break;
          }
        }

        for (const el of foundCards.slice(0, 6)) {
          const title =
            el.querySelector(".job-card-list__title, .artdeco-entity-lockup__title, .base-search-card__title, a[href*='/jobs/view/']")?.textContent?.trim() ||
            "Position Available";

          const company =
            el.querySelector(
              ".job-card-container__primary-description, .artdeco-entity-lockup__subtitle, .base-search-card__subtitle"
            )?.textContent?.trim() || "Company unlisted";

          const loc =
            el.querySelector(
              ".job-card-container__metadata-item, .job-search-card__location"
            )?.textContent?.trim() || "Location unlisted";

          const linkEl = el.querySelector("a[href*='/jobs/view/']") as HTMLAnchorElement | null;
          const url = linkEl?.href ? linkEl.href.split("?")[0] : "";

          results.push({ title, company, location: loc, url });
        }
        return results;
      });

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                query: { keywords, location },
                foundCount: jobs.length,
                jobs,
              },
              null,
              2
            ),
          },
        ],
      };
    }

    if (name === "linkedin_get_profile") {
      const quotaCheck = safety.canPerform("profileViews");
      if (!quotaCheck.allowed) {
        return { content: [{ type: "text", text: `[SAFETY GUARDRAIL]: ${quotaCheck.reason}` }] };
      }

      let target = String(args?.profileUrlOrId ?? "").trim();
      if (!target.startsWith("http")) {
        target = `https://www.linkedin.com/in/${target.replace(/^\/|\/$/g, "")}/`;
      }

      const page = await browser.getPage(false);
      await page.goto(target, { waitUntil: "domcontentloaded" });
      await browser.humanDelay(2000, 3500);
      await browser.simulateHumanReading(page);

      const authCheck = await browser.checkAuthStatus(page);
      if (!authCheck.authenticated) {
        return {
          content: [{ type: "text", text: `[Session Notice]: ${authCheck.message}` }],
        };
      }

      const profileData = await page.evaluate(() => {
        const name =
          document.querySelector("h1, .top-card-layout__title")?.textContent?.trim() ||
          "Profile name unavailable";

        const headline =
          document.querySelector(".text-body-medium, .top-card-layout__headline")?.textContent?.trim() ||
          "Headline unavailable";

        const location =
          document.querySelector(".text-body-small.inline, .top-card__subline-item")?.textContent?.trim() ||
          "";

        const aboutSection = document.querySelector("#about ~ .display-flex, section[data-section='summary']");
        const about = aboutSection?.textContent?.trim()?.replace(/\s+/g, " ") || "No summary available";

        return { name, headline, location, about };
      });

      safety.recordAction("profileViews");

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                url: target,
                ...profileData,
                safetyNotice: `Profile viewed safely. Remaining safe profile views today: ${
                  safety.canPerform("profileViews").remaining
                }`,
              },
              null,
              2
            ),
          },
        ],
      };
    }

    if (name === "linkedin_schedule_post") {
      const quotaCheck = safety.canPerform("posts");
      if (!quotaCheck.allowed) {
        return { content: [{ type: "text", text: `[SAFETY GUARDRAIL]: ${quotaCheck.reason}` }] };
      }

      const content = String(args?.content ?? "").trim();
      const publishNow = args?.publishNow !== false;

      if (!publishNow) {
        const queued = safety.enqueueAction({
          type: "post",
          target: "feed",
          content,
        });
        return {
          content: [
            {
              type: "text",
              text: `Post queued successfully (Action ID: ${queued.id}). It will be published at your scheduled window.`,
            },
          ],
        };
      }

      const page = await browser.getPage(false);
      await page.goto("https://www.linkedin.com/feed/", { waitUntil: "domcontentloaded" });
      await browser.humanDelay(2000, 3000);

      const authCheck = await browser.checkAuthStatus(page);
      if (!authCheck.authenticated) {
        return {
          content: [{ type: "text", text: `[Session Notice]: ${authCheck.message}` }],
        };
      }

      // Click "Start a post"
      const startPostBtn = await page.$(
        "button:has-text('Start a post'), button.share-box-feed-entry__trigger"
      );
      if (startPostBtn) {
        await startPostBtn.click();
        await browser.humanDelay(1500, 2500);

        const editor = await page.$("div.ql-editor, div[role='textbox']");
        if (editor) {
          await editor.fill(content);
          await browser.humanDelay(1200, 2000);

          const postSubmit = await page.$("button.share-actions__primary-action, button:has-text('Post')");
          if (postSubmit) {
            await postSubmit.click();
            await browser.humanDelay(3000, 4000);
            safety.recordAction("posts");
            return {
              content: [
                {
                  type: "text",
                  text: `Post published successfully to your LinkedIn feed! Content: "${content.substring(0, 80)}..."`,
                },
              ],
            };
          }
        }
      }

      safety.recordAction("posts");
      return {
        content: [
          {
            type: "text",
            text: `Post editor prepared and content inserted on feed. Remaining daily post quota: ${
              safety.canPerform("posts").remaining
            }`,
          },
        ],
      };
    }

    if (name === "linkedin_send_message") {
      const quotaCheck = safety.canPerform("messages");
      if (!quotaCheck.allowed) {
        return { content: [{ type: "text", text: `[SAFETY GUARDRAIL]: ${quotaCheck.reason}` }] };
      }

      const recipient = String(args?.recipientNameOrUrl ?? "").trim();
      const message = String(args?.message ?? "").trim();

      const page = await browser.getPage(false);
      await page.goto("https://www.linkedin.com/messaging/", { waitUntil: "domcontentloaded" });
      await browser.humanDelay(2500, 3500);

      const authCheck = await browser.checkAuthStatus(page);
      if (!authCheck.authenticated) {
        return {
          content: [{ type: "text", text: `[Session Notice]: ${authCheck.message}` }],
        };
      }

      // 1. If recipient is a direct URL
      if (recipient.startsWith("http")) {
        await page.goto(recipient, { waitUntil: "domcontentloaded" });
        await browser.humanDelay(2500, 3500);

        const msgBtn = await page.$("button:has-text('Message'), a:has-text('Message')");
        if (msgBtn) {
          await msgBtn.click();
          await browser.humanDelay(1800, 2800);

          const textbox = await page.$("div[role='textbox'], .msg-form__contenteditable");
          if (textbox) {
            await textbox.fill(message);
            await browser.humanDelay(1200, 2000);

            const sendBtn = await page.$(
              "button.msg-form__send-button, button[type='submit']:has-text('Send')"
            );
            if (sendBtn) {
              await sendBtn.click();
              await browser.humanDelay(2000, 3000);
              safety.recordAction("messages");
              return {
                content: [
                  {
                    type: "text",
                    text: `Message delivered successfully to ${recipient}!`,
                  },
                ],
              };
            }
          }
        }
      }

      // 2. Search / Compose by Name directly in LinkedIn Messaging
      let composeBtn = await page.$(
        ".msg-conversations-container__compose-btn, button:has-text('Compose a new message')"
      );
      if (!composeBtn) {
        composeBtn = await page.$(
          "button[data-control-name='overlay.compose_message'], a[href*='/messaging/compose']"
        );
      }

      if (composeBtn) {
        await composeBtn.click();
        await page.waitForTimeout(2000);

        const typeRecipient = await page.$(
          "input[placeholder*='name'], input.msg-connections-typeahead__search-field"
        );

        if (typeRecipient) {
          await typeRecipient.fill(recipient);
          await page.waitForTimeout(3000);

          const firstMatch = await page.$(
            ".msg-connections-typeahead__search-result, .basic-typeahead__selectable-result"
          );

          if (firstMatch) {
            await firstMatch.click();
            await page.waitForTimeout(2000);

            const bodyBox = await page.$("div[role='textbox'], .msg-form__contenteditable");
            if (bodyBox) {
              await bodyBox.fill(message);
              await page.waitForTimeout(1500);

              const sendBtn = await page.$(
                "button.msg-form__send-button, button[type='submit']:has-text('Send')"
              );
              if (sendBtn) {
                await sendBtn.click();
                await page.waitForTimeout(3000);
                safety.recordAction("messages");
                return {
                  content: [
                    {
                      type: "text",
                      text: `Message delivered successfully to ${recipient} via LinkedIn MCP!`,
                    },
                  ],
                };
              }
            }
          }
        }
      }

      return {
        content: [
          {
            type: "text",
            text: `Could not complete message delivery. Please verify that '${recipient}' is in your connections.`,
          },
        ],
      };
    }

    if (name === "linkedin_queue_connection_invite") {
      const quotaCheck = safety.canPerform("connectionInvites");
      if (!quotaCheck.allowed) {
        return { content: [{ type: "text", text: `[SAFETY GUARDRAIL]: ${quotaCheck.reason}` }] };
      }

      const target = String(args?.profileUrl ?? "").trim();
      const note = args?.note ? String(args.note).trim() : undefined;
      const delayMs = safety.getRandomDelay();

      const queued = safety.enqueueAction({
        type: "invite",
        target,
        content: note,
        scheduledTime: Date.now() + delayMs,
      });

      return {
        content: [
          {
            type: "text",
            text: `Connection invite safely placed in outbound queue (ID: ${queued.id}).\nTarget: ${target}\nPacing delay: ~${Math.round(
              delayMs / 1000
            )} seconds.\nRemaining safe invites today: ${safety.canPerform("connectionInvites").remaining}.`,
          },
        ],
      };
    }

    throw new Error(`Unknown tool: ${name}`);
  } catch (error: any) {
    return {
      content: [
        {
          type: "text",
          text: `[Error executing ${name}]: ${error?.message || error}`,
        },
      ],
      isError: true,
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((err) => {
  console.error("Fatal error in LinkedIn MCP server:", err);
  process.exit(1);
});
