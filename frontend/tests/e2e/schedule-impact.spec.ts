import { expect, test, type APIRequestContext, type Page } from "@playwright/test";
import {
  filterFutureSlots,
  listAvailableSlots,
  loginWith,
  openSpecialistProfileById,
  provisionBookingActors,
  replaceSpecialistAvailability,
} from "./helpers";

const apiBaseUrl = process.env.PW_API_BASE_URL?.trim() || "http://localhost:8000/api/v1";

function addHours(iso: string, hours: number) {
  const date = new Date(iso);
  date.setHours(date.getHours() + hours);
  return date.toISOString();
}

async function listSlotValues(page: Page) {
  return page.getByLabel("Choose slot").locator("option").evaluateAll((elements) =>
    elements
      .map((element) => (element as HTMLOptionElement).value)
      .filter(Boolean),
  );
}

async function createTimeOff(request: APIRequestContext, token: string, startDateTime: string) {
  const response = await request.post(`${apiBaseUrl}/specialists/me/time-off`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    data: {
      start_datetime: startDateTime,
      end_datetime: addHours(startDateTime, 2),
      reason: "Playwright schedule impact time off",
    },
  });

  if (!response.ok()) {
    throw new Error(`Time off creation failed: ${response.status()} ${await response.text()}`);
  }
}

test.describe.serial("specialist schedule impact", () => {
  test("specialist time off removes a previously bookable slot from the user view", async ({ page, request }) => {
    const { user, specialist } = await provisionBookingActors(request, "schedule-impact-timeoff");

    await loginWith(page, user);
    await openSpecialistProfileById(page, specialist);
    const initialSlots = filterFutureSlots(await listAvailableSlots(page));
    expect(initialSlots.length).toBeGreaterThan(0);
    const blockedSlot = initialSlots[0].value;

    await createTimeOff(request, specialist.token, blockedSlot);
    await page.reload();

    await expect.poll(async () => {
      const updatedSlots = await listSlotValues(page);
      return updatedSlots.includes(blockedSlot);
    }).toBeFalsy();
  });

  test("specialist availability changes are reflected in the public booking slots", async ({ page, request }) => {
    const { user, specialist } = await provisionBookingActors(request, "schedule-impact-availability");

    await loginWith(page, user);
    await openSpecialistProfileById(page, specialist);
    const initialSlots = filterFutureSlots(await listAvailableSlots(page));
    expect(initialSlots.length).toBeGreaterThan(0);
    const blockedSlot = initialSlots[0].value;
    const blockedWeekday = new Date(blockedSlot).getUTCDay();

    await replaceSpecialistAvailability(request, specialist.token, [0, 1, 2, 3, 4].filter((weekday) => weekday !== blockedWeekday));
    await page.goto(`/specialists/${specialist.specialistId}`);

    await expect.poll(async () => {
      const updatedSlots = await listSlotValues(page);
      return updatedSlots.includes(blockedSlot);
    }).toBeFalsy();

    await expect.poll(async () => {
      const updatedSlots = await listSlotValues(page);
      return updatedSlots.length;
    }).toBeGreaterThan(0);
  });
});
