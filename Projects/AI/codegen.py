import asyncio

from playwright.async_api import Playwright, async_playwright, expect


async def run(playwright: Playwright) -> None:
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("http://www.csm-testcenter.org/test?do=show&subdo=common&test=file_upload")

    fileChooserPromise = page.wait_for_event('filechooser')
    await page.locator("tbody").filter(has_text="File to upload Enable re-download (requires cookies) Start HTTP upload").get_by_role("textbox").click()
    fileChooser = await fileChooserPromise;

    # await page.locator("tbody").filter(has_text="File to upload Enable re-download (requires cookies) Start HTTP upload").get_by_role("textbox").set_input_files("custom.js")

    # ---------------------
    # await context.close()
    # await browser.close()
    input('exit?')


async def main() -> None:
    async with async_playwright() as playwright:
        await run(playwright)


asyncio.run(main())
