import { View, Text, StyleSheet } from "react-native";
import { colors } from "../theme";

export default function SensorOverview({ telemetry }) {
  if (!telemetry) {
    return (
      <View style={styles.card}>
        <Text style={styles.title}>Live sensor readings</Text>
        <Text style={styles.muted}>Waiting for telemetry from the station...</Text>
      </View>
    );
  }

  const stats = [
    { label: "Temperature", value: `${telemetry.temperature_c ?? "--"} °C`, warn: telemetry.temperature_c > 45 },
    { label: "Humidity", value: `${telemetry.humidity_pct ?? "--"} %` },
    { label: "Gas level", value: `${telemetry.gas_level ?? "--"}`, warn: telemetry.gas_level > 700 },
    { label: "Flame", value: telemetry.flame_detected ? "DETECTED" : "Clear", warn: telemetry.flame_detected },
    { label: "Motion", value: telemetry.motion_detected ? "Detected" : "None" },
  ];

  return (
    <View style={styles.card}>
      <Text style={styles.title}>Live sensor readings</Text>
      <Text style={styles.muted}>
        {telemetry.device_id} · {telemetry.room}
      </Text>
      <View style={styles.grid}>
        {stats.map((s) => (
          <View key={s.label} style={[styles.stat, s.warn && styles.statWarn]}>
            <Text style={styles.statLabel}>{s.label.toUpperCase()}</Text>
            <Text style={styles.statValue}>{s.value}</Text>
          </View>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.card,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    padding: 16,
    marginBottom: 16,
  },
  title: { color: colors.text, fontSize: 17, fontWeight: "600", marginBottom: 4 },
  muted: { color: colors.muted, fontSize: 13 },
  grid: { flexDirection: "row", flexWrap: "wrap", marginTop: 12, gap: 8 },
  stat: {
    backgroundColor: colors.bg,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    padding: 10,
    width: "31%",
  },
  statWarn: { borderColor: colors.red },
  statLabel: { color: colors.muted, fontSize: 10, textTransform: "uppercase" },
  statValue: { color: colors.text, fontSize: 15, fontWeight: "600", marginTop: 2 },
});