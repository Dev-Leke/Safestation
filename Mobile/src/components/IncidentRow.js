import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { colors, severityColor } from "../theme";

export default function IncidentRow({ incident, onPress }) {
  const sevColor = severityColor(incident.severity);
  return (
    <TouchableOpacity style={[styles.row, { borderLeftColor: sevColor }]} onPress={onPress}>
      <View style={styles.top}>
        <View style={[styles.pill, { backgroundColor: sevColor + "30" }]}>
          <Text style={[styles.pillText, { color: sevColor }]}>{incident.severity.toUpperCase()}</Text>
        </View>
        <Text style={styles.category}>{incident.category}</Text>
        <Text style={styles.reviewStatus}>{incident.review_status}</Text>
      </View>
      <View style={styles.bottom}>
        <Text style={styles.muted}>{incident.room}</Text>
        <Text style={styles.muted}>{new Date(incident.timestamp + "Z").toLocaleTimeString()}</Text>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  row: {
    backgroundColor: colors.card,
    borderRadius: 8,
    borderLeftWidth: 4,
    padding: 10,
    marginBottom: 8,
  },
  top: { flexDirection: "row", alignItems: "center", marginBottom: 4 },
  pill: { borderRadius: 999, paddingHorizontal: 8, paddingVertical: 2, marginRight: 8 },
  pillText: { fontSize: 11, fontWeight: "700" },
  category: { color: colors.text, fontSize: 14, textTransform: "capitalize" },
  reviewStatus: { color: colors.muted, fontSize: 12, marginLeft: "auto", textTransform: "capitalize" },
  bottom: { flexDirection: "row", justifyContent: "space-between" },
  muted: { color: colors.muted, fontSize: 12 },
});