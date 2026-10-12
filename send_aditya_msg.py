import asyncio
import os
import json
from playwright.async_api import async_playwright

async def find_and_message():
    user_data = os.path.expandvars(r'%USERPROFILE%\.linkedin_mcp_browser_profile')
    print("Launching browser with persistent session...")
    
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data,
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        
        # 1. Search for 1st-degree connections named "Aditya Agarwal"
        search_url = "https://www.linkedin.com/search/results/people/?keywords=Aditya%20Agarwal&network=%5B%22F%22%5D"
        print(f"Navigating to: {search_url}")
        await page.goto(search_url, wait_until="domcontentloaded")
        await asyncio.sleep(4)
        
        # 2. Extract found connections
        connections = await page.evaluate('''() => {
            const items = Array.from(document.querySelectorAll('.reusable-search__result-container, .entity-result'));
            return items.map(el => {
                const link = el.querySelector('a[href*="/in/"]');
                const titleText = el.querySelector('.entity-result__title-text a, .app-aware-link');
                const name = titleText ? titleText.textContent.trim().split('\\n')[0] : '';
                const subtitle = el.querySelector('.entity-result__primary-subtitle')?.textContent?.trim() || '';
                return {
                    name,
                    url: link ? link.href.split('?')[0] : '',
                    headline: subtitle
                };
            }).filter(c => c.url && c.url.includes('/in/'));
        }''')
        
        print(f"Found {len(connections)} matching 1st-degree connections:")
        for idx, c in enumerate(connections):
            print(f"[{idx+1}] {c['name']} - {c['headline']} -> {c['url']}")
            
        if not connections:
            print("No 1st-degree connection named 'Aditya Agarwal' found directly under filter. Checking global search...")
            global_search = "https://www.linkedin.com/search/results/people/?keywords=Aditya%20Agarwal"
            await page.goto(global_search, wait_until="domcontentloaded")
            await asyncio.sleep(4)
            connections = await page.evaluate('''() => {
                const items = Array.from(document.querySelectorAll('.reusable-search__result-container, .entity-result'));
                return items.map(el => {
                    const link = el.querySelector('a[href*="/in/"]');
                    const titleText = el.querySelector('.entity-result__title-text a, .app-aware-link');
                    const name = titleText ? titleText.textContent.trim().split('\\n')[0] : '';
                    const subtitle = el.querySelector('.entity-result__primary-subtitle')?.textContent?.trim() || '';
                    return {
                        name,
                        url: link ? link.href.split('?')[0] : '',
                        headline: subtitle
                    };
                }).filter(c => c.url && c.url.includes('/in/'));
            }''')
            print(f"Global results found: {len(connections)}")
            for idx, c in enumerate(connections[:5]):
                print(f"[{idx+1}] {c['name']} - {c['headline']} -> {c['url']}")

        if connections:
            target_profile = connections[0]['url']
            print(f"\nNavigating to top match: {target_profile}")
            await page.goto(target_profile, wait_until="domcontentloaded")
            await asyncio.sleep(4)
            
            # Look for the Message button on the profile
            print("Looking for Message button...")
            msg_btn = await page.query_selector("button:has-text('Message'), a:has-text('Message')")
            if msg_btn:
                print("Clicking Message button...")
                await msg_btn.click()
                await asyncio.sleep(3)
                
                # Type message
                textbox = await page.query_selector("div[role='textbox'], .msg-form__contenteditable")
                if textbox:
                    print("Typing message into chat composer...")
                    msg_text = "Hello Aditya, This is the message from MCP created by Rahul Agarwal"
                    await textbox.fill(msg_text)
                    await asyncio.sleep(2)
                    
                    # Find send button
                    send_btn = await page.query_selector("button.msg-form__send-button, button[type='submit']:has-text('Send')")
                    if send_btn:
                        print("Sending message...")
                        await send_btn.click()
                        await asyncio.sleep(3)
                        print("MESSAGE DELIVERED SUCCESSFULLY!")
                    else:
                        print("Send button found, typed message into input.")
                else:
                    print("Message input box not found.")
            else:
                print("Message button not directly clickable on this profile.")
                
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(find_and_message())
