import { expect, test } from "@playwright/test";
import { loginWith, registerTestUser } from "./helpers";
const apiBaseUrl = process.env.PW_API_BASE_URL?.trim() || "http://localhost:8000/api/v1";
async function getOpenSessionId(request, token) {
    const response = await request.get(`${apiBaseUrl}/chat/sessions/open`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    expect(response.ok()).toBeTruthy();
    const payload = (await response.json());
    return payload?.id ?? null;
}
async function getChatSessionDetail(request, token, sessionId) {
    const response = await request.get(`${apiBaseUrl}/chat/sessions/${sessionId}`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    expect(response.ok()).toBeTruthy();
    return (await response.json());
}
async function generateReport(request, token, period) {
    const response = await request.post(`${apiBaseUrl}/reports/${period}`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    expect(response.ok()).toBeTruthy();
}
test.describe.serial("chat and reports", () => {
    test("user can send a chat message, close the session, and generate weekly and monthly reports", async ({ page, request }) => {
        const user = await registerTestUser(request, "chat-reports");
        const chatMessage = `Playwright chat flow ${Date.now()} - I felt calmer after a walk and journaling.`;
        await loginWith(page, user);
        await page.goto("/chat");
        await page.getByLabel("Message").fill(chatMessage);
        await page.getByRole("button", { name: /send message/i }).click();
        await expect(page.getByText(chatMessage)).toBeVisible();
        let sessionId = null;
        await expect
            .poll(async () => {
            const openSessionId = await getOpenSessionId(request, user.token);
            if (!openSessionId) {
                return 0;
            }
            const session = await getChatSessionDetail(request, user.token, openSessionId);
            if (session.messages.length >= 2) {
                sessionId = session.id;
            }
            return session.messages.length;
        }, {
            timeout: 15_000,
            intervals: [500, 1_000, 1_500],
        })
            .toBeGreaterThanOrEqual(2);
        await page.getByRole("button", { name: /close session/i }).click();
        await expect.poll(async () => {
            const session = await getChatSessionDetail(request, user.token, sessionId ?? "");
            return session.status;
        }).toBe("closed");
        await generateReport(request, user.token, "weekly");
        await generateReport(request, user.token, "monthly");
        await page.goto("/reports");
        await expect(page.getByText("Daily mood summaries")).toBeVisible();
        await expect(page.getByRole("heading", { name: /weekly report/i })).toBeVisible();
        await expect(page.getByRole("heading", { name: /monthly report/i })).toBeVisible();
        await expect(page.getByText(/days with data:/i).first()).toBeVisible();
        await expect(page.getByText(/highest risk:/i).first()).toBeVisible();
        await expect(page.getByText(/no generated report yet\./i)).toHaveCount(0);
    });
});
