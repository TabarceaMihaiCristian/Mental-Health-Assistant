import { type APIRequestContext, type Page } from "@playwright/test";
export declare const accounts: {
    readonly user: {
        readonly email: string;
        readonly secret: string;
        readonly homePath: "/app";
        readonly heading: RegExp;
    };
    readonly specialist: {
        readonly email: string;
        readonly secret: string;
        readonly homePath: "/specialist/dashboard";
        readonly heading: RegExp;
    };
    readonly admin: {
        readonly email: string;
        readonly secret: string;
        readonly homePath: "/admin/dashboard";
        readonly heading: RegExp;
    };
};
type Role = keyof typeof accounts;
type AdminSpecialistRecord = {
    id: string;
    email: string;
    full_name: string;
};
type LoginAccount = {
    email: string;
    password: string;
    homePath: string;
    heading: RegExp;
};
export type ProvisionedUserAccount = LoginAccount & {
    userId: string;
    fullName: string;
    token: string;
};
export type ProvisionedSpecialistAccount = LoginAccount & {
    specialistId: string;
    fullName: string;
    token: string;
};
export declare function loginWith(page: Page, options: {
    email: string;
    password: string;
    homePath: string;
    heading: RegExp;
}): Promise<void>;
export declare function loginAs(page: Page, role: Role): Promise<void>;
export declare function logout(page: Page): Promise<void>;
export declare function loginViaApi(request: APIRequestContext, role: Role): Promise<string>;
export declare function loginViaApiWithCredentials(request: APIRequestContext, credentials: {
    email: string;
    password: string;
}): Promise<string>;
export declare function registerTestUser(request: APIRequestContext, prefix?: string): Promise<ProvisionedUserAccount>;
export declare function createTestSpecialist(request: APIRequestContext, prefix?: string): Promise<ProvisionedSpecialistAccount>;
export declare function replaceSpecialistAvailability(request: APIRequestContext, specialistToken: string, weekdays: number[]): Promise<void>;
export declare function provisionBookingActors(request: APIRequestContext, prefix: string): Promise<{
    user: LoginAccount & {
        userId: string;
        fullName: string;
        token: string;
    };
    specialist: LoginAccount & {
        specialistId: string;
        fullName: string;
        token: string;
    };
}>;
export declare function reseedDemoData(): Promise<void>;
export declare function createPastConfirmedAppointmentForActors(userEmail: string, specialistEmail: string, notes: string): Promise<void>;
export declare function getSeededSpecialistProfile(request: APIRequestContext): Promise<AdminSpecialistRecord>;
export declare function openSpecialistProfileById(page: Page, specialist: {
    specialistId: string;
    fullName: string;
}): Promise<{
    specialistId: string;
    fullName: string;
}>;
export declare function openSpecialistProfile(page: Page, request: APIRequestContext): Promise<{
    specialistId: string;
    fullName: string;
}>;
export declare function chooseFirstAvailableSlot(page: Page): Promise<{
    value: string;
    label: string;
}>;
export declare function listAvailableSlots(page: Page): Promise<{
    value: string;
    label: string;
}[]>;
export declare function filterFutureSlots(options: Array<{
    value: string;
    label: string;
}>, minimumFutureOffsetMs?: number): {
    value: string;
    label: string;
}[];
export {};
