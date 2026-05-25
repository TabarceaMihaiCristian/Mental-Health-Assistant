import { expect, test } from "@playwright/test";
import { chooseFirstAvailableSlot, filterFutureSlots, listAvailableSlots, loginAs, loginWith, logout, openSpecialistProfileById, provisionBookingActors, } from "./helpers";
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
}
async function confirmLatestAppointment(request, specialistToken) {
    const appointmentsResponse = await request.get(`${apiBaseUrl}/specialist/appointments`, {
        headers: {
            Authorization: `Bearer ${specialistToken}`,
        },
    });
    expect(appointmentsResponse.ok()).toBeTruthy();
    const appointments = (await appointmentsResponse.json());
    const latestAppointment = appointments.at(0);
    expect(latestAppointment).toBeTruthy();
    const confirmResponse = await request.patch(`${apiBaseUrl}/specialist/appointments/${latestAppointment?.id}/confirm`, {
        headers: {
            Authorization: `Bearer ${specialistToken}`,
        },
    });
    expect(confirmResponse.ok()).toBeTruthy();
}
test.describe.serial("user appointment lifecycle", () => {
    test("user can cancel a requested appointment", async ({ page, request }) => {
        const cancellationReason = `Playwright cancel ${Date.now()}`;
        const requestedNote = `Playwright requested lifecycle ${Date.now()}`;
        const { user, specialist } = await provisionBookingActors(request, "user-cancel");
        await loginWith(page, user);
        await openSpecialistProfileById(page, specialist);
        await chooseFirstAvailableSlot(page);
        await page.getByLabel("Notes").fill(requestedNote);
        await page.getByRole("button", { name: /request appointment/i }).click();
        await expect(page.getByText(/appointment request submitted\./i)).toBeVisible();
        await page.goto("/appointments");
        const requestedCard = page
            .getByRole("button", { name: /^cancel$/i })
            .first()
            .locator("xpath=ancestor::div[contains(@class, 'rounded-[24px]')][1]");
        await expect(requestedCard).toContainText(/requested/i);
        await requestedCard.getByRole("button", { name: /^cancel$/i }).click();
        const cancelModal = page.getByText("Cancel appointment").locator("xpath=ancestor::div[contains(@class, 'relative z-10')][1]");
        await cancelModal.getByLabel("Cancellation reason").fill(cancellationReason);
        await cancelModal.getByRole("button", { name: /confirm cancellation/i }).click({ force: true });
        await expect(page.getByText("Cancel appointment")).not.toBeVisible();
        await expect(page.getByText(/appointment cancelled\./i)).toBeVisible();
        await logout(page);
        await loginAs(page, "admin");
        await page.goto("/admin/appointments");
        const adminCard = page.locator("div").filter({ hasText: cancellationReason }).first();
        await expect(adminCard).toContainText(cancellationReason);
        await expect(adminCard).toContainText(/cancelled/i);
    });
    test("user can reschedule a confirmed appointment back to requested", async ({ page, request }) => {
        const appointmentNote = `Playwright confirmed lifecycle ${Date.now()}`;
        const rescheduleNote = `Playwright user reschedule ${Date.now()}`;
        const { user, specialist } = await provisionBookingActors(request, "user-reschedule");
        await loginWith(page, user);
        await openSpecialistProfileById(page, specialist);
        const slotOptions = filterFutureSlots(await listAvailableSlots(page));
        expect(slotOptions.length).toBeGreaterThanOrEqual(2);
        await createAppointment(request, user.token, specialist.specialistId, slotOptions[0].value, appointmentNote);
        await confirmLatestAppointment(request, specialist.token);
        await page.goto("/appointments");
        const confirmedCard = page
            .getByRole("button", { name: /^reschedule$/i })
            .first()
            .locator("xpath=ancestor::div[contains(@class, 'rounded-[24px]')][1]");
        await expect(confirmedCard).toContainText(/confirmed/i);
        await confirmedCard.getByRole("button", { name: /^reschedule$/i }).click();
        const rescheduleModal = page.getByText("Reschedule appointment").locator("xpath=ancestor::div[contains(@class, 'relative z-10')][1]");
        await rescheduleModal.getByLabel("New appointment date and time").fill(toDateTimeLocal(slotOptions[1].value));
        await rescheduleModal.getByLabel("Reschedule note").fill(rescheduleNote);
        await rescheduleModal.getByRole("button", { name: /confirm reschedule/i }).click({ force: true });
        await expect(page.getByText("Reschedule appointment")).not.toBeVisible();
        await expect(page.getByText(/appointment rescheduled\./i)).toBeVisible();
        await logout(page);
        await loginAs(page, "admin");
        await page.goto("/admin/appointments");
        const adminCard = page.locator("div").filter({ hasText: appointmentNote }).first();
        await expect(adminCard).toContainText(appointmentNote);
        await expect(adminCard).toContainText(/requested/i);
    });
});
