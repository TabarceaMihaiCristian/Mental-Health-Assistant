import { expect, test } from "@playwright/test";
import { createPastConfirmedAppointmentForActors, chooseFirstAvailableSlot, filterFutureSlots, listAvailableSlots, loginAs, loginWith, logout, openSpecialistProfileById, provisionBookingActors, } from "./helpers";
const apiBaseUrl = process.env.PW_API_BASE_URL?.trim() || "http://localhost:8000/api/v1";
function toDateTimeLocal(value) {
    const date = new Date(value);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    return `${year}-${month}-${day}T${hours}:${minutes}`;
}
async function createAppointment(request, userToken, specialistId, preferredDateTime, notes) {
    const response = await request.post(`${apiBaseUrl}/appointments`, {
        headers: {
            Authorization: `Bearer ${userToken}`,
        },
        data: {
            specialist_id: specialistId,
            mode: "online",
            preferred_datetime: preferredDateTime,
            notes,
        },
    });
    if (!response.ok()) {
        throw new Error(`Appointment creation failed: ${response.status()} ${await response.text()}`);
    }
    return (await response.json());
}
async function confirmAppointment(request, specialistToken, appointmentId) {
    const response = await request.patch(`${apiBaseUrl}/specialist/appointments/${appointmentId}/confirm`, {
        headers: {
            Authorization: `Bearer ${specialistToken}`,
        },
    });
    expect(response.ok()).toBeTruthy();
}
test.describe.serial("specialist appointment decisions", () => {
    test("specialist can reject a requested appointment", async ({ page, request }) => {
        const appointmentNote = `Playwright requested decision ${Date.now()}`;
        const rejectionReason = `Playwright rejection ${Date.now()}`;
        const { user, specialist } = await provisionBookingActors(request, "specialist-reject");
        await loginWith(page, user);
        await openSpecialistProfileById(page, specialist);
        await chooseFirstAvailableSlot(page);
        await page.getByLabel("Notes").fill(appointmentNote);
        await page.getByRole("button", { name: /request appointment/i }).click();
        await expect(page.getByText(/appointment request submitted\./i)).toBeVisible();
        await logout(page);
        await loginWith(page, specialist);
        await page.goto("/specialist/appointments");
        const specialistCard = page
            .locator("div")
            .filter({ hasText: appointmentNote })
            .first();
        await expect(specialistCard).toContainText(/requested/i);
        await specialistCard.getByRole("button", { name: /^reject$/i }).click();
        const rejectModal = page.getByText("Reject appointment").locator("xpath=ancestor::div[contains(@class, 'relative z-10')][1]");
        await rejectModal.getByLabel("Reason").fill(rejectionReason);
        await rejectModal.getByRole("button", { name: /confirm rejection/i }).click({ force: true });
        await expect(page.getByText("Reject appointment")).not.toBeVisible();
        await page.goto("/specialist/appointments");
        await expect(specialistCard).toContainText(/rejected/i);
        await logout(page);
        await loginAs(page, "admin");
        await page.goto("/admin/appointments");
        const adminCard = page.locator("div").filter({ hasText: appointmentNote }).first();
        await expect(adminCard).toContainText(appointmentNote);
        await expect(adminCard).toContainText(/rejected/i);
    });
    test("specialist can reschedule a confirmed appointment back to requested", async ({ page, request }) => {
        const appointmentNote = `Playwright confirmed decision ${Date.now()}`;
        const rescheduleNote = `Playwright reschedule ${Date.now()}`;
        const { user, specialist } = await provisionBookingActors(request, "specialist-reschedule");
        await loginWith(page, user);
        await openSpecialistProfileById(page, specialist);
        const slotOptions = filterFutureSlots(await listAvailableSlots(page));
        expect(slotOptions.length).toBeGreaterThanOrEqual(2);
        const appointment = await createAppointment(request, user.token, specialist.specialistId, slotOptions[0].value, appointmentNote);
        await confirmAppointment(request, specialist.token, appointment.id);
        await logout(page);
        await loginWith(page, specialist);
        await page.goto("/specialist/appointments");
        const specialistCard = page
            .locator("div")
            .filter({ hasText: appointmentNote })
            .first();
        await expect(specialistCard).toContainText(/confirmed/i);
        await specialistCard.getByRole("button", { name: /^reschedule$/i }).click();
        const rescheduleModal = page.getByText("Reschedule appointment").locator("xpath=ancestor::div[contains(@class, 'relative z-10')][1]");
        await rescheduleModal.getByLabel("New date and time").fill(toDateTimeLocal(slotOptions[1].value));
        await rescheduleModal.getByLabel("Reschedule note").fill(rescheduleNote);
        await rescheduleModal.getByRole("button", { name: /confirm reschedule/i }).click({ force: true });
        await expect(page.getByText("Reschedule appointment")).not.toBeVisible();
        await page.goto("/specialist/appointments");
        await expect(specialistCard).toContainText(/requested/i);
        await logout(page);
        await loginAs(page, "admin");
        await page.goto("/admin/appointments");
        const adminCard = page.locator("div").filter({ hasText: appointmentNote }).first();
        await expect(adminCard).toContainText(appointmentNote);
        await expect(adminCard).toContainText(/requested/i);
    });
    test("specialist can complete a past confirmed appointment", async ({ page, request }) => {
        const appointmentNote = `Playwright completable decision ${Date.now()}`;
        const { user, specialist } = await provisionBookingActors(request, "specialist-complete");
        await createPastConfirmedAppointmentForActors(user.email, specialist.email, appointmentNote);
        await loginWith(page, specialist);
        await page.goto("/specialist/appointments");
        const specialistCard = page
            .getByText(appointmentNote)
            .locator("xpath=ancestor::div[contains(@class, 'rounded-[24px]')][1]");
        await expect(specialistCard).toContainText(/confirmed/i);
        await specialistCard.getByRole("button", { name: /^complete$/i }).click();
        await page.goto("/specialist/appointments");
        await expect(specialistCard).toContainText(/completed/i);
        await logout(page);
        await loginAs(page, "admin");
        await page.goto("/admin/appointments");
        const adminCard = page.locator("div").filter({ hasText: appointmentNote }).first();
        await expect(adminCard).toContainText(appointmentNote);
        await expect(adminCard).toContainText(/completed/i);
    });
});
