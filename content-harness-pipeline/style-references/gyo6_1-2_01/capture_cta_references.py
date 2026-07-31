from pathlib import Path

from playwright.sync_api import sync_playwright


VIEWPORT = {"width": 1600, "height": 900}
SCENES = {
    "intro": "cta-intro.png",
    "activity": "cta-activity.png",
    "final": "cta-primary-secondary.png",
}


def main() -> None:
    root = Path(__file__).resolve().parent
    reference_url = (root / "cta-reference.html").as_uri()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport=VIEWPORT, device_scale_factor=1)
        for scene, filename in SCENES.items():
            page.goto(f"{reference_url}?scene={scene}", wait_until="networkidle")
            page.screenshot(path=str(root / "ctas" / filename), full_page=False)
        browser.close()


if __name__ == "__main__":
    main()
