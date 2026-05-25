import { expect, test, type APIRequestContext } from "@playwright/test";
import { loginWith, registerTestUser } from "./helpers";

const apiBaseUrl = process.env.PW_API_BASE_URL?.trim() || "http://localhost:8000/api/v1";

type ChatSessionDetail = {
  id: string;
  status: string;
};

type ChatSessionListItem = {
  id: string;
  status: string;
};

async function listSessions(request: APIRequestContext, token: string) {
  const response = await request.get(`${apiBaseUrl}/chat/sessions`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  expect(response.ok()).toBeTruthy();
  return (await response.json()) as ChatSessionListItem[];
}

async function getChatSessionDetail(
  request: APIRequestContext,
  token: string,
  sessionId: string,
) {
  const response = await request.get(`${apiBaseUrl}/chat/sessions/${sessionId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  expect(response.ok()).toBeTruthy();
  return (await response.json()) as ChatSessionDetail;
}

async function generateReport(request: APIRequestContext, token: string, period: "weekly" | "monthly") {
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
    await expect(page.getByText("Thinking...")).toBeVisible();
    await expect(page.getByText("Thinking...")).toHaveCount(0, { timeout: 15_000 });

    let sessionId: string | null = null;
    await expect
      .poll(
        async () => {
          const sessions = await listSessions(request, user.token);
          const targetSession = sessions.find((item) => item.status === "open") ?? sessions[0];
          if (!targetSession) {
            return 0;
          }

          sessionId = targetSession.id;
          return sessions.length;
        },
        {
          timeout: 15_000,
          intervals: [500, 1_000, 1_500],
        },
      )
      .toBeGreaterThanOrEqual(1);

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
