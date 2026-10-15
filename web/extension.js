// web/scripts/extension.ts
import { app } from "../../scripts/app.js";
app.registerExtension({
  name: "fal",
  setup: () => {
    const stylesheet = document.createElement("link");
    stylesheet.rel = "stylesheet";
    stylesheet.href = new URL("./extension.css", import.meta.url).href;
    const stylesheets = /* @__PURE__ */ new Set();
    for (const link of document.querySelectorAll("link[rel=stylesheet]")) {
      stylesheets.add(link.getAttribute("href"));
    }
    if (!stylesheets.has(stylesheet.href)) document.head.append(stylesheet);
  }
});
