import { expect, test, type APIRequestContext, type Page } from "@playwright/test";
import {
  createPastConfirmedAppointmentForActors,
  chooseFirstAvailableSlot,
  filterFutureSlots,
  loginViaApi,
  listAvailableSlots,
  loginAs,
  loginWith,
  logout,
  openSpecialistProfileById,
  provisionBookingActors,
} from "./helpers";

const apiBaseUrl = process.env.PW_API_BASE_URL?.trim() || "http://localhost:8000/api/v1";

async function createAppointment(
  request: APIRequestContext,
  userToken: string,
  specialistId: string,
  preferredDateTime: string,
  notes: string,
) {
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

  return (await response.json()) as { id: string };
}

async function createConfirmedAppointmentForSpecialist(
  request: APIRequestContext,
  specialistToken: string,
  userId: string,
  preferredDateTime: string,
  notes: string,
) {
  const response = await request.post(`${apiBaseUrl}/specialist/appointments`, {
    headers: {
      Authorization: `Bearer ${specialistToken}`,
    },
    data: {
      user_id: userId,
      mode: "online",
      preferred_datetime: preferredDateTime,
      notes,
    },
  });

  if (!response.ok()) {
    throw new Error(`Specialist appointment creation failed: ${response.status()} ${await response.text()}`);
  }

  return (await response.json()) as { id: string };
}

async function rescheduleAppointmentAsSpecialist(
  request: APIRequestContext,
  specialistToken: string,
  appointmentId: string,
  preferredDateTime: string,
  note: string,
) {
  const response = await request.patch(`${apiBaseUrl}/specialist/appointments/${appointmentId}/reschedule`, {
    headers: {
      Authorization: `Bearer ${specialistToken}`,
    },
    data: {
      preferred_datetime: preferredDateTime,
      note,
    },
  });

  if (!response.ok()) {
    throw new Error(`Specialist appointment reschedule failed: ${response.status()} ${await response.text()}`);
  }

  return (await response.json()) as { status: string; reschedule_note: string | null };
}

async function getAdminAppointment(
  request: APIRequestContext,
  adminToken: string,
  appointmentId: string,
) {
  const response = await request.get(`${apiBaseUrl}/admin/appointments/${appointmentId}`, {
    headers: {
      Authorization: `Bearer ${adminToken}`,
    },
  });
  expect(response.ok()).toBeTruthy();
  return (await response.json()) as { notes: string | null; status: string };
}

async function openSpecialistAppointments(page: Page, specialist: { email: string; password: string; homePath: string; heading: RegExp }) {
  await page.goto("/specialist/appointments");

  if (/\/login$/.test(page.url())) {
    await loginWith(page, specialist);
    await page.goto("/specialist/appointments");
  }

  await expect(page).toHaveURL(/\/specialist\/appointments$/);
  await expect(page.getByRole("heading", { name: /assigned appointments/i })).toBeVisible();
}

test.describe.serial("specialist appointment decisions", () => {
  test("specialist can reject a requested appointment", async ({ page, request }) => {
    const appointmentNote = `Playwright requested decision ${Date.now()}`;
    const rejectionReason = `Playwright rejection ${Date.now()}`;
    const { user, specialist } = await provisionBookingActors(request, "specialist-reject");

    await loginWith(page, user);
    await openSpecialistProfileById(page, specialist);
    const slot = await chooseFirstAvailableSlot(page);
    await logout(page);

    const appointment = await createAppointment(
      request,
      user.token,
      specialist.specialistId,
      slot.value,
      appointmentNote,
    );

    await loginWith(page, specialist);
    await openSpecialistAppointments(page, specialist);

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

    const adminToken = await loginViaApi(request, "admin");
    await expect
      .poll(async () => {
        const adminAppointment = await getAdminAppointment(request, adminToken, appointment.id);
        return adminAppointment.status;
      })
      .toBe("rejected");

    const adminAppointment = await getAdminAppointment(request, adminToken, appointment.id);
    expect(adminAppointment.notes).toBe(appointmentNote);

    await loginAs(page, "admin");
    await page.goto("/admin/appointments");
    await expect(page.getByRole("heading", { name: /appointment records/i })).toBeVisible();
  });

  test("specialist can reschedule a confirmed appointment back to requested", async ({ page, request }) => {
    const appointmentNote = `Playwright confirmed decision ${Date.now()}`;
    const rescheduleNote = `Playwright reschedule ${Date.now()}`;
    const { user, specialist } = await provisionBookingActors(request, "specialist-reschedule");

    await loginWith(page, user);
    await openSpecialistProfileById(page, specialist);
    const slotOptions = filterFutureSlots(await listAvailableSlots(page));
    expect(slotOptions.length).toBeGreaterThanOrEqual(2);
    await logout(page);

    const appointment = await createConfirmedAppointmentForSpecialist(
      request,
      specialist.token,
      user.userId,
      slotOptions[0].value,
      appointmentNote,
    );

    await loginWith(page, specialist);
    await openSpecialistAppointments(page, specialist);
    await logout(page);

    const rescheduled = await rescheduleAppointmentAsSpecialist(
      request,
      specialist.token,
      appointment.id,
      slotOptions[1].value,
      rescheduleNote,
    );
    expect(rescheduled.status).toBe("requested");
    expect(rescheduled.reschedule_note).toBe(rescheduleNote);

    const adminToken = await loginViaApi(request, "admin");
    await expect
      .poll(async () => {
        const adminAppointment = await getAdminAppointment(request, adminToken, appointment.id);
        return adminAppointment.status;
      })
      .toBe("requested");

    const adminAppointment = await getAdminAppointment(request, adminToken, appointment.id);
    expect(adminAppointment.notes).toBe(appointmentNote);

    await loginAs(page, "admin");
    await page.goto("/admin/appointments");
    await expect(page.getByRole("heading", { name: /appointment records/i })).toBeVisible();
  });

  test("specialist can complete a past confirmed appointment", async ({ page, request }) => {
    const appointmentNote = `Playwright completable decision ${Date.now()}`;
    const { user, specialist } = await provisionBookingActors(request, "specialist-complete");
    const appointmentId = await createPastConfirmedAppointmentForActors(user.email, specialist.email, appointmentNote);

    await loginWith(page, specialist);
    await openSpecialistAppointments(page, specialist);

    const specialistCard = page
      .getByText(appointmentNote)
      .locator("xpath=ancestor::div[contains(@class, 'rounded-[24px]')][1]");

    await expect(specialistCard).toContainText(/confirmed/i);
    await specialistCard.getByRole("button", { name: /^complete$/i }).click();
    await page.goto("/specialist/appointments");
    await expect(specialistCard).toContainText(/completed/i);
    await logout(page);

    const adminToken = await loginViaApi(request, "admin");
    await expect
      .poll(async () => {
        const appointment = await getAdminAppointment(request, adminToken, appointmentId);
        return appointment.status;
      })
      .toBe("completed");

    const appointment = await getAdminAppointment(request, adminToken, appointmentId);
    expect(appointment.notes).toBe(appointmentNote);

    await loginAs(page, "admin");
    await page.goto("/admin/appointments");
    await expect(page.getByRole("heading", { name: /appointment records/i })).toBeVisible();
  });
});
