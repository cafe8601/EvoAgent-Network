from playwright.sync_api import sync_playwright

def check_styles():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        
        print("Navigating...")
        try:
            page.goto("http://localhost:8000")
            page.wait_for_timeout(1000)
        except Exception as e:
            print(f"Error: {e}")
            return

        def get_computed(selector):
            return page.eval_on_selector(selector, """e => {
                const s = window.getComputedStyle(e);
                const r = e.getBoundingClientRect();
                return {
                    position: s.position,
                    display: s.display,
                    width: s.width,
                    height: s.height,
                    top: s.top,
                    left: s.left,
                    bottom: s.bottom,
                    right: s.right,
                    zIndex: s.zIndex,
                    marginTop: s.marginTop,
                    flexDirection: s.flexDirection,
                    rect: {x: r.x, y: r.y, w: r.width, h: r.height}
                };
            }""")

        print("\n--- Diagnostic Report ---")
        
        try:
            ws_style = get_computed('#welcome-screen')
            print(f"\n[#welcome-screen]")
            print(ws_style)
        except:
            print("Could not find #welcome-screen")
            
        try:
            main_style = get_computed('.main')
            print(f"\n[.main]")
            print(main_style)
        except:
            print("Could not find .main")
            
        try:
            body_style = get_computed('body')
            print(f"\n[body]")
            print(body_style)
        except:
            print("Could not find body")

        browser.close()

if __name__ == "__main__":
    check_styles()
