import { expect, test } from "@playwright/test";
import { loginAs, loginWith, logout } from "./helpers";

test.describe.serial("admin specialist management", () => {
  test("admin can create a specialist, toggle visibility, and the specialist can sign in", async ({ page }) => {
    const uniqueSuffix = Date.now();
    const specialistName = `Dr. E2E Specialist ${uniqueSuffix}`;
    const specialistEmail = `specialist.e2e.${uniqueSuffix}@mentalhealthapp.com`;
    const specialistPassword = `E2ESpecialist${uniqueSuffix}!`;

    await loginAs(page, "admin");
    await page.getByRole("link", { name: /^specialists$/i }).click();
    await expect(page).toHaveURL(/\/admin\/specialists$/);
    await expect(page.getByRole("heading", { level: 1, name: /specialist management/i })).toBeVisible();

    await page.getByLabel("Full name").first().fill(specialistName);
    await page.getByLabel("Email").first().fill(specialistEmail);
    await page.getByLabel("Password").first().fill(specialistPassword);
    await page.getByLabel("Specialty").first().fill("Stress Management");
    await page.getByLabel("Consultation modes").first().fill("online, onsite");
    await page.getByLabel("City").first().fill("Bucharest");
    await page.getByLabel("Bio").first().fill("Playwright created specialist for E2E verification.");
    await page.getByRole("button", { name: /create specialist/i }).click();

    await expect(page.getByText(`Created specialist account for ${specialistName}.`)).toBeVisible();

    await page.getByLabel(/search by name, specialty, or email/i).fill(specialistEmail);
    const specialistCard = page.getByText(specialistEmail).locator("xpath=ancestor::div[contains(@class, 'rounded-[22px]')][1]");
    await expect(specialistCard).toContainText(specialistName);
    await expect(specialistCard).toContainText(/active/i);

    await specialistCard.getByRole("button", { name: /deactivate/i }).click();
    await expect(page.getByText(`${specialistName} is now inactive.`)).toBeVisible();
    await expect(specialistCard).toContainText(/inactive/i);

    await specialistCard.getByRole("button", { name: /activate/i }).click();
    await expect(page.getByText(`${specialistName} is now active.`)).toBeVisible();
    await expect(specialistCard).toContainText(/active/i);
    await logout(page);

    await loginWith(page, {
      email: specialistEmail,
      password: specialistPassword,
      homePath: "/specialist/dashboard",
      heading: /specialist dashboard/i,
    });
    await logout(page);
  });
});

