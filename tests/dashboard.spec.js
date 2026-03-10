const path = require("path");

function loadPlaywrightTest() {
  const candidates = ["@playwright/test", "playwright/test"];

  for (const request of candidates) {
    try {
      return require(request);
    } catch (error) {
      continue;
    }
  }

  const fallbackPaths = [];
  if (require.main?.filename) {
    fallbackPaths.push(path.dirname(require.main.filename));
  }
  fallbackPaths.push(...module.paths);

  for (const basePath of fallbackPaths) {
    for (const request of candidates) {
      try {
        return require(require.resolve(request, { paths: [basePath] }));
      } catch (error) {
        continue;
      }
    }
  }

  throw new Error("Playwright test runner could not be resolved from the current environment.");
}

const { test, expect } = loadPlaywrightTest();

const dashboardUrl = `file://${path.resolve(__dirname, "..", "dashboard.html")}`;
const csvPath = path.resolve(__dirname, "..", "joe_rogan_episodes.csv");

test("dashboard loads the CSV and supports filtering and drill-down", async ({ page }) => {
  await page.goto(dashboardUrl);

  await page.setInputFiles("#csv-file", csvPath);

  await expect(page.locator('[data-stat="episode-count"] .stat-value')).toHaveText("2,651");
  await expect(page.locator("#results-summary")).toContainText("Showing 1-10 of 2,651 filtered episodes");
  await expect(page.locator("#episode-table-body tr")).toHaveCount(10);
  await expect(page.locator("#page-size")).toHaveValue("10");
  await expect(page.locator("#prev-page")).toBeDisabled();

  await page.getByLabel("Search episodes").fill("2026-03-05");
  await expect(page.locator('[data-stat="episode-count"] .stat-value')).toHaveText("1");
  await expect(page.locator("#results-summary")).toContainText("1 filtered episode");
  await expect(page.locator("#episode-table-body tr")).toHaveCount(1);

  await page.getByRole("button", { name: /#2464 - Priyanka Chopra Jonas/i }).click();
  await expect(page.locator("#episode-detail-title")).toContainText("Priyanka Chopra Jonas");
  await expect(page.locator("#detail-content")).toContainText("Mar 5, 2026");

  await page.getByRole("button", { name: "Reset filters" }).click();
  await expect(page.locator("#page-size")).toHaveValue("10");
  await expect(page.locator("#episode-table-body tr")).toHaveCount(10);

  await page.locator("#page-size").selectOption("25");
  await expect(page.locator("#results-summary")).toContainText("Showing 1-25 of 2,651 filtered episodes");
  await expect(page.locator("#episode-table-body tr")).toHaveCount(25);

  await page.locator('#page-numbers button[data-page="3"]').click();
  await expect(page.locator("#page-copy")).toHaveText("Page 3 of 107");
  await expect(page.locator("#results-summary")).toContainText("Showing 51-75 of 2,651 filtered episodes");
  await expect(page.locator('#page-numbers button[aria-current="page"]')).toHaveText("3");
  await expect(page.locator("#prev-page")).toBeEnabled();

  await page.getByRole("button", { name: "Reset filters" }).click();
  await page.getByLabel("Series type").selectOption("JRE MMA Show");
  await expect(page.locator('[data-stat="episode-count"] .stat-value')).toHaveText("175");
  await expect(page.locator("#results-summary")).toContainText("175 filtered episodes");
});
