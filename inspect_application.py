import asyncio
import os
import json
from playwright.async_api import async_playwright

async def inspect_jobs():
    user_data = os.path.expandvars(r'%USERPROFILE%\.linkedin_mcp_browser_profile')
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        
        urls = [
            ("Digitals AI - Generative AI Engineer", "https://www.linkedin.com/jobs/view/4478384181/"),
            ("Arthatai - Full-Stack Developer", "https://www.linkedin.com/jobs/view/4477248426/"),
            ("Arclend - Full Stack Developer Intern", "https://www.linkedin.com/jobs/view/4467364744/")
        ]
        
        for name, url in urls:
            print(f"\n==========================================")
            print(f"CHECKING: {name}")
            print(f"==========================================")
            await page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(3)
            
            btn_info = await page.evaluate("""() => {
                const btn = document.querySelector('.jobs-apply-button--top-card button, .jobs-apply-button');
                if (!btn) return { hasBtn: false };
                return {
                    hasBtn: true,
                    text: btn.textContent.trim(),
                    isEasyApply: btn.textContent.includes('Easy Apply')
                };
            }""")
            print("Apply button status:", json.dumps(btn_info, indent=2))
            
            if btn_info.get("isEasyApply"):
                print("Opening Easy Apply form...")
                await page.click(".jobs-apply-button--top-card button, .jobs-apply-button")
                await asyncio.sleep(2)
                
                questions = await page.evaluate("""() => {
                    const elements = Array.from(document.querySelectorAll('.jobs-easy-apply-modal .fb-dash-form-element'));
                    return elements.map(el => {
                        const label = el.querySelector('label')?.textContent?.trim() || '';
                        const input = el.querySelector('input, select, textarea');
                        const val = input ? input.value : '';
                        const type = input ? (input.tagName === 'SELECT' ? 'dropdown' : input.type) : 'unknown';
                        return { label, type, currentValue: val };
                    }).filter(q => q.label);
                }""")
                print("Questions & Fields found:")
                print(json.dumps(questions, indent=2))
                
                # Take screenshot of the application modal
                screenshot_path = f"B:\\AI_Projects\\linkedin-mcp-agent\\apply_{name.split()[0].lower()}.png"
                await page.screenshot(path=screenshot_path)
                print(f"Saved application screenshot to: {screenshot_path}")
                
                # Dismiss without submitting
                dismiss_btn = await page.query_selector('.jobs-easy-apply-modal button[aria-label="Dismiss"]')
                if dismiss_btn:
                    await dismiss_btn.click()
                    await asyncio.sleep(1)
                    discard = await page.query_selector('button[data-control-name="discard_application_confirm_btn"]')
                    if discard:
                        await discard.click()
            else:
                print("This job redirects to company website or direct submission.")
                
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(inspect_jobs())
