# ComputerBox Desktop Automation Guide

Complete guide for using BoxLite's ComputerBox for desktop GUI automation.

## Overview

ComputerBox provides a full Linux desktop environment running in a hardware-isolated VM. It enables:
- Mouse and keyboard automation
- Screenshot capture for visual AI analysis
- Browser automation without Selenium/Playwright
- Desktop application testing
- Visual validation and UI testing

## Use Cases

### AI Agent Browser Automation

Unlike Playwright/Selenium that automate browsers through APIs, ComputerBox runs a real desktop with real browsers - useful for:
- Sites with anti-bot protection
- Complex JavaScript-heavy applications
- Visual AI that needs screenshots
- Testing actual user experience

### Desktop Application Testing

```python
import asyncio
import boxlite

async def test_desktop_app():
    async with boxlite.ComputerBox(
        image="ubuntu-desktop:22.04",
        cpu=4,
        memory=8192
    ) as desktop:
        await desktop.wait_until_ready()

        # Launch application
        await desktop.exec("libreoffice", "--calc")
        await asyncio.sleep(3)

        # Interact with application
        await desktop.type("Hello World")
        await desktop.hotkey("ctrl", "s")

        # Take screenshot for verification
        screenshot = await desktop.screenshot()
        return screenshot
```

### Visual AI Integration

```python
import asyncio
import boxlite
import base64

async def get_screen_for_vision_model():
    async with boxlite.ComputerBox() as desktop:
        await desktop.wait_until_ready()

        # Navigate to webpage
        await desktop.exec("firefox", "https://example.com")
        await asyncio.sleep(5)

        # Capture for vision model
        screenshot = await desktop.screenshot()
        b64_image = base64.b64encode(screenshot).decode()

        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": b64_image
            }
        }

# Use with Claude Vision, GPT-4V, etc.
```

## Mouse Operations

### Basic Mouse Control

```python
import asyncio
import boxlite

async def mouse_demo():
    async with boxlite.ComputerBox() as desktop:
        await desktop.wait_until_ready()

        # Move to absolute position
        await desktop.mouse_move(500, 300)

        # Click operations
        await desktop.left_click()
        await desktop.right_click()
        await desktop.double_click()

        # Click at specific position (move + click)
        await desktop.mouse_move(100, 100)
        await desktop.left_click()
```

### Drag and Drop

```python
async def drag_and_drop(desktop, start_x, start_y, end_x, end_y):
    """Perform drag and drop operation."""
    await desktop.mouse_move(start_x, start_y)
    await desktop.mouse_down()  # Press and hold
    await asyncio.sleep(0.1)

    await desktop.mouse_move(end_x, end_y)
    await asyncio.sleep(0.1)

    await desktop.mouse_up()  # Release
```

### Scroll

```python
async def scroll_demo(desktop):
    # Scroll down
    await desktop.scroll(0, -100)  # Negative Y = scroll down

    # Scroll up
    await desktop.scroll(0, 100)   # Positive Y = scroll up

    # Horizontal scroll
    await desktop.scroll(100, 0)   # Positive X = scroll right
```

## Keyboard Operations

### Typing Text

```python
async def typing_demo(desktop):
    # Simple text
    await desktop.type("Hello, BoxLite!")

    # With delay between keystrokes (for slow applications)
    await desktop.type("Slow typing...", delay_ms=100)

    # Special characters
    await desktop.type("email@example.com")
    await desktop.type("Price: $99.99")
```

### Special Keys

```python
async def special_keys_demo(desktop):
    # Common keys
    await desktop.key("Enter")
    await desktop.key("Tab")
    await desktop.key("Escape")
    await desktop.key("Backspace")
    await desktop.key("Delete")

    # Arrow keys
    await desktop.key("Up")
    await desktop.key("Down")
    await desktop.key("Left")
    await desktop.key("Right")

    # Function keys
    await desktop.key("F1")
    await desktop.key("F5")
    await desktop.key("F11")

    # Modifier keys alone
    await desktop.key("Shift")
    await desktop.key("Control")
    await desktop.key("Alt")
```

