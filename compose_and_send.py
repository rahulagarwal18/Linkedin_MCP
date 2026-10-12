import asyncio
import os
from playwright.async_api import async_playwright

async def send_new_msg():
    user_data = os.path.expandvars(r'%USERPROFILE%\.linkedin_mcp_browser_profile')
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data,
            headless=True,
            viewport={"width": 1280, "height": 800},
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        
        print("Navigating to LinkedIn Messaging...")
        await page.goto("https://www.linkedin.com/messaging/", wait_until="domcontentloaded")
        await asyncio.sleep(3)
        
        # Click the Compose New Message button (the pencil icon button near top right of messages list)
        print("Looking for compose new message button...")
        compose_btn = await page.query_selector("button[data-control-name='overlay.compose_message'], a[href*='/messaging/compose'], svg[data-test-icon='compose-small'], button:has(svg[data-test-icon='compose-small'])")
        if not compose_btn:
            compose_btn = await page.query_selector(".msg-conversations-container__title-row button:last-child")
            
        if compose_btn:
            print("Clicking Compose button...")
            await compose_btn.click()
            await asyncio.sleep(2)
            
            # The 'Type a name or multiple names' input
            type_recipient = await page.query_selector("input[placeholder*='name'], input.msg-connections-typeahead__search-field")
            if type_recipient:
                print("Typing 'Aditya Agarwal' into recipient field...")
                await type_recipient.fill("Aditya Agarwal")
                await asyncio.sleep(3)
                
                # Check dropdown suggestions
                suggestions = await page.evaluate('''() => {
                    const list = Array.from(document.querySelectorAll('.msg-connections-typeahead__search-result, .basic-typeahead__selectable-result'));
                    return list.map(el => el.textContent.trim().replace(/\\s+/g, ' '));
                }''')
                print(f"Suggestions found ({len(suggestions)}):", suggestions)
                
                # Screenshot the compose suggestion state
                await page.screenshot(path=r"B:\AI_Projects\linkedin-mcp-agent\compose_dropdown.png")
                
                # Click the first suggestion
                first_sugg = await page.query_selector(".msg-connections-typeahead__search-result, .basic-typeahead__selectable-result")
                if first_sugg:
                    print("Selecting recipient from dropdown...")
                    await first_sugg.click()
                    await asyncio.sleep(2)
                    
                    # Fill message
                    body_box = await page.query_selector("div[role='textbox'], .msg-form__contenteditable")
                    if body_box:
                        print("Writing message...")
                        msg = "Hello Aditya, This is the message from MCP created by Rahul Agarwal"
                        await body_box.fill(msg)
                        await asyncio.sleep(2)
                        
                        send_btn = await page.query_selector("button.msg-form__send-button, button[type='submit']:has-text('Send')")
                        if send_btn:
                            print("Clicking Send...")
                            await send_btn.click()
                            await asyncio.sleep(3)
                            print(">>> SUCCESS: Message sent to Aditya Agarwal! <<<")
                        else:
                            print("Send button not found.")
                    else:
                        print("Message text area not found.")
                else:
                    print("No connection matched 'Aditya Agarwal' in typeahead.")
            else:
                print("Recipient input not found.")
        else:
            print("Compose button not found.")
            
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(send_new_msg())
