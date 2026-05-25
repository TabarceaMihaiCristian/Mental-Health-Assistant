import { expect, test } from "@playwright/test";
import { chooseFirstAvailableSlot, loginAs, loginWith, logout, openSpecialistProfileById, provisionBookingActors } from "./helpers";
test.describe.serial("booking oversight flow", () => {
    test("user can request, specialist can confirm, and admin can see the appointment", async ({ page, request }) => {
        const bookingNote = `Playwright E2E ${Date.now()}`;
        const { user, specialist } = await provisionBookingActors(request, "booking-flow");
        await loginWith(page, user);
        await openSpecialistProfileById(page, specialist);
        await chooseFirstAvailableSlot(page);
        await page.getByLabel("Notes").fill(bookingNote);
        await page.getByRole("button", { name: /request appointment/i }).click();
        await expect(page.getByText(/appointment request submitted\./i)).toBeVisible();
        await logout(page);
        await loginWith(page, specialist);
        await page.goto("/specialist/appointments");
        const noteText = page.getByText(bookingNote);
        const specialistCard = noteText.locator("xpath=ancestor::div[contains(@class, 'rounded-[24px]')][1]");
        await expect(specialistCard).toContainText(bookingNote);
        await specialistCard.getByRole("button", { name: /^confirm$/i }).click();
        await expect(specialistCard).toContainText(/confirmed/i);
        await logout(page);
        await loginAs(page, "admin");
        await page.goto("/admin/appointments");
        const adminCard = page.locator("div").filter({ hasText: bookingNote }).first();
        await expect(adminCard).toContainText(bookingNote);
        await expect(adminCard).toContainText(/confirmed/i);
    });
});
