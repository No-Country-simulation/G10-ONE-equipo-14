const { test } = require("@playwright/test");

const runId = "36c28c96-0997-438c-bcb8-ef4babcfe677";
const evidenceDir = "docs/sets_pruebas/evidencia_compatibilidad";

test.use({
  channel: "msedge",
  colorScheme: "light",
  locale: "es-PY",
  viewport: { width: 1440, height: 1000 },
});

test("capture test-set evidence with the current dashboard", async ({ page }) => {
  test.setTimeout(120000);

  await page.goto("http://localhost:8501", { waitUntil: "networkidle" });
  await page.getByText("Servicios disponibles", { exact: true }).waitFor();
  await page.screenshot({ path: `${evidenceDir}/01-sistema-disponible.png` });

  const runInput = page.getByLabel("Run ID", { exact: true });
  await runInput.fill(runId);
  await runInput.press("Enter");
  await page.getByRole("button", { name: "Buscar ejecución" }).click();
  await page
    .getByText("Ejecución recuperada correctamente.", { exact: true })
    .waitFor();

  await page.setViewportSize({ width: 1440, height: 1200 });
  await page.getByText("25", { exact: true }).first().waitFor();
  await page.waitForTimeout(500);
  await page
    .getByText("3. Resultado persistido", { exact: true })
    .evaluate((element) => element.scrollIntoView({ block: "start" }));
  await page.screenshot({ path: `${evidenceDir}/02-resumen-ejecucion.png` });

  await page.getByRole("tab", { name: "Análisis" }).click();
  await page
    .getByText("1. positive · confianza 1.00", { exact: true })
    .first()
    .waitFor();
  await page.getByRole("tab", { name: "Análisis" }).scrollIntoViewIfNeeded();
  await page.screenshot({ path: `${evidenceDir}/03-analisis-gemini.png` });

  await page.getByRole("tab", { name: "Oportunidades" }).click();
  await page.waitForTimeout(1000);
  await page.getByRole("tab", { name: "Oportunidades" }).scrollIntoViewIfNeeded();
  await page.screenshot({ path: `${evidenceDir}/04-oportunidades.png` });

  await page.getByRole("tab", { name: "Alertas internas" }).click();
  await page.waitForTimeout(1000);
  await page.getByRole("tab", { name: "Alertas internas" }).scrollIntoViewIfNeeded();
  await page.screenshot({ path: `${evidenceDir}/05-alertas-internas.png` });

  await page.getByRole("tab", { name: "LinkedIn y FAQ" }).click();
  await page.getByRole("textbox", { name: "Título" }).first().waitFor();
  await page.setViewportSize({ width: 1440, height: 1400 });
  await page.getByRole("tab", { name: "LinkedIn y FAQ" }).scrollIntoViewIfNeeded();
  await page.screenshot({ path: `${evidenceDir}/06-activos-generados.png` });
});
