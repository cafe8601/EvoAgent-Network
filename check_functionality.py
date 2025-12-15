from playwright.sync_api import sync_playwright
import time

def check_functionality():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        
        print("1. Navigating to HAES (http://localhost:8000)...")
        try:
            page.goto("http://localhost:8000", timeout=5000)
        except Exception as e:
            print(f"❌ Failed to load page: {e}")
            return

        # Check Initial State
        print("2. Checking Initial Layout...")
        
        sidebar = page.locator(".sidebar")
        welcome = page.locator("#welcome-screen")
        input_area = page.locator(".input-area")
        
        if sidebar.is_visible() and welcome.is_visible() and input_area.is_visible():
            print("✅ Initial Layout: Visible (Sidebar, Welcome Screen, Input Area)")
        else:
            print(f"❌ Initial Layout Issues: Sidebar={sidebar.is_visible()}, Welcome={welcome.is_visible()}, Input={input_area.is_visible()}")
        
        # Test Interaction: Starter Card
        print("3. Testing Starter Card Interaction...")
        starter_card = page.locator(".starter-card").nth(1) # Second card (Realtime Search)
        card_text_element = starter_card.locator("h3") # Title
        card_text = card_text_element.inner_text()
        print(f"   Clicking card: {card_text}")
        
        starter_card.click()
        
        # Verify UI State Change
        print("4. Verifying UI State Transition...")
        # Welcome screen should define 'display: none'
        # Messages should be visible
        
        # Wait a bit for JS to execute
        page.wait_for_timeout(500)
        
        welcome_display = welcome.evaluate("el => getComputedStyle(el).display")
        messages = page.locator("#messages")
        messages_visible = messages.is_visible()
        
        if welcome_display == 'none':
            print("✅ Welcome Screen Hidden")
        else:
            print(f"❌ Welcome Screen Still Visible (display: {welcome_display})")
            
        if messages_visible:
            print("✅ Messages Area Visible")
        else:
            print("❌ Messages Area Not Visible")
            
        # Verify User Message
        user_msg = messages.locator(".message-text").first
        if user_msg.is_visible():
            print(f"✅ User Message Posted: '{user_msg.inner_text()}'")
        else:
            print("❌ User Message Not Found")

        # Verify Assistant Response (Wait a bit)
        print("5. Waiting for Assistant Response (up to 10s)...")
        try:
            # Look for assistant message
            assistant_msg = messages.locator(".message-avatar.assistant").first
            assistant_msg.wait_for(state="visible", timeout=10000)
            print("✅ Assistant Response Received!")
            
            # Print content preview
            content = messages.locator(".message-content").last.inner_text()
            print(f"   Response Preview: {content[:50]}...")
            
        except Exception as e:
            print("⚠️ Assistant Response Timeout or Error (Backend might be slow or offline)")
            print(f"   Details: {e}")

        # Screenshot for debug (saving to file just in case)
        page.screenshot(path="final_check_result.png")
        print("6. Test Complete.")
        
        browser.close()

if __name__ == "__main__":
    check_functionality()
