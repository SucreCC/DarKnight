import sharp from "sharp";
import pngToIco from "png-to-ico";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { writeFile } from "node:fs/promises";

const __dirname = dirname(fileURLToPath(import.meta.url));
const src = resolve(__dirname, "../public/statics/logo.png");
const outDir = resolve(__dirname, "../public/statics/favicon");

const pngTargets = [
  ["favicon-16x16.png", 16],
  ["favicon-32x32.png", 32],
  ["apple-touch-icon.png", 180],
  ["android-chrome-192x192.png", 192],
  ["android-chrome-512x512.png", 512],
  ["mstile-150x150.png", 150],
];

for (const [name, size] of pngTargets) {
  await sharp(src)
    .resize(size, size, { fit: "contain", background: { r: 0, g: 0, b: 0, alpha: 0 } })
    .png()
    .toFile(resolve(outDir, name));
  console.log("generated", name, size);
}

const icoBuffers = await Promise.all(
  [16, 32, 48].map((size) =>
    sharp(src)
      .resize(size, size, { fit: "contain", background: { r: 0, g: 0, b: 0, alpha: 0 } })
      .png()
      .toBuffer(),
  ),
);
const ico = await pngToIco(icoBuffers);
await writeFile(resolve(outDir, "favicon.ico"), ico);
console.log("generated favicon.ico");
