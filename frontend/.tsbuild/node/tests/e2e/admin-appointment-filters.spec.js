import { expect, test } from "@playwright/test";
import { loginAs, provisionBookingActors } from "./helpers";
const apiBaseUrl = process.env.PW_API_BASE_URL?.trim() || "http://localhost:8000/api/v1";
const completedNote = "Initial assessment and plan for anxiety management.";
async function getAvailableSlots(request, token, specialistId) {
    const now = new Date();
    const dateFrom = now.toISOString().slice(0, 10);
    const dateToDate = new Date(now);
    dateToDate.setDate(dateToDate.getDate() + 14);
    const dateTo = dateToDate.toISOString().slice(0, 10);
    const response = await request.get(`${apiBaseUrl}/specialists/${specialistId}/availability?date_from=${dateFrom}&date_to=${dateTo}`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    expect(response.ok()).toBeTruthy();
    return (await response.json());
}
async function createAppointment(request, token, specialistId, preferredDateTime, notes) {
    const response = await request.post(`${apiBaseUrl}/appointments`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
        data: {
            specialist_id: specialistId,
            mode: "online",
            preferred_datetime: preferredDateTime,
            notes,
        },
    });
    if (!response.ok()) {
        throw new Error(`Appointment setup failed for "${notes}": ${response.status()} ${await response.text()}`);
    }
    return (await response.json());
}
async function applyStatusFilter(page, status) {
    await page.getByLabel("Status").selectOption(status);
    await page.getByRole("button", { name: /^apply$/i }).click();
}
test.describe.serial("admin appointment filters", () => {
    test("admin can filter appointments across requested, confirmed, rejected, cancelled, and completed", async ({ page, request }) => {
        const requestedNote = `Playwright admin requested ${Date.now()}`;
        const confirmedNote = `Playwright admin confirmed ${Date.now()}`;
        const rejectedNote = `Playwright admin rejected ${Date.now()}`;
        const cancelledNote = `Playwright admin cancelled ${Date.now()}`;
        const { user, specialist } = await provisionBookingActors(request, "admin-filters");
        const availability = await getAvailableSlots(request, user.token, specialist.specialistId);
        const minimumFutureOffsetMs = 4 * 60 * 60 * 1000;
        const candidateSlots = availability.slots
            .map((slot) => slot.start_datetime)
            .filter((slot) => Date.parse(slot) > Date.now() + minimumFutureOffsetMs);
        expect(candidateSlots.length).toBeGreaterThanOrEqual(4);
        await createAppointment(request, user.token, specialist.specialistId, candidateSlots[0], requestedNote);
        const confirmedAppointment = await createAppointment(request, user.token, specialist.specialistId, candidateSlots[1], confirmedNote);
        const rejectedAppointment = await createAppointment(request, user.token, specialist.specialistId, candidateSlots[2], rejectedNote);
        const cancelledAppointment = await createAppointment(request, user.token, specialist.specialistId, candidateSlots[3], cancelledNote);
        const confirmResponse = await request.patch(`${apiBaseUrl}/specialist/appointments/${confirmedAppointment.id}/confirm`, {
            headers: {
                Authorization: `Bearer ${specialist.token}`,
            },
        });
        expect(confirmResponse.ok()).toBeTruthy();
        const rejectResponse = await request.patch(`${apiBaseUrl}/specialist/appointments/${rejectedAppointment.id}/reject`, {
            headers: {
                Authorization: `Bearer ${specialist.token}`,
            },
            data: {
                reason: "Playwright admin filter rejection setup",
            },
        });
        expect(rejectResponse.ok()).toBeTruthy();
        const cancelResponse = await request.patch(`${apiBaseUrl}/appointments/${cancelledAppointment.id}/cancel`, {
            headers: {
                Authorization: `Bearer ${user.token}`,
            },
            data: {
                reason: "Playwright admin filter cancellation setup",
            },
        });
        expect(cancelResponse.ok()).toBeTruthy();
        await loginAs(page, "admin");
        await page.goto("/admin/appointments");
        await applyStatusFilter(page, "requested");
        await expect(page.locator("div").filter({ hasText: requestedNote }).first()).toContainText(/requested/i);
        await expect(page.getByText(rejectedNote)).toHaveCount(0);
        await applyStatusFilter(page, "confirmed");
        await expect(page.locator("div").filter({ hasText: confirmedNote }).first()).toContainText(/confirmed/i);
        await expect(page.getByText(cancelledNote)).toHaveCount(0);
        await applyStatusFilter(page, "rejected");
        await expect(page.locator("div").filter({ hasText: rejectedNote }).first()).toContainText(/rejected/i);
        await expect(page.getByText(requestedNote)).toHaveCount(0);
        await applyStatusFilter(page, "cancelled");
        await expect(page.locator("div").filter({ hasText: cancelledNote }).first()).toContainText(/cancelled/i);
        await expect(page.getByText(confirmedNote)).toHaveCount(0);
        await applyStatusFilter(page, "completed");
        await expect(page.locator("div").filter({ hasText: completedNote }).first()).toContainText(/completed/i);
        await expect(page.getByText(rejectedNote)).toHaveCount(0);
    });
});
