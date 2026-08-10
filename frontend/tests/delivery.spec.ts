import { expect, test } from "@playwright/test";


const initialRequests = [
  "/api/files",
  "/api/templates",
  "/api/tasks",
  "/api/approvals?status=pending",
  "/api/audit?limit=80",
  "/api/metrics/evaluation",
];

test("Docker frontend reaches every initial API endpoint through browser CORS", async ({ page }) => {
  const responses = Promise.all(
    initialRequests.map((path) =>
      page.waitForResponse((response) => {
        const url = new URL(response.url());
        return `${url.pathname}${url.search}` === path;
      }),
    ),
  );

  await page.goto("/");

  for (const response of await responses) {
    expect(response.status(), response.url()).toBe(200);
    expect(response.headers()["access-control-allow-origin"], response.url()).toBe("http://127.0.0.1:4173");
  }
});
