/// <reference types="node" />

import { expect, type APIRequestContext, type Page } from "@playwright/test";

function fromEnv(name: string, fallbackParts: readonly string[]) {
  return process.env[name]?.trim() || fallbackParts.join("");
}

const apiBaseUrl = process.env.PW_API_BASE_URL?.trim() || "http://localhost:8000/api/v1";

export const accounts = {
  user: {
    email: process.env.PW_USER_EMAIL?.trim() || "user.test@mentalhealthapp.com",
    secret: fromEnv("PW_USER_SECRET", ["User", "Test123!"]),
    homePath: "/app",
    heading: /alex marin/i,
  },
  specialist: {
    email: process.env.PW_SPECIALIST_EMAIL?.trim() || "specialist.test@mentalhealthapp.com",
    secret: fromEnv("PW_SPECIALIST_SECRET", ["Specialist", "Test123!"]),
    homePath: "/specialist/dashboard",
    heading: /specialist dashboard/i,
  },
  admin: {
    email: process.env.PW_ADMIN_EMAIL?.trim() || "admin.test@mentalhealthapp.com",
    secret: fromEnv("PW_ADMIN_SECRET", ["Admin", "Test123!"]),
    homePath: "/admin/dashboard",
    heading: /admin dashboard/i,
  },
} as const;

type Role = keyof typeof accounts;

type AdminSpecialistRecord = {
  id: string;
  email: string;
  full_name: string;
};

function escapeForRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, String.raw`\$&`);
}

export async function loginAs(page: Page, role: Role) {
  const account = accounts[role];
  await page.goto("/login");
  await page.getByLabel("Email").fill(account.email);
  await page.getByLabel("Password").fill(account.secret);
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page).not.toHaveURL(/\/login$/);
  await expect(page).toHaveURL(new RegExp(`${escapeForRegExp(account.homePath)}$`));
  await expect(page.getByRole("heading", { level: 1 })).toContainText(account.heading);
  await expect(page.getByRole("button", { name: /logout/i })).toBeVisible();
}

export async function logout(page: Page) {
  await page.getByRole("button", { name: /logout/i }).click();
  await expect(page).toHaveURL(/\/login$/);
}

async function loginViaApi(request: APIRequestContext, role: Role) {
  const account = accounts[role];
  const response = await request.post(`${apiBaseUrl}/auth/login`, {
    data: {
      email: account.email,
      password: account.secret,
    },
  });

  if (!response.ok()) {
    throw new Error(`Playwright API login failed for ${role}: ${response.status()} ${response.statusText()}`);
  }

  const payload = (await response.json()) as { access_token: string };
  return payload.access_token;
}

export async function getSeededSpecialistProfile(request: APIRequestContext) {
  const adminToken = await loginViaApi(request, "admin");
  const response = await request.get(`${apiBaseUrl}/admin/specialists?page=1&page_size=100`, {
    headers: {
      Authorization: `Bearer ${adminToken}`,
    },
  });

  if (!response.ok()) {
    throw new Error(`Unable to load admin specialist directory: ${response.status()} ${response.statusText()}`);
  }

  const payload = (await response.json()) as { items: AdminSpecialistRecord[] };
  const specialist = payload.items.find((item) => item.email === accounts.specialist.email);
  if (!specialist) {
    throw new Error(`No specialist profile matched seeded account ${accounts.specialist.email}.`);
  }

  return specialist;
}

export async function openSpecialistProfile(page: Page, request: APIRequestContext) {
  const specialist = await getSeededSpecialistProfile(request);

  await page.goto(`/specialists/${specialist.id}`);
  await expect(page).toHaveURL(new RegExp(`/specialists/${escapeForRegExp(specialist.id)}$`));
  await expect(page.getByRole("heading", { level: 1 })).toContainText(specialist.full_name);
  return specialist;
}

export async function chooseFirstAvailableSlot(page: Page) {
  await expect.poll(async () => {
    return await page.getByLabel("Choose slot").locator("option").evaluateAll((elements) =>
      elements.filter((element) => (element as HTMLOptionElement).value).length,
    );
  }).toBeGreaterThan(0);

  const minimumFutureOffsetMs = 4 * 60 * 60 * 1000;
  const now = Date.now();
  const options = await page.getByLabel("Choose slot").locator("option").evaluateAll((elements) =>
    elements
      .map((element) => ({
        value: (element as HTMLOptionElement).value,
        label: element.textContent?.trim() ?? "",
      }))
      .filter((item) => item.value),
  );

  const futureOption = options.find((option) => {
    const parsed = Date.parse(option.value);
    return Number.isFinite(parsed) && parsed > now + minimumFutureOffsetMs;
  });

  if (!futureOption) {
    throw new Error("No future appointment slots were available for Playwright booking.");
  }

  await page.getByLabel("Choose slot").selectOption(futureOption.value);
  return futureOption;
}

