import asyncio
import os
import json
from playwright.async_api import async_playwright

async def inspect_all_steps():
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
        
        btn = await page.query_selector("button:has-text('Easy Apply')")
        if btn:
            await btn.click()
            await asyncio.sleep(2)
            
            pages_data = []
            
            for step in range(1, 6):
                print(f"--- Extracting Step {step} ---")
                data = await page.evaluate("""() => {
                    const header = document.querySelector('.jobs-easy-apply-modal h3, .jobs-easy-apply-modal h2')?.textContent?.trim() || 'Details';
                    const questions = Array.from(document.querySelectorAll('.jobs-easy-apply-modal .fb-dash-form-element, .jobs-easy-apply-modal .jobs-easy-apply-form-section__grouping')).map(el => {
                        const label = el.querySelector('label, span.t-14')?.textContent?.trim()?.replace(/\\s+/g, ' ') || '';
                        const input = el.querySelector('input, select, textarea');
                        const val = input ? input.value : '';
                        const type = input ? (input.tagName === 'SELECT' ? 'dropdown' : input.type) : 'section';
                        return { label, type, currentValue: val };
                    }).filter(q => q.label);
                    return { header, questions };
                }""")
                pages_data.append(data)
                
                # Screenshot each page
                await page.screenshot(path=f"B:\\AI_Projects\\linkedin-mcp-agent\\step_{step}.png")
                
                # Click Next (DO NOT click Review or Submit)
                next_btn = await page.query_selector("button:has-text('Next')")
                if next_btn:
                    await next_btn.click()
                    await asyncio.sleep(2)
                else:
                    break
                    
            print("ALL APPLICATION STEPS EXTRACTED:")
            print(json.dumps(pages_data, indent=2))
            
            # Dismiss safely
            dismiss = await page.query_selector('button[aria-label="Dismiss"]')
            if dismiss:
                await dismiss.click()
                await asyncio.sleep(1)
                discard = await page.query_selector('button[data-control-name="discard_application_confirm_btn"]')
                if discard:
                    await discard.click()
                    
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(inspect_all_steps())
