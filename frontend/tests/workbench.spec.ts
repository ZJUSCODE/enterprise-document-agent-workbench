import { expect, test } from "@playwright/test";


test("workbench exposes the primary document-agent surfaces", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "企业文档流程自动化" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "把文档交给 Agent" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "处理进度" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "需要确认的结果" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "向文档提问" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "质量指标" })).toBeVisible();
});
