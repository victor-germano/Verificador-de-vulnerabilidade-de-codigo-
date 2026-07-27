// SVG fill/stroke attributes don't reliably resolve CSS custom properties
// across browsers, so chart colors are fixed hex values (chosen to read
// clearly on both the light and dark card backgrounds) rather than reusing
// the `--severity-*` custom properties used elsewhere.
export const SEVERITY_COLORS = {
  critical: "#dc2626",
  high: "#ea580c",
  medium: "#d97706",
  low: "#2563eb",
  info: "#64748b",
} as const;

export const CHART_GRID_COLOR = "currentColor";
