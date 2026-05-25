async function waitForBackend(url, attempts = 20, delayMs = 1500) {
    for (let attempt = 1; attempt <= attempts; attempt += 1) {
        try {
            const response = await fetch(url);
            if (response.ok) {
                return;
            }
        }
        catch {
            // keep retrying until the backend is reachable
        }
        await new Promise((resolve) => setTimeout(resolve, delayMs));
    }
    throw new Error(`Backend health check failed at ${url}. Start the API before running Playwright, for example with docker compose up -d backend db.`);
}
export default async function globalSetup() {
    await waitForBackend("http://localhost:8000/api/v1/health");
}
