import { expect, test } from "@playwright/test";
import { createTestSpecialist, loginWith, logout } from "./helpers";
test.describe.serial("specialist schedule management", () => {
    test("specialist can create and delete a recurring break", async ({ page, request }) => {
        const breakLabel = `Playwright Break ${Date.now()}`;
        const specialist = await createTestSpecialist(request, "specialist-schedule");
        const existingBreaksResponse = await request.get("http://localhost:8000/api/v1/specialists/me/breaks", {
            headers: {
                Authorization: `Bearer ${specialist.token}`,
            },
        });
        expect(existingBreaksResponse.ok()).toBeTruthy();
        const existingBreaks = (await existingBreaksResponse.json());
        for (const item of existingBreaks.filter((breakItem) => (breakItem.label ?? "").startsWith("Playwright Break"))) {
            const deleteResponse = await request.delete(`http://localhost:8000/api/v1/specialists/me/breaks/${item.id}`, {
                headers: {
                    Authorization: `Bearer ${specialist.token}`,
                },
            });
            expect(deleteResponse.ok()).toBeTruthy();
        }
        await loginWith(page, specialist);
        await page.getByRole("link", { name: /^schedule$/i }).click();
        await expect(page).toHaveURL(/\/specialist\/schedule$/);
        await expect(page.getByRole("heading", { level: 1, name: /specialist schedule/i })).toBeVisible();
        await page.getByLabel(/break weekday/i).selectOption("2");
        await page.getByLabel(/break start/i).fill("12:00");
        await page.getByLabel(/break end/i).fill("12:30");
        await page.getByLabel(/^Label$/i).fill(breakLabel);
        await page.getByRole("button", { name: /create break/i }).click();
        const breakRow = page.getByText(new RegExp(`Wed.*${breakLabel}`));
        await expect(breakRow).toBeVisible();
        const breakCard = breakRow.locator("xpath=ancestor::div[.//button[normalize-space()='Delete']][1]");
        await expect(breakCard).toContainText(/12:00 - 12:30/);
        await breakCard.getByRole("button", { name: /delete/i }).click();
        await expect(page.getByText(new RegExp(`Wed.*${breakLabel}`))).toHaveCount(0);
        await logout(page);
    });
});
