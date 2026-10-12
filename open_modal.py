import asyncio
import os
import json
from playwright.async_api import async_playwright

async def inspect_modal():
    user_data = os.path.expandvars(r'%USERPROFILE%\.linkedin_mcp_browser_profile')
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        
        await page.goto("https://www.linkedin.com/jobs/view/4478384181/", wait_until="domcontentloaded")
        await asyncio.sleep(4)
        
        # Click Easy Apply
        btn = await page.query_selector("button.jobs-apply-button")
        if not btn:
            btn = await page.query_selector("button:has-text('Easy Apply')")
            
        if btn:
            print("Clicking Easy Apply...")
            await btn.click()
            await asyncio.sleep(3)
            
            modal_data = await page.evaluate("""() => {
                const modal = document.querySelector('.jobs-easy-apply-modal, div[role="dialog"]');
                if (!modal) return { found: false };
                
                const title = modal.querySelector('h2, h3')?.textContent?.trim() || 'No Title';
                const labels = Array.from(modal.querySelectorAll('label')).map(l => l.textContent.trim().replace(/\\s+/g, ' '));
                const inputs = Array.from(modal.querySelectorAll('input, select, textarea')).map(i => ({
                    tag: i.tagName,
                    type: i.type,
                    id: i.id,
                    value: i.value,
                    name: i.name,
                    placeholder: i.placeholder
                }));
                return { found: true, title, labels, inputs };
            }""")
            print("MODAL DETAILS:")
            print(json.dumps(modal_data, indent=2))
            
            await page.screenshot(path=r"B:\AI_Projects\linkedin-mcp-agent\digitals_ai_modal.png")
            print("Saved screenshot to digitals_ai_modal.png")
            
            dismiss = await page.query_selector('button[aria-label="Dismiss"]')
            if dismiss:
                await dismiss.click()
                await asyncio.sleep(1)
                discard = await page.query_selector('button[data-control-name="discard_application_confirm_btn"]')
                if discard:
                    await discard.click()
        else:
            print("Easy Apply button not found")
            
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(inspect_modal())
