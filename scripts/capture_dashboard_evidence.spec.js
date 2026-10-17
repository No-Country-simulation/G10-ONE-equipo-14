const { test } = require("@playwright/test");

const runId = "62f117b9-8994-406a-91bf-34d228cb0d2a";
const visualDir = "docs/evidence/INV-021-visual-evidence";
const uxDir = "docs/evidence/COMLAB-115-dashboard-ux";

test.use({
  channel: "msedge",
  colorScheme: "light",
  locale: "es-PY",
  viewport: { width: 1440, height: 1000 },
});

test("capture current dashboard evidence", async ({ page, context }) => {
  test.setTimeout(180000);
  await page.goto("http://localhost:8501", { waitUntil: "networkidle" });
  await page.getByText("¿Para qué sirven los datos de la carga?", { exact: true }).waitFor();

  await page.screenshot({ path: `${visualDir}/01-E1-dashboard-health.png` });
  await page.screenshot({ path: `${uxDir}/01-dashboard-home.png` });
  const contextualHelp = page
    .getByRole("group")
    .filter({ hasText: "¿Para qué sirven los datos de la carga?" });
  await contextualHelp.screenshot({ path: `${uxDir}/02-contextual-help.png` });

  await page.getByLabel("Run ID", { exact: true }).fill(runId);
  await page.getByLabel("Run ID", { exact: true }).press("Enter");
  await page.getByRole("button", { name: "Buscar ejecución" }).click();
  await page.getByText("Ejecución recuperada correctamente.", { exact: true }).waitFor();
  await page.getByText("3. Resultado persistido", { exact: true }).scrollIntoViewIfNeeded();
  await page.screenshot({ path: `${uxDir}/03-run-result.png` });

  await page.getByRole("tab", { name: "Análisis" }).click();
  const firstAnalysis = page.getByText(/1\. positive · confianza 1\.00/).first();
  await firstAnalysis.scrollIntoViewIfNeeded();
  await firstAnalysis.click();
  await page.getByText("Evidencia y fuentes", { exact: true }).first().waitFor();
  const analysisCard = page
    .locator('[data-testid="stExpander"]')
    .filter({ hasText: "1. positive · confianza 1.00" });
  await analysisCard.screenshot({ path: `${visualDir}/03-E3-run-analysis.png` });
  await analysisCard.screenshot({ path: `${uxDir}/04-analysis-evidence.png` });

  await page.getByRole("tab", { name: "Oportunidades" }).click();
  await page
    .getByRole("tab", { name: "Oportunidades" })
    .waitFor({ state: "visible" });
  await page.waitForTimeout(1000);
  await page.getByRole("tab", { name: "Oportunidades" }).scrollIntoViewIfNeeded();
  await page.screenshot({ path: `${visualDir}/04-E4-generated-opportunities.png` });
  await page.screenshot({ path: `${uxDir}/05-opportunities.png` });

  await page.getByRole("tab", { name: "LinkedIn y FAQ" }).click();
  await page.getByRole("textbox", { name: "Título" }).waitFor();
  await page.setViewportSize({ width: 1440, height: 1400 });
  await page.getByRole("tab", { name: "LinkedIn y FAQ" }).scrollIntoViewIfNeeded();
  await page.screenshot({ path: `${visualDir}/05-E5-curation-queue.png` });
  await page.screenshot({ path: `${uxDir}/06-curation-queue.png` });

  const production = await context.newPage();
  await production.goto("https://communitylab-dashboard.onrender.com", {
    waitUntil: "networkidle",
  });
  await production
    .getByText("¿Para qué sirven los datos de la carga?", { exact: true })
    .waitFor({ timeout: 60000 });
  await production.screenshot({
    path: "docs/evidence/E8-render-deployment/01-dashboard-publico.png",
  });
  await production.screenshot({ path: `${uxDir}/07-public-deployment.png` });
});
