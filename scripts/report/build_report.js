"use strict";

/** Build the analysis DOCX from current processed data and analysis outputs. */
const fs = require("fs");
const path = require("path");
const {
  AlignmentType, BorderStyle, Document, Footer, Header, HeadingLevel, ImageRun,
  Packer, PageBreak, PageNumber, Paragraph, ShadingType, Table, TableCell,
  TableOfContents, TableRow, TextRun, WidthType,
} = require("docx");

const ROOT = path.resolve(__dirname, "..", "..");
const DATA = path.join(ROOT, "data", "processed");
const FIGURES = path.join(ROOT, "reports", "figures");
const OUTPUT = path.join(ROOT, "reports", "final_report.docx");
const REQUIRED = [
  "pitcher_stats.csv", "team_financials.csv", "pitcher_regression_results.csv",
  "did_regression_results.csv",
];

function parseCsv(file) {
  const text = fs.readFileSync(file, "utf8").replace(/^\uFEFF/, "");
  const rows = [];
  let row = [], field = "", quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    if (char === '"') {
      if (quoted && text[i + 1] === '"') { field += '"'; i += 1; }
      else quoted = !quoted;
    } else if (char === "," && !quoted) { row.push(field); field = ""; }
    else if ((char === "\n" || char === "\r") && !quoted) {
      if (char === "\r" && text[i + 1] === "\n") i += 1;
      row.push(field); field = "";
      if (row.some(value => value !== "")) rows.push(row);
      row = [];
    } else field += char;
  }
  if (field || row.length) { row.push(field); rows.push(row); }
  const headers = rows.shift();
  return rows.map(values => Object.fromEntries(headers.map((header, i) => [header, values[i]])));
}

function mean(rows, column) {
  const values = rows.map(row => Number(row[column])).filter(Number.isFinite);
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}
function pValue(value) { return Number(value) < 0.001 ? "<0.001" : Number(value).toFixed(3); }
function usd(value) {
  const abs = Math.abs(value), sign = value >= 0 ? "+" : "-";
  if (abs >= 1e9) return `${sign}$${(abs / 1e9).toFixed(2)}B`;
  return `${sign}$${(abs / 1e6).toFixed(1)}M`;
}
function effect(outcome, value) {
  return outcome === "OI_Margin_Pct" ? `${(Number(value) * 100).toFixed(2)} pp` : usd(Number(value));
}

const border = { style: BorderStyle.SINGLE, size: 1, color: "D0D7DE" };
const borders = { top: border, bottom: border, left: border, right: border };
function h1(text) { return new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(text)] }); }
function h2(text) { return new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(text)] }); }
function paragraph(text, options = {}) {
  return new Paragraph({ spacing: { after: 150 }, children: [new TextRun({ text, ...options })] });
}
function bullet(text) {
  return new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun(text)] });
}
function dataTable(headers, rows, widths) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA }, columnWidths: widths,
    rows: [
      new TableRow({ children: headers.map((text, index) => new TableCell({
        borders, width: { size: widths[index], type: WidthType.DXA },
        shading: { fill: "1F4E79", type: ShadingType.CLEAR },
        children: [new Paragraph({ children: [new TextRun({ text, bold: true, color: "FFFFFF", size: 18 })] })],
      })) }),
      ...rows.map(row => new TableRow({ children: row.map((text, index) => new TableCell({
        borders, width: { size: widths[index], type: WidthType.DXA },
        children: [new Paragraph({ children: [new TextRun({ text: String(text), size: 18 })] })],
      })) })),
    ],
  });
}
function reportImage(filename, width, height) {
  const file = path.join(FIGURES, filename);
  if (!fs.existsSync(file)) return paragraph(`Figure unavailable: ${filename}`, { italics: true, color: "777777" });
  return new Paragraph({ alignment: AlignmentType.CENTER, children: [new ImageRun({
    type: "png", data: fs.readFileSync(file), transformation: { width, height },
    altText: { title: filename, description: filename, name: filename },
  })] });
}

