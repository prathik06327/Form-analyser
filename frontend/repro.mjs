import { chromium } from "playwright";
const outDir = process.argv[2];
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1500, height: 1000 } });
const errs = [];
const netLog = [];
page.on("console", m => { if (m.type() === "error") errs.push(m.text()); });
page.on("pageerror", e => errs.push(String(e)));
page.on("requestfinished", async req => {
  if (req.url().includes("/analyze/")) {
    const res = await req.response();
    netLog.push(`${req.method()} ${req.url()} -> ${res?.status()}`);
  }
});
page.on("requestfailed", req => {
  if (req.url().includes("/analyze/") || req.url().includes("/health")) {
    netLog.push(`FAILED ${req.method()} ${req.url()} -> ${req.failure()?.errorText}`);
  }
});

await page.goto("http://localhost:3000", { waitUntil: "networkidle" });
await page.waitForSelector("text=FormSense AI");
await page.waitForTimeout(1000); // let health check land
await page.screenshot({ path: `${outDir}/r1-loaded.png`, clip: {x:0,y:0,width:1500,height:120} });

await page.getByRole("tab", { name: /upload video/i }).click();
await page.waitForTimeout(300);
await page.locator('input[type="file"]').setInputFiles(`${outDir}/synthetic.mp4`);
await page.waitForTimeout(400);
await page.getByRole("button", { name: /analyze video/i }).click();

await page.waitForSelector("text=Analysis Complete", { timeout: 60000 }).catch(e => {
  netLog.push("TIMED OUT waiting for Analysis Complete: " + e.message);
});
await page.waitForTimeout(800);
await page.screenshot({ path: `${outDir}/r2-result.png`, fullPage: true });

console.log("NETWORK:", JSON.stringify(netLog, null, 2));
console.log("CONSOLE_ERRORS:", JSON.stringify(errs, null, 2));
await browser.close();
