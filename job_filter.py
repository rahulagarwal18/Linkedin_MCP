import asyncio
import os
import json
from playwright.async_api import async_playwright

async def run_search():
    user_data = os.path.expandvars(r'%USERPROFILE%\.linkedin_mcp_browser_profile')
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(user_data, headless=True)
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        
        # f_TPR=r172800 -> Past 2 days (48 hours)
        # f_E=1,2 -> Internship & Entry level (Fresher)
        url = "https://www.linkedin.com/jobs/search/?keywords=AI%20Full%20Stack%20Engineer&location=India&f_TPR=r172800&f_E=1%2C2"
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(4)
        
        jobs = await page.evaluate("""() => {
            const cards = Array.from(document.querySelectorAll('.job-card-container, .jobs-search-results__list-item, li[data-occludable-job-id]')).slice(0, 10);
            return cards.map(el => {
                const title = el.querySelector('.job-card-list__title, .artdeco-entity-lockup__title')?.textContent?.trim() || '';
                const comp = el.querySelector('.job-card-container__primary-description, .artdeco-entity-lockup__subtitle')?.textContent?.trim() || '';
                const loc = el.querySelector('.job-card-container__metadata-item, .artdeco-entity-lockup__caption')?.textContent?.trim() || '';
                const link = el.querySelector('a[href*="/jobs/view/"]')?.href?.split('?')[0] || '';
                return { title, company: comp, location: loc, url: link };
            }).filter(j => j.title && j.url);
        }""")
        
        print("FILTERED_JOBS_RESULT:")
        print(json.dumps(jobs, indent=2))
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(run_search())
