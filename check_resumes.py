import asyncio
import os
import json
from playwright.async_api import async_playwright

async def check_uploaded_resumes():
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
            
            # Click Next to reach page 2 (resume selection)
            next_btn = await page.query_selector("button:has-text('Next')")
            if next_btn:
                await next_btn.click()
                await asyncio.sleep(2)
                
            # Inspect all available resumes on the page
            resumes = await page.evaluate("""() => {
                const items = Array.from(document.querySelectorAll('.jobs-resume-picker__resume-item, li[data-test-resume-picker-item], .ui-attachment')).map(el => {
                    const title = el.querySelector('p, h4, .t-bold, span')?.textContent?.trim() || '';
                    const date = el.querySelector('.t-12, .t-black--light')?.textContent?.trim() || '';
                    const radio = el.querySelector('input[type="radio"]');
                    return {
                        title,
                        date,
                        selected: radio ? radio.checked : false,
                        radioId: radio ? radio.id : ''
                    };
                });
                return items;
            }""")
            print("CURRENT AVAILABLE RESUMES ON LINKEDIN:")
            print(json.dumps(resumes, indent=2))
            
            await page.screenshot(path=r"B:\AI_Projects\linkedin-mcp-agent\updated_resumes.png")
            print("Saved screenshot to updated_resumes.png")
            
            dismiss = await page.query_selector('button[aria-label="Dismiss"]')
            if dismiss:
                await dismiss.click()
                await asyncio.sleep(1)
                discard = await page.query_selector('button[data-control-name="discard_application_confirm_btn"]')
                if discard:
                    await discard.click()
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(check_uploaded_resumes())
