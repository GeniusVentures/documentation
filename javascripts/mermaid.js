document.addEventListener("DOMContentLoaded", () => {
  if (typeof mermaid === "undefined") return;

  const config = { startOnLoad: true };
  mermaid.initialize(config);

  if (window.document$) {
    document$.subscribe(() => {
      mermaid.initialize(config);
      mermaid.init(undefined, document.querySelectorAll(".mermaid"));
    });
  }
});
