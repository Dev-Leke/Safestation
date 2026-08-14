export const colors = {
  bg: "#0f1420",
  card: "#161d2e",
  border: "#262f45",
  text: "#e6e9f0",
  muted: "#8a93a8",
  accent: "#3b82f6",
  green: "#22c55e",
  red: "#ef4444",
  orange: "#f97316",
  yellow: "#eab308",
};

export function severityColor(severity) {
  switch (severity) {
    case "critical":
      return colors.red;
    case "high":
      return colors.orange;
    case "medium":
      return colors.yellow;
    case "low":
      return colors.green;
    default:
      return colors.muted;
  }
}