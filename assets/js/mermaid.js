function css(name) {
  return "rgb(" + getComputedStyle(document.documentElement).getPropertyValue(name) + ")";
}

function initMermaidLight() {
  mermaid.initialize({
    theme: "base",
    themeVariables: {
      background: "#f5f5f2",
      primaryColor: "#f5f5f2",
      secondaryColor: "#e9eae7",
      tertiaryColor: "#f5f5f2",
      primaryBorderColor: "#686e74",
      secondaryBorderColor: "#686e74",
      tertiaryBorderColor: "#686e74",
      lineColor: "#686e74",
      primaryTextColor: "#0d0e0e",
      secondaryTextColor: "#0d0e0e",
      tertiaryTextColor: "#0d0e0e",
      fontFamily:
        "ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,segoe ui,Roboto,helvetica neue,Arial,noto sans,sans-serif",
      fontSize: "16px",
    },
  });
}

function initMermaidDark() {
  mermaid.initialize({
    theme: "base",
    themeVariables: {
      background: "#0d0e0e",
      primaryColor: "#0d0e0e",
      secondaryColor: "#171918",
      tertiaryColor: "#0d0e0e",
      primaryBorderColor: "#c9cdd2",
      secondaryBorderColor: "#c9cdd2",
      tertiaryBorderColor: "#c9cdd2",
      lineColor: "#c9cdd2",
      primaryTextColor: "#c9cdd2",
      secondaryTextColor: "#c9cdd2",
      tertiaryTextColor: "#c9cdd2",
      fontFamily:
        "ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,segoe ui,Roboto,helvetica neue,Arial,noto sans,sans-serif",
      fontSize: "16px",
    },
  });
}
