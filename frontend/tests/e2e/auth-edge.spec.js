import { expect, test } from "@playwright/test";
import { accounts, loginAs } from "./helpers";
test.describe.serial("auth edge cases", () => {
    test("invalid login stays on the login page and shows the backend error", async ({ page }) => {
        await page.goto("/login");
        await page.getByLabel("Email").fill(accounts.user.email);
        await page.getByLabel("Password").fill("WrongPassword123!");
        await page.getByRole("button", { name: /sign in/i }).click();
        await expect(page).toHaveURL(/\/login$/);
        await expect(page.getByText("Invalid email or password.")).toBeVisible();
    });
    test("protected routes redirect unauthenticated users and preserve the original destination after login", async ({ page }) => {
        await page.goto("/app");
        await expect(page).toHaveURL(/\/login$/);
        await page.getByLabel("Email").fill(accounts.user.email);
        await page.getByLabel("Password").fill(accounts.user.secret);
        await page.getByRole("button", { name: /sign in/i }).click();
        await expect(page).toHaveURL(/\/app$/);
        await expect(page.getByRole("heading", { level: 1 })).toContainText(/alex marin/i);
    });
    test("logout blocks revisiting a protected page", async ({ page }) => {
        await loginAs(page, "user");
        await page.getByRole("button", { name: /logout/i }).click();
        await expect(page).toHaveURL(/\/login$/);
        await page.goto("/app");
        await expect(page).toHaveURL(/\/login$/);
    });
});
