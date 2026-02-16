document.addEventListener("DOMContentLoaded", () => {
  const anchors = document.querySelectorAll("a[href^='http://'], a[href^='https://']");
  anchors.forEach((a) => {
    a.setAttribute("target", "_blank");
    a.setAttribute("rel", "noopener");
  });
});
