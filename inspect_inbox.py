import asyncio
import os
from playwright.async_api import async_playwright

async def inspect():
    user_data = os.path.expandvars(r'%USERPROFILE%\.linkedin_mcp_browser_profile')
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        
        # Navigate to LinkedIn messaging
        print("Navigating to LinkedIn Messaging inbox...")
        await page.goto("https://www.linkedin.com/messaging/", wait_until="domcontentloaded")
        await asyncio.sleep(4)
        
        print("Page URL:", page.url)
        title = await page.title()
        print("Page Title:", title)
        
        screenshot_path = r"B:\AI_Projects\linkedin-mcp-agent\messaging_view.png"
        await page.screenshot(path=screenshot_path)
        print("Screenshot saved to:", screenshot_path)
        
        # Search the messaging search box for Aditya Agarwal
        search_input = await page.query_selector("input.msg-search-form__search-input, input[placeholder*='Search messages']")
        if search_input:
            print("Typing 'Aditya Agarwal' into messaging search box...")
            await search_input.fill("Aditya Agarwal")
            await asyncio.sleep(3)
            
            # Capture results
            matches = await page.evaluate('''() => {
                const els = Array.from(document.querySelectorAll('.msg-conversation-listitem__participant-names, .msg-search-results__match, .msg-conversation-card__participant-names'));
                return els.map(e => e.textContent.trim());
            }''')
            print("Matches found in messaging:", matches)
            
            # Click first match if any
            first_item = await page.query_selector(".msg-conversation-listitem, .msg-conversation-card")
            if first_item:
                print("Selecting conversation thread...")
                await first_item.click()
                await asyncio.sleep(2)
                
                # Check message compose input
                msg_box = await page.query_selector("div[role='textbox'], .msg-form__contenteditable")
                if msg_box:
                    print("Composing message to Aditya Agarwal...")
                    await msg_box.fill("Hello Aditya, This is the message from MCP created by Rahul Agarwal")
                    await asyncio.sleep(2)
                    
                    send_btn = await page.query_selector("button.msg-form__send-button, button[type='submit']")
                    if send_btn:
                        print("Clicking Send button...")
                        await send_btn.click()
                        await asyncio.sleep(3)
                        print(">>> SUCCESS: Message sent successfully to Aditya Agarwal! <<<")
                    else:
                        print("Send button not found.")
                else:
                    print("Message composer box not found.")
        else:
            print("Inbox search input not found.")
            
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(inspect())