### Hotkeys (Key Combinations)

```python
async def hotkey_demo(desktop):
    # Copy/Paste
    await desktop.hotkey("ctrl", "c")
    await desktop.hotkey("ctrl", "v")

    # Save
    await desktop.hotkey("ctrl", "s")

    # Select all
    await desktop.hotkey("ctrl", "a")

    # Find
    await desktop.hotkey("ctrl", "f")

    # Undo/Redo
    await desktop.hotkey("ctrl", "z")
    await desktop.hotkey("ctrl", "shift", "z")

    # Close window
    await desktop.hotkey("alt", "F4")

    # Switch window
    await desktop.hotkey("alt", "Tab")

    # Open terminal (Ubuntu)
    await desktop.hotkey("ctrl", "alt", "t")
```

## Screenshot Operations

### Basic Screenshot

```python
async def screenshot_demo(desktop):
    # Full screen capture
    screenshot = await desktop.screenshot()

    # Save to file
    with open("screenshot.png", "wb") as f:
        f.write(screenshot)

    return screenshot
```

### Screenshot for AI Analysis

```python
import base64

async def screenshot_for_ai(desktop):
    screenshot = await desktop.screenshot()

    # For OpenAI Vision API
    b64 = base64.b64encode(screenshot).decode()

    return {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/png;base64,{b64}"
        }
    }
```

### Periodic Screenshot Capture

```python
async def monitor_screen(desktop, interval_sec: float = 1.0, count: int = 10):
    screenshots = []

    for i in range(count):
        screenshot = await desktop.screenshot()
        screenshots.append({
            "index": i,
            "timestamp": asyncio.get_event_loop().time(),
            "data": screenshot
        })
        await asyncio.sleep(interval_sec)

    return screenshots
```

## Browser Automation Patterns

### Simple Web Navigation

```python
import asyncio
import boxlite

async def browse_web():
    async with boxlite.ComputerBox(
        cpu=2,
        memory=4096
    ) as desktop:
        await desktop.wait_until_ready()

        # Open Firefox
        await desktop.exec("firefox", "https://google.com")
        await asyncio.sleep(5)

        # Type in search box (Google's search box is usually focused)
        await desktop.type("BoxLite AI sandbox")
        await desktop.key("Enter")
        await asyncio.sleep(3)

        # Take screenshot of results
        return await desktop.screenshot()
```

### Form Filling

```python
async def fill_form(desktop, form_data: dict):
    """Fill web form with data."""
    for field_name, value in form_data.items():
        # Click on field (assuming known coordinates or using Tab)
        await desktop.key("Tab")
        await asyncio.sleep(0.2)

        # Clear existing content
        await desktop.hotkey("ctrl", "a")

        # Type new value
        await desktop.type(value)
        await asyncio.sleep(0.1)

    # Submit
    await desktop.key("Enter")
```

### Login Automation

```python
async def login_to_site(desktop, url: str, username: str, password: str):
    """Automate login process."""
    # Navigate to login page
    await desktop.exec("firefox", url)
    await asyncio.sleep(5)

    # Fill username
    await desktop.type(username)
    await desktop.key("Tab")

    # Fill password
    await desktop.type(password)
    await desktop.key("Enter")

    await asyncio.sleep(3)
    return await desktop.screenshot()
```

## AI Agent Integration Patterns

### Visual Feedback Loop

