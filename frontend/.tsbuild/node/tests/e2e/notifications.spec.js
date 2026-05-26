import { expect, test } from "@playwright/test";
import { loginWith, logout, provisionBookingActors, } from "./helpers";
const apiBaseUrl = process.env.PW_API_BASE_URL?.trim() || "http://localhost:8000/api/v1";
async function clearNotifications(request, token) {
    const response = await request.delete(`${apiBaseUrl}/notifications`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    expect(response.ok()).toBeTruthy();
}
async function listNotifications(request, token) {
    const response = await request.get(`${apiBaseUrl}/notifications?page=1&page_size=100`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    expect(response.ok()).toBeTruthy();
    const payload = (await response.json());
    return payload.items;
}
async function createAppointment(request, userToken, specialistId, notes) {
    const now = new Date();
    const dateFrom = now.toISOString().slice(0, 10);
    const dateToDate = new Date(now);
    dateToDate.setDate(dateToDate.getDate() + 14);
    const dateTo = dateToDate.toISOString().slice(0, 10);
    const availabilityResponse = await request.get(`${apiBaseUrl}/specialists/${specialistId}/availability?date_from=${dateFrom}&date_to=${dateTo}`, {
        headers: {
            Authorization: `Bearer ${userToken}`,
        },
    });
    expect(availabilityResponse.ok()).toBeTruthy();
    const availability = (await availabilityResponse.json());
    const slot = availability.slots.find((item) => Date.parse(item.start_datetime) > Date.now() + 4 * 60 * 60 * 1000);
    expect(slot).toBeTruthy();
    const response = await request.post(`${apiBaseUrl}/appointments`, {
        headers: {
            Authorization: `Bearer ${userToken}`,
        },
        data: {
            specialist_id: specialistId,
            mode: "online",
            preferred_datetime: slot?.start_datetime,
            notes,
        },
    });
    expect(response.ok()).toBeTruthy();
}
test.describe.serial("notifications", () => {
    test("booking and confirmation notifications arrive and read state persists", async ({ page, request }) => {
        const bookingNote = `Playwright notification flow ${Date.now()}`;
        const { user, specialist } = await provisionBookingActors(request, "notifications");
        await clearNotifications(request, user.token);
        await clearNotifications(request, specialist.token);
        await createAppointment(request, user.token, specialist.specialistId, bookingNote);
        await loginWith(page, specialist);
        await page.goto("/notifications");
        const specialistNotification = page
            .getByText("New appointment request")
            .locator("xpath=ancestor::div[contains(@class, 'rounded-[24px]')][1]");
        await expect.poll(async () => await specialistNotification.count()).toBeGreaterThan(0);
        await expect(specialistNotification).toContainText(/unread/i);
        await specialistNotification.getByRole("button", { name: /mark read/i }).click();
        await expect(specialistNotification).toContainText(/read/i);
        await page.goto("/notifications");
        await expect(specialistNotification).toContainText(/read/i);
        await page.goto("/specialist/appointments");
        const appointmentCard = page
            .getByText(bookingNote)
            .locator("xpath=ancestor::div[contains(@class, 'rounded-[24px]')][1]");
        await appointmentCard.getByRole("button", { name: /^confirm$/i }).click();
        await expect(appointmentCard).toContainText(/confirmed/i);
        await logout(page);
        await expect
            .poll(async () => {
            const items = await listNotifications(request, user.token);
            return items.filter((item) => item.title === "Appointment confirmed").length;
        })
            .toBeGreaterThan(0);
        await loginWith(page, user);
        await page.goto("/notifications");
        const userNotification = page
            .getByText("Appointment confirmed")
            .first()
            .locator("xpath=ancestor::div[contains(@class, 'rounded-[24px]')][1]");
        await expect(userNotification).toContainText(/unread/i);
        await userNotification.getByRole("button", { name: /mark read/i }).click();
        await expect(userNotification).toContainText(/read/i);
        await userNotification.getByRole("button", { name: /mark unread/i }).click();
        await expect(userNotification).toContainText(/unread/i);
        await page.goto("/notifications");
        await expect(userNotification).toContainText(/unread/i);
    });
});