async function main() {
  const missing = REQUIRED.filter(filename => !fs.existsSync(path.join(DATA, filename)));
  if (missing.length) throw new Error(`Missing analysis outputs: ${missing.join(", ")}. Run the analysis scripts first.`);

  const pitchers = parseCsv(path.join(DATA, "pitcher_stats.csv"));
  const team = parseCsv(path.join(DATA, "team_financials.csv"));
  const regressions = parseCsv(path.join(DATA, "pitcher_regression_results.csv"));
  const did = parseCsv(path.join(DATA, "did_regression_results.csv"));
  const sample = pitchers.filter(row => Number(row.low_sample_flag) === 0);
  const buckets = [
    ["<92 mph", row => Number(row.fastball_velo_mph) < 92],
    ["92-94 mph", row => Number(row.fastball_velo_mph) >= 92 && Number(row.fastball_velo_mph) < 94],
    ["94-96 mph", row => Number(row.fastball_velo_mph) >= 94 && Number(row.fastball_velo_mph) < 96],
    ["96+ mph", row => Number(row.fastball_velo_mph) >= 96],
  ].map(([label, predicate]) => {
    const rows = sample.filter(predicate);
    return [label, rows.length, mean(rows, "IL_days").toFixed(1), mean(rows, "WAR_per_IP").toFixed(4)];
  });
  const before = team.filter(row => Number(row.Superstar_Era) === 0);
  const after = team.filter(row => Number(row.Superstar_Era) === 1);
  const mainReg = regressions.filter(row => row.specification === "main");
  const fullDid = did.filter(row => row.sample === "full_2017_2026");
  const covidExcluded = Object.fromEntries(
    did.filter(row => row.sample === "excl_2020_2021").map(row => [row.outcome, row])
  );

  const children = [
    new Paragraph({ spacing: { before: 1400, after: 250 }, alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: "Velocity, Injury Risk, and Franchise Value", bold: true, size: 40, color: "1F4E79" })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({
      text: "An exploratory LA Dodgers pitching and financial analysis", italics: true, size: 25,
    })] }),
    new Paragraph({ spacing: { before: 1000 }, alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: "Analysis edition — generated from processed data", size: 19, color: "555555" })] }),
    new Paragraph({ children: [new PageBreak()] }),
    new TableOfContents("Contents", { hyperlink: true, headingStyleRange: "1-2" }),
    new Paragraph({ children: [new PageBreak()] }),

    h1("1. Executive summary"),
    paragraph(`This project combines ${sample.length} pitcher-season observations (${new Set(sample.map(row => row.player_id)).size} unique pitchers) with team financial data and a six-team comparison panel.`),
    ...mainReg.map(row => bullet(
      `A 1 mph velocity increase is associated with ${Number(row.velocity_coef).toFixed(row.outcome === "IL_days" ? 2 : 4)} in ${row.outcome} (p=${pValue(row.velocity_p_value)}).`
    )),
    bullet("Results are observational associations. They do not establish that velocity or the superstar strategy caused the outcomes."),

    h1("2. Data and design"),
    paragraph("Pitcher-level models use player-clustered standard errors and exclude rows flagged for fewer than five innings. A sensitivity model controls for the prior observed season's IL days."),
    paragraph("The financial analysis compares LAD with NYY, BOS, NYM, CHC, and SFG using team and season fixed effects. Post equals one from 2024 onward."),
    paragraph("Important caveats: only six team clusters are available, pre-trends are imperfect, external financial values are estimates, and 2026 values are preliminary."),

    h1("3. Velocity trade-off"),
    dataTable(["Velocity bucket", "Pitcher-seasons", "Mean IL days", "Mean WAR/IP"], buckets,
      [2300, 2100, 2100, 2860]),
    paragraph("Bucket counts and means above are computed from the processed pitcher dataset when this report is built.", { italics: true, color: "555555" }),
    reportImage("chart1_velo_il.png", 480, 309),
    reportImage("chart2_bucket.png", 480, 309),

    h1("4. Team financial comparison"),
    dataTable(["Metric", "Before 2024 mean", "2024+ mean", "Change"], [
      ["Revenue", usd(mean(before, "Revenue")).replace("+", ""), usd(mean(after, "Revenue")).replace("+", ""), usd(mean(after, "Revenue") - mean(before, "Revenue"))],
      ["Operating income", usd(mean(before, "Operating_Income")).replace("+", ""), usd(mean(after, "Operating_Income")).replace("+", ""), usd(mean(after, "Operating_Income") - mean(before, "Operating_Income"))],
      ["Team value", usd(mean(before, "Team_Value")).replace("+", ""), usd(mean(after, "Team_Value")).replace("+", ""), usd(mean(after, "Team_Value") - mean(before, "Team_Value"))],
      ["CBT tax", usd(mean(before, "CBT_Tax_Paid")).replace("+", ""), usd(mean(after, "CBT_Tax_Paid")).replace("+", ""), usd(mean(after, "CBT_Tax_Paid") - mean(before, "CBT_Tax_Paid"))],
    ], [2300, 2300, 2300, 2460]),
    reportImage("chart3_cbt.png", 480, 309),

    h2("4.1 Difference-in-Differences"),
    dataTable(["Outcome", "Full-sample effect", "p-value", "Excl. 2020-21"], fullDid.map(row => [
      row.outcome, effect(row.outcome, row.did_coef), pValue(row.p_value),
      `${effect(row.outcome, covidExcluded[row.outcome].did_coef)} (p=${pValue(covidExcluded[row.outcome].p_value)})`,
    ]), [2500, 2300, 1700, 2860]),
    paragraph("OI_Margin_Pct is stored as a proportion. Its coefficients are multiplied by 100 and reported above in percentage points (pp).", { bold: true, color: "1F4E79" }),
    reportImage("chart5_did_trend.png", 480, 192),
    reportImage("chart6_event_study.png", 440, 248),

    h1("5. Interpretation and limitations"),
    bullet("Higher velocity is associated with both greater injury burden and higher WAR efficiency."),
    bullet("Revenue and team-value estimates rise relative to the selected peer group, while operating-income effects are not statistically distinguishable from zero."),
    bullet("The DiD estimates are exploratory: six clusters limit conventional cluster-robust inference, and the parallel-trends assumption is not fully supported."),
    bullet("The published IL snapshot can understate unresolved or unmatched stints; the live collection utility now right-censors open stints for future refreshes."),
    paragraph("The repository includes the processed datasets, scripts, workbook, figures, and documentation needed to inspect and rerun the analysis."),
  ];

  const document = new Document({
    numbering: { config: [{ reference: "bullets", levels: [{ level: 0, format: "bullet", text: "•", alignment: AlignmentType.LEFT }] }] },
    sections: [{
      properties: { page: { margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 } } },
      headers: { default: new Header({ children: [paragraph("Dodgers Pitching Analytics", { size: 16, color: "777777" })] }) },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
        children: [new TextRun({ children: [PageNumber.CURRENT], size: 17 })] })] }) },
      children,
    }],
  });
  fs.mkdirSync(path.dirname(OUTPUT), { recursive: true });
  fs.writeFileSync(OUTPUT, await Packer.toBuffer(document));
  console.log(`Saved ${path.relative(ROOT, OUTPUT)}`);
}

main().catch(error => { console.error(error); process.exitCode = 1; });
