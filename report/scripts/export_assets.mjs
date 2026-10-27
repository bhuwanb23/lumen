/**
 * Export report SVGs → PNG and HTML reports → PDF via Playwright.
 * Run: cd report && node scripts/export_assets.mjs
 */
import { createServer } from "node:http";
import { readFileSync, existsSync, mkdirSync, writeFileSync } from "node:fs";
import { dirname, join, basename, extname } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPORT = join(__dirname, "..");
const DIAGRAMS = join(REPORT, "diagrams");

const SVG_FILES = [
  "patient_journey.svg",
  "scope_boundary.svg",
  "evidence_gate.svg",
  "principles_infographic.svg",
  "information_flow.svg",
  "trust_snapshot.svg",
  "appointment_value.svg",
  "validation_snapshot.svg",
];

const HTML_REPORTS = [
  { html: "Lumen_Executive_Brief.html", pdf: "Lumen_Executive_Brief.pdf" },
  { html: "Lumen_Product_Overview.html", pdf: "Lumen_Product_Overview.pdf" },
  { html: "Lumen_One_Pager.html", pdf: "Lumen_One_Pager.pdf" },
];

function contentType(filePath) {
  switch (extname(filePath).toLowerCase()) {
    case ".html":
      return "text/html; charset=utf-8";
    case ".svg":
      return "image/svg+xml";
    case ".png":
      return "image/png";
    default:
      return "application/octet-stream";
  }
}

function startStaticServer(root) {
  return new Promise((resolve) => {
    const server = createServer((req, res) => {
      const urlPath = decodeURIComponent((req.url || "/").split("?")[0]);
      const safe = urlPath.replace(/\.\./g, "");
      const filePath = join(root, safe === "/" ? "index.html" : safe.slice(1));
      if (!existsSync(filePath)) {
        res.writeHead(404);
        res.end("Not found");
        return;
      }
      res.writeHead(200, { "Content-Type": contentType(filePath) });
      res.end(readFileSync(filePath));
    });
    server.listen(0, "127.0.0.1", () => {
      const { port } = server.address();
      resolve({ server, port });
    });
  });
}

async function exportSvgToPng(page, svgName) {
  const svgPath = join(DIAGRAMS, svgName);
  const pngPath = join(DIAGRAMS, svgName.replace(/\.svg$/i, ".png"));
  let svg = readFileSync(svgPath, "utf8");
  // Strip XML declaration so inline HTML parse is clean
  svg = svg.replace(/<\?xml[^>]*>\s*/i, "");
  const widthMatch = svg.match(/\bwidth="(\d+)"/);
  const heightMatch = svg.match(/\bheight="(\d+)"/);
  const width = Number(widthMatch?.[1] || 1400);
  const height = Number(heightMatch?.[1] || 800);
  const scale = 2;

  await page.setViewportSize({ width: Math.ceil(width * scale), height: Math.ceil(height * scale) });
  await page.setContent(
    `<!DOCTYPE html><html><head><meta charset="utf-8"><style>
      html, body { margin: 0; padding: 0; background: #ffffff; }
      #frame { width: ${width}px; height: ${height}px; transform: scale(${scale}); transform-origin: top left; }
      #frame svg { display: block; width: ${width}px; height: ${height}px; }
    </style></head><body><div id="frame">${svg}</div></body></html>`,
    { waitUntil: "load" },
  );
  await page.waitForSelector("#frame svg");
  await page.waitForTimeout(100);
  await page.locator("#frame").screenshot({
    path: pngPath,
    type: "png",
    omitBackground: false,
  });
  console.log(`PNG  ${basename(pngPath)} (${width * scale}×${height * scale})`);
}

async function exportPdf(page, baseUrl, htmlName, pdfName) {
  const url = `${baseUrl}/${htmlName}`;
  await page.goto(url, { waitUntil: "networkidle" });
  // Ensure embedded PNGs finished
  await page.evaluate(async () => {
    const images = Array.from(document.images);
    await Promise.all(
      images.map((img) =>
        img.complete
          ? Promise.resolve()
          : new Promise((resolve) => {
              img.onload = resolve;
              img.onerror = resolve;
            }),
      ),
    );
  });
  await page.waitForTimeout(400);
  const pdfPath = join(REPORT, pdfName);
  await page.pdf({
    path: pdfPath,
    format: "A4",
    printBackground: true,
    margin: { top: "10mm", right: "10mm", bottom: "10mm", left: "10mm" },
  });
  console.log(`PDF  ${pdfName}`);
}

async function main() {
  mkdirSync(DIAGRAMS, { recursive: true });
  const { server, port } = await startStaticServer(REPORT);
  const baseUrl = `http://127.0.0.1:${port}`;
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  try {
    for (const svg of SVG_FILES) {
      if (!existsSync(join(DIAGRAMS, svg))) {
        console.warn(`skip missing ${svg}`);
        continue;
      }
      await exportSvgToPng(page, svg);
    }
    for (const item of HTML_REPORTS) {
      await exportPdf(page, baseUrl, item.html, item.pdf);
    }
    writeFileSync(
      join(REPORT, ".export_stamp.json"),
      JSON.stringify(
        {
          exported_at: new Date().toISOString(),
          svgs: SVG_FILES,
          pdfs: HTML_REPORTS.map((x) => x.pdf),
        },
        null,
        2,
      ),
    );
    console.log("Done.");
  } finally {
    await browser.close();
    server.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
