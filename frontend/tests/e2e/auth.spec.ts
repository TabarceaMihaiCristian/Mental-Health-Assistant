import { test } from "@playwright/test";
import { loginAs, logout } from "./helpers";

test.describe("role authentication", () => {
  test("user can sign in to the user dashboard", async ({ page }) => {
    await loginAs(page, "user");
    await logout(page);
  });

  test("specialist can sign in to the specialist dashboard", async ({ page }) => {
    await loginAs(page, "specialist");
    await logout(page);
  });

  test("admin can sign in to the admin dashboard", async ({ page }) => {
    await loginAs(page, "admin");
    await logout(page);
  });
});
