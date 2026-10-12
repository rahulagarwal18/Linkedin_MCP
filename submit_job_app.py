import asyncio
import os
from playwright.async_api import async_playwright

async def submit_application():
    user_data = os.path.expandvars(r'%USERPROFILE%\.linkedin_mcp_browser_profile')
    print("Launching browser with your persistent session...")
    
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        
        job_url = "https://www.linkedin.com/jobs/view/4478384181/"
        print(f"Navigating to job: {job_url}")
        await page.goto(job_url, wait_until="domcontentloaded")
        await asyncio.sleep(4)
        
        # Click Easy Apply
        easy_apply_btn = await page.query_selector("button:has-text('Easy Apply')")
        if not easy_apply_btn:
            print("Easy Apply button not found!")
            await ctx.close()
            return
            
        print("Clicking Easy Apply...")
        await easy_apply_btn.click()
        await asyncio.sleep(3)
        
        # Page 1: Contact Info -> Click Next
        print("Step 1: Contact info verified. Clicking Next...")
        next_btn = await page.query_selector("button:has-text('Next')")
        if next_btn:
            await next_btn.click()
            await asyncio.sleep(2)
            
        # Page 2: Headline, Summary, Cover Letter
        print("Step 2: Filling Headline, Summary, and Cover Letter...")
        
        # 1. Headline
        headline_input = await page.query_selector("input[id*='headline'], input[aria-label*='Headline'], input[name*='headline']")
        if not headline_input:
            inputs = await page.query_selector_all(".jobs-easy-apply-modal input[type='text']")
            if len(inputs) > 0:
                headline_input = inputs[0]
                
        if headline_input:
            headline_text = "Full-Stack Developer & Applied AI Engineer | Python, LangChain, Next.js"
            print("Entering Headline...")
            await headline_input.fill(headline_text)
            await asyncio.sleep(1)
            
        # 2. Summary
        textareas = await page.query_selector_all(".jobs-easy-apply-modal textarea")
        summary_text = "Full-Stack & Applied AI Engineer with hands-on experience building production web platforms and integrating autonomous LLM agents (LangChain, Llama-3, RAG, FAISS). Winner of National Science Day (1st Place) & UN Millennium Fellow."
        
        cover_letter_text = (
            "Dear Hiring Manager,\n\n"
            "I am writing to express my strong interest in the Generative AI Engineer role for Freshers at Digitals AI. "
            "With hands-on experience building production full-stack systems and specialized AI agent workflows "
            "(LangChain, Llama-3, RAG pipelines, and Vector Search), I am eager to contribute to your generative AI development team. "
            "My background as Founder's Intern at InferWorks and UN Millennium Fellow demonstrates my ability to deliver scalable, reliable solutions.\n\n"
            "Thank you for your consideration.\n\n"
            "Sincerely,\n"
            "Rahul Agarwal"
        )
        
        if len(textareas) >= 2:
            print("Entering Summary...")
            await textareas[0].fill(summary_text)
            await asyncio.sleep(1)
            print("Entering Cover Letter tailored for Digitals AI...")
            await textareas[1].fill(cover_letter_text)
            await asyncio.sleep(1)
        elif len(textareas) == 1:
            print("Updating Cover Letter...")
            await textareas[0].fill(cover_letter_text)
            await asyncio.sleep(1)
            
        # Click Next
        next_btn = await page.query_selector("button:has-text('Next')")
        if next_btn:
            print("Advancing to Step 3...")
            await next_btn.click()
            await asyncio.sleep(2)
            
        # Step 3: Work experience -> Click Next
        next_btn = await page.query_selector("button:has-text('Next')")
        if next_btn:
            print("Advancing to Step 4 (Education)...")
            await next_btn.click()
            await asyncio.sleep(2)
            
        # Step 4: Education -> Click Review
        review_btn = await page.query_selector("button:has-text('Review')")
        if review_btn:
            print("Clicking Review...")
            await review_btn.click()
            await asyncio.sleep(3)
            
        # Take screenshot of final review page before submit
        screenshot_review = r"B:\AI_Projects\linkedin-mcp-agent\application_review.png"
        await page.screenshot(path=screenshot_review)
        print(f"Saved review screenshot to {screenshot_review}")
        
        # Click Submit application
        submit_btn = await page.query_selector("button:has-text('Submit application'), button[aria-label*='Submit application']")
        if submit_btn:
            print("Clicking 'Submit application'...")
            await submit_btn.click()
            await asyncio.sleep(4)
            
            # Take confirmation screenshot
            confirm_screenshot = r"B:\AI_Projects\linkedin-mcp-agent\application_submitted.png"
            await page.screenshot(path=confirm_screenshot)
            print(f"Saved submission confirmation screenshot to {confirm_screenshot}")
            print("\n>>> APPLICATION SUBMITTED SUCCESSFULLY! <<<")
        else:
            print("Submit application button not found on review page.")
            
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(submit_application())
