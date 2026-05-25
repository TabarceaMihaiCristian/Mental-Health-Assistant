/// <reference types="node" />
import { spawnSync } from "node:child_process";
import path from "node:path";
import { expect } from "@playwright/test";
function fromEnv(name, fallbackParts) {
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
};
const repoRoot = path.resolve(import.meta.dirname, "..", "..", "..");
const backendRoot = path.join(repoRoot, "backend");
function escapeForRegExp(value) {
    return value.replace(/[.*+?^${}()|[\]\\]/g, String.raw `\$&`);
}
export async function loginWith(page, options) {
    await page.goto("/login");
    await page.getByLabel("Email").fill(options.email);
    await page.getByLabel("Password").fill(options.password);
    await page.getByRole("button", { name: /sign in/i }).click();
    await expect(page).not.toHaveURL(/\/login$/);
    await expect(page).toHaveURL(new RegExp(`${escapeForRegExp(options.homePath)}$`));
    await expect(page.getByRole("heading", { level: 1 })).toContainText(options.heading);
    await expect(page.getByRole("button", { name: /logout/i })).toBeVisible();
}
export async function loginAs(page, role) {
    const account = accounts[role];
    await loginWith(page, {
        email: account.email,
        password: account.secret,
        homePath: account.homePath,
        heading: account.heading,
    });
}
export async function logout(page) {
    await page.getByRole("button", { name: /logout/i }).click();
    await expect(page).toHaveURL(/\/login$/);
}
export async function loginViaApi(request, role) {
    const account = accounts[role];
    return loginViaApiWithCredentials(request, {
        email: account.email,
        password: account.secret,
    });
}
export async function loginViaApiWithCredentials(request, credentials) {
    let lastError = null;
    for (let attempt = 1; attempt <= 3; attempt += 1) {
        try {
            const response = await request.post(`${apiBaseUrl}/auth/login`, {
                data: {
                    email: credentials.email,
                    password: credentials.password,
                },
            });
            if (!response.ok()) {
                throw new Error(`Playwright API login failed for ${credentials.email}: ${response.status()} ${response.statusText()}`);
            }
            const payload = (await response.json());
            return payload.access_token;
        }
        catch (error) {
            lastError = error;
            if (attempt < 3) {
                await new Promise((resolve) => setTimeout(resolve, 500));
            }
        }
    }
    throw lastError instanceof Error ? lastError : new Error("Playwright API login failed unexpectedly.");
}
function buildUniqueValue(prefix) {
    const random = Math.random().toString(36).slice(2, 8);
    return `${prefix}-${Date.now()}-${random}`;
}
export async function registerTestUser(request, prefix = "playwright-user") {
    const uniqueValue = buildUniqueValue(prefix);
    const fullName = `Playwright ${uniqueValue}`;
    const email = `${uniqueValue}@mentalhealthapp.com`;
    const password = "PlaywrightUser123!";
    const response = await request.post(`${apiBaseUrl}/auth/register`, {
        data: {
            email,
            full_name: fullName,
            password,
        },
    });
    if (!response.ok()) {
        throw new Error(`Playwright user registration failed: ${response.status()} ${await response.text()}`);
    }
    const payload = (await response.json());
    return {
        email,
        password,
        homePath: "/app",
        heading: new RegExp(fullName, "i"),
        userId: payload.user.id,
        fullName,
        token: payload.access_token,
    };
}
export async function createTestSpecialist(request, prefix = "playwright-specialist") {
    const adminToken = await loginViaApi(request, "admin");
    const uniqueValue = buildUniqueValue(prefix);
    const fullName = `Dr. ${uniqueValue}`;
    const email = `${uniqueValue}@mentalhealthapp.com`;
    const password = "PlaywrightSpecialist123!";
    const response = await request.post(`${apiBaseUrl}/admin/specialists`, {
        headers: {
            Authorization: `Bearer ${adminToken}`,
        },
        data: {
            email,
            full_name: fullName,
            password,
            specialty: "Stress Management",
            bio: "Playwright-owned specialist profile for E2E isolation.",
            consultation_modes: ["online"],
            city: "Bucharest",
        },
    });
    if (!response.ok()) {
        throw new Error(`Playwright specialist creation failed: ${response.status()} ${await response.text()}`);
    }
    const payload = (await response.json());
    const token = await loginViaApiWithCredentials(request, { email, password });
    await replaceSpecialistAvailability(request, token, [0, 1, 2, 3, 4]);
    return {
        email,
        password,
        homePath: "/specialist/dashboard",
        heading: /specialist dashboard/i,
        specialistId: payload.id,
        fullName,
        token,
    };
}
export async function replaceSpecialistAvailability(request, specialistToken, weekdays) {
    const response = await request.put(`${apiBaseUrl}/specialists/me/availability`, {
        headers: {
            Authorization: `Bearer ${specialistToken}`,
        },
        data: weekdays.map((weekday) => ({
            weekday,
            start_time: "09:00:00",
            end_time: "17:00:00",
            is_enabled: true,
        })),
    });
    if (!response.ok()) {
        throw new Error(`Replacing specialist availability failed: ${response.status()} ${await response.text()}`);
    }
}
export async function provisionBookingActors(request, prefix) {
    const [user, specialist] = await Promise.all([
        registerTestUser(request, `${prefix}-user`),
        createTestSpecialist(request, `${prefix}-specialist`),
    ]);
    return { user, specialist };
}
async function waitForBackendHealth(url, attempts = 20, delayMs = 500) {
    for (let attempt = 1; attempt <= attempts; attempt += 1) {
        try {
            const response = await fetch(url);
            if (response.ok) {
                return;
            }
        }
        catch {
            // keep retrying until the backend is reachable again after reseed
        }
        await new Promise((resolve) => setTimeout(resolve, delayMs));
    }
    throw new Error(`Backend health check failed after reseed at ${url}.`);
}
function runBackendScript(moduleName, args) {
    const dockerScript = spawnSync("docker", ["compose", "exec", "-T", "backend", "python", "-m", moduleName, ...args], {
        cwd: repoRoot,
        encoding: "utf-8",
    });
    const windowsPython = path.join(backendRoot, ".venv", "Scripts", "python.exe");
    const unixPython = path.join(backendRoot, ".venv", "bin", "python");
    const pythonExecutable = process.platform === "win32" ? windowsPython : unixPython;
    const fallbackExecutable = process.platform === "win32" ? "python" : "python3";
    const executable = process.env.PW_BACKEND_PYTHON?.trim() || pythonExecutable;
    const localScript = spawnSync(executable, ["-m", moduleName, ...args], {
        cwd: backendRoot,
        encoding: "utf-8",
    });
    if (dockerScript.status === 0) {
        return;
    }
    if (localScript.error && executable !== fallbackExecutable) {
        const retried = spawnSync(fallbackExecutable, ["-m", moduleName, ...args], {
            cwd: backendRoot,
            encoding: "utf-8",
        });
        if (retried.status === 0) {
            return;
        }
        const stderr = retried.stderr?.trim() || retried.stdout?.trim() || retried.error?.message || "Unknown backend script failure.";
        throw new Error(`Playwright backend helper failed via ${fallbackExecutable}: ${stderr}`);
    }
    if (localScript.status !== 0) {
        const stderr = localScript.stderr?.trim() || localScript.stdout?.trim() || localScript.error?.message || "Unknown backend script failure.";
        const dockerError = dockerScript.stderr?.trim() || dockerScript.stdout?.trim() || dockerScript.error?.message || "Docker backend helper was unavailable.";
        throw new Error(`Playwright backend helper failed via docker and local python. Docker: ${dockerError} Local (${executable}): ${stderr}`);
    }
}
export async function reseedDemoData() {
    runBackendScript("app.scripts.seed_demo_data", []);
    await waitForBackendHealth("http://localhost:8000/api/v1/health");
}
export async function createPastConfirmedAppointmentForActors(userEmail, specialistEmail, notes) {
    runBackendScript("app.scripts.create_test_past_confirmed_appointment", [
        "--user-email",
        userEmail,
        "--specialist-email",
        specialistEmail,
        "--notes",
        notes,
    ]);
}
export async function getSeededSpecialistProfile(request) {
    const adminToken = await loginViaApi(request, "admin");
    const response = await request.get(`${apiBaseUrl}/admin/specialists?page=1&page_size=100`, {
        headers: {
            Authorization: `Bearer ${adminToken}`,
        },
    });
    if (!response.ok()) {
        throw new Error(`Unable to load admin specialist directory: ${response.status()} ${response.statusText()}`);
    }
    const payload = (await response.json());
    const specialist = payload.items.find((item) => item.email === accounts.specialist.email);
    if (!specialist) {
        throw new Error(`No specialist profile matched seeded account ${accounts.specialist.email}.`);
    }
    return specialist;
}
export async function openSpecialistProfileById(page, specialist) {
    await page.goto(`/specialists/${specialist.specialistId}`);
    await expect(page).toHaveURL(new RegExp(`/specialists/${escapeForRegExp(specialist.specialistId)}$`));
    await expect(page.getByRole("heading", { level: 1 })).toContainText(specialist.fullName);
    return specialist;
}
export async function openSpecialistProfile(page, request) {
    const specialist = await getSeededSpecialistProfile(request);
    return openSpecialistProfileById(page, {
        specialistId: specialist.id,
        fullName: specialist.full_name,
    });
}
export async function chooseFirstAvailableSlot(page) {
    const options = await listAvailableSlots(page);
    const futureOption = findFutureSlot(options, 4 * 60 * 60 * 1000);
    if (!futureOption) {
        throw new Error("No future appointment slots were available for Playwright booking.");
    }
    await page.getByLabel("Choose slot").selectOption(futureOption.value);
    return futureOption;
}
export async function listAvailableSlots(page) {
    await expect.poll(async () => {
        return await page.getByLabel("Choose slot").locator("option").evaluateAll((elements) => elements.filter((element) => element.value).length);
    }).toBeGreaterThan(0);
    return page.getByLabel("Choose slot").locator("option").evaluateAll((elements) => elements
        .map((element) => ({
        value: element.value,
        label: element.textContent?.trim() ?? "",
    }))
        .filter((item) => item.value));
}
function findFutureSlot(options, minimumFutureOffsetMs) {
    const now = Date.now();
    return options.find((option) => {
        const parsed = Date.parse(option.value);
        return Number.isFinite(parsed) && parsed > now + minimumFutureOffsetMs;
    });
}
export function filterFutureSlots(options, minimumFutureOffsetMs = 4 * 60 * 60 * 1000) {
    const now = Date.now();
    return options.filter((option) => {
        const parsed = Date.parse(option.value);
        return Number.isFinite(parsed) && parsed > now + minimumFutureOffsetMs;
    });
}