```python
import asyncio
import boxlite

class VisualAgent:
    """Agent that uses screenshots for decision making."""

    def __init__(self, vision_model):
        self.vision_model = vision_model
        self.desktop = None

    async def setup(self):
        self.desktop = await boxlite.ComputerBox(
            cpu=2,
            memory=4096
        ).__aenter__()
        await self.desktop.wait_until_ready()

    async def observe(self) -> bytes:
        """Capture current screen state."""
        return await self.desktop.screenshot()

    async def act(self, action: dict):
        """Execute action based on AI decision."""
        action_type = action.get("type")

        if action_type == "click":
            await self.desktop.mouse_move(action["x"], action["y"])
            await self.desktop.left_click()

        elif action_type == "type":
            await self.desktop.type(action["text"])

        elif action_type == "key":
            await self.desktop.key(action["key"])

        elif action_type == "hotkey":
            await self.desktop.hotkey(*action["keys"])

    async def step(self, goal: str) -> dict:
        """Single agent step: observe -> think -> act."""
        # Observe
        screenshot = await self.observe()

        # Think (call vision model)
        action = await self.vision_model.decide(screenshot, goal)

        # Act
        await self.act(action)

        # Return new state
        new_screenshot = await self.observe()
        return {
            "action_taken": action,
            "new_state": new_screenshot
        }

    async def cleanup(self):
        if self.desktop:
            await self.desktop.__aexit__(None, None, None)
```

### Multi-Step Task Execution

```python
async def execute_task(desktop, steps: list[dict]):
    """Execute sequence of UI actions."""
    results = []

    for i, step in enumerate(steps):
        try:
            await asyncio.sleep(step.get("delay", 0.5))

            if step["action"] == "click":
                await desktop.mouse_move(step["x"], step["y"])
                await desktop.left_click()

            elif step["action"] == "type":
                await desktop.type(step["text"])

            elif step["action"] == "key":
                await desktop.key(step["key"])

            elif step["action"] == "screenshot":
                screenshot = await desktop.screenshot()
                results.append({
                    "step": i,
                    "screenshot": screenshot
                })

            elif step["action"] == "wait":
                await asyncio.sleep(step.get("seconds", 1))

        except Exception as e:
            results.append({
                "step": i,
                "error": str(e)
            })

    return results
```

## Configuration

### Display Settings

```python
async with boxlite.ComputerBox(
    display_width=1920,   # Screen width
    display_height=1080,  # Screen height
    # Default: 1280x720
) as desktop:
    pass
```

### Resource Allocation

```python
# Minimum for basic desktop
async with boxlite.ComputerBox(
    cpu=2,
    memory=2048
) as desktop:
    pass

# For browser automation
async with boxlite.ComputerBox(
    cpu=4,
    memory=4096
) as desktop:
    pass

# For heavy applications
async with boxlite.ComputerBox(
    cpu=8,
    memory=8192,
    disk_size=40960
) as desktop:
    pass
```

### Custom Desktop Image

```python
# Ubuntu with specific packages
async with boxlite.ComputerBox(
    image="ubuntu-desktop:22.04"
) as desktop:
    pass

# Custom image with pre-installed tools
async with boxlite.ComputerBox(
    image="my-registry/custom-desktop:latest"
) as desktop:
    pass
```

## Troubleshooting

### Desktop Not Ready

```python
async def safe_wait(desktop, timeout: float = 120.0):
    """Wait for desktop with extended timeout."""
    try:
        await asyncio.wait_for(
            desktop.wait_until_ready(),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        # Take diagnostic screenshot anyway
        try:
            screenshot = await desktop.screenshot()
            with open("debug.png", "wb") as f:
                f.write(screenshot)
        except:
            pass
        raise RuntimeError("Desktop failed to start within timeout")
```

### Click Not Working

```python
async def robust_click(desktop, x: int, y: int, retries: int = 3):
    """Click with retry logic."""
    for i in range(retries):
        await desktop.mouse_move(x, y)
        await asyncio.sleep(0.1)  # Wait for cursor to settle
        await desktop.left_click()
        await asyncio.sleep(0.3)  # Wait for click to register

        # Could add screenshot verification here
```

### Slow Application Response

```python
async def wait_for_change(desktop, max_wait: float = 10.0):
    """Wait for screen content to change."""
    initial = await desktop.screenshot()

    start = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start < max_wait:
        await asyncio.sleep(0.5)
        current = await desktop.screenshot()

        if current != initial:
            return True

    return False
```
