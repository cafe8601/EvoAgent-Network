from playwright.sync_api import sync_playwright

def check_position():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a standard desktop viewport
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        
        print("Navigating to http://localhost:8000...")
        try:
            page.goto("http://localhost:8000", timeout=5000)
        except Exception as e:
            print(f"Error accessing page: {e}")
            return

        # Wait for any animations to settle
        page.wait_for_timeout(1500)
        
        # Check elements
        welcome_screen = page.locator("#welcome-screen")
        title = page.locator(".welcome-title")
        
        if not title.is_visible():
            print("ERROR: Welcome Title not visible!")
            browser.close()
            return

        screen_box = welcome_screen.bounding_box()
        title_box = title.bounding_box()
        viewport = page.viewport_size
        
        print("\n--- UI Layout Analysis ---")
        print(f"Viewport Size: {viewport['width']}x{viewport['height']}")
        
        print(f"\n[Welcome Screen Container]")
        print(f"Box: {screen_box}")
        
        print(f"\n[Title: '무엇을 도와드릴까요?']")
        print(f"Box: {title_box}")
        
        if title_box:
            # Calculate Centers
            title_center_x = title_box['x'] + title_box['width'] / 2
            title_center_y = title_box['y'] + title_box['height'] / 2
            
            screen_center_x = viewport['width'] / 2
            screen_center_y = viewport['height'] / 2
            
            # Sidebar consideration
            # The viewport center ignore sidebar, but our visual center should be (viewport_width - sidebar) / 2 + sidebar
            # Assuming sidebar is 280px
            effective_center_x = 280 + (1280 - 280) / 2
            
            print(f"\nTitle Center Point: ({title_center_x:.1f}, {title_center_y:.1f})")
            print(f"Screen Absolute Center: ({screen_center_x:.1f}, {screen_center_y:.1f})")
            print(f"Effective Visual Center (w/ Sidebar): ({effective_center_x:.1f}, {screen_center_y:.1f})")
            
            # Analysis
            x_diff = title_center_x - screen_center_x
            y_diff = title_center_y - screen_center_y
            
            print(f"\nOffset from Screen Center: X={x_diff:.1f}, Y={y_diff:.1f}")
            
            print("\n[VERDICT]")
            if title_center_y < screen_center_y:
                print("✅ Vertical: Title is positioned ABOVE the center line (Correct).")
            else:
                print("❌ Vertical: Title is positioned BELOW or AT the center line (Incorrect).")
            
            if abs(title_center_x - effective_center_x) < 20: 
                 print("✅ Horizontal: Title is centered in the main content area (Correct, considering sidebar).")
            elif abs(title_center_x - screen_center_x) < 20:
                 print("⚠️ Horizontal: Title is centered to the WINDOW, ignoring sidebar (Acceptable but maybe ignored sidebar).")
            else:
                 print(f"❌ Horizontal: Title is NOT centered. It seems shifted by {title_center_x - effective_center_x:.1f}px from effective center.")

        browser.close()

if __name__ == "__main__":
    check_position()
