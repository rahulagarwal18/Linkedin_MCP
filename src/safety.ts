import fs from "node:fs";
import path from "node:path";
import { CONFIG } from "./config.js";

export interface DailyUsage {
  date: string; // YYYY-MM-DD
  profileViews: number;
  connectionInvites: number;
  messages: number;
  posts: number;
}

export interface QueuedAction {
  id: string;
  type: "message" | "invite" | "post";
  target: string;
  content?: string;
  scheduledTime?: number;
  status: "pending" | "processing" | "completed" | "failed";
  error?: string;
  createdAt: number;
  processedAt?: number;
}

export class SafetyManager {
  private usageFile: string;
  private queueFile: string;

  constructor() {
    if (!fs.existsSync(CONFIG.dataDir)) {
      fs.mkdirSync(CONFIG.dataDir, { recursive: true });
    }
    this.usageFile = path.join(CONFIG.dataDir, "usage.json");
    this.queueFile = path.join(CONFIG.dataDir, "queue.json");
  }

  private getTodayStr(): string {
    const now = new Date();
    return now.toISOString().split("T")[0];
  }

  public getUsage(): DailyUsage {
    const today = this.getTodayStr();
    if (fs.existsSync(this.usageFile)) {
      try {
        const data = JSON.parse(fs.readFileSync(this.usageFile, "utf-8")) as DailyUsage;
        if (data.date === today) {
          return data;
        }
      } catch {
        // Fallback to fresh record
      }
    }
    const fresh: DailyUsage = {
      date: today,
      profileViews: 0,
      connectionInvites: 0,
      messages: 0,
      posts: 0,
    };
    this.saveUsage(fresh);
    return fresh;
  }

  public saveUsage(usage: DailyUsage): void {
    const tmp = `${this.usageFile}.tmp`;
    fs.writeFileSync(tmp, JSON.stringify(usage, null, 2), "utf-8");
    fs.renameSync(tmp, this.usageFile);
  }

  public canPerform(type: keyof typeof CONFIG.dailyLimits): { allowed: boolean; reason?: string; remaining: number } {
    const usage = this.getUsage();
    const current = usage[type] || 0;
    const limit = CONFIG.dailyLimits[type];
    const remaining = Math.max(0, limit - current);

    if (current >= limit) {
      return {
        allowed: false,
        reason: `Daily quota limit reached for ${type} (${current}/${limit} used today). Action paused for account safety.`,
        remaining: 0,
      };
    }
    return { allowed: true, remaining };
  }

  public recordAction(type: keyof typeof CONFIG.dailyLimits): void {
    const usage = this.getUsage();
    usage[type] = (usage[type] || 0) + 1;
    this.saveUsage(usage);
  }

  public getQueue(): QueuedAction[] {
    if (fs.existsSync(this.queueFile)) {
      try {
        return JSON.parse(fs.readFileSync(this.queueFile, "utf-8")) as QueuedAction[];
      } catch {
        return [];
      }
    }
    return [];
  }

  public saveQueue(queue: QueuedAction[]): void {
    const tmp = `${this.queueFile}.tmp`;
    fs.writeFileSync(tmp, JSON.stringify(queue, null, 2), "utf-8");
    fs.renameSync(tmp, this.queueFile);
  }

  public enqueueAction(action: Omit<QueuedAction, "id" | "status" | "createdAt">): QueuedAction {
    const queue = this.getQueue();
    const newAction: QueuedAction = {
      ...action,
      id: Math.random().toString(36).substring(2, 10),
      status: "pending",
      createdAt: Date.now(),
    };
    queue.push(newAction);
    this.saveQueue(queue);
    return newAction;
  }

  public updateActionStatus(id: string, status: QueuedAction["status"], error?: string): void {
    const queue = this.getQueue();
    const item = queue.find((q) => q.id === id);
    if (item) {
      item.status = status;
      if (error) item.error = error;
      if (status === "completed" || status === "failed") {
        item.processedAt = Date.now();
      }
      this.saveQueue(queue);
    }
  }

  public getRandomDelay(): number {
    const { minActionDelayMs, maxActionDelayMs } = CONFIG.delays;
    return Math.floor(Math.random() * (maxActionDelayMs - minActionDelayMs + 1)) + minActionDelayMs;
  }
}
