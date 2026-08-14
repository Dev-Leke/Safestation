import { useCallback, useEffect, useState } from "react";
import { View, Text, FlatList, StyleSheet, SafeAreaView } from "react-native";
import { api } from "../api";
import { colors } from "../theme";
import SensorOverview from "../components/SensorOverview";
import IncidentRow from "../components/IncidentRow";

const POLL_MS = 4000;
const SEVERITY_ORDER = { critical: 0, high: 1, medium: 2, low: 3 };

export default function DashboardScreen({ navigation }) {
  const [telemetry, setTelemetry] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [apiOnline, setApiOnline] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const [t, inc] = await Promise.all([api.latestTelemetry(), api.incidents()]);
      setTelemetry(t);
      setIncidents(inc);
      setApiOnline(true);
    } catch (e) {
      setApiOnline(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, POLL_MS);
    return () => clearInterval(id);
  }, [refresh]);

  const sorted = [...incidents].sort((a, b) => {
    const diff = (SEVERITY_ORDER[a.severity] ?? 9) - (SEVERITY_ORDER[b.severity] ?? 9);
    if (diff !== 0) return diff;
    return new Date(b.timestamp) - new Date(a.timestamp);
  });

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        <View style={styles.header}>
          <View>
            <Text style={styles.h1}>SafeStation AI</Text>
            <Text style={styles.muted}>Cloud-native emergency detection & response</Text>
          </View>
          <View style={[styles.badge, { backgroundColor: apiOnline ? colors.green + "30" : colors.red + "30" }]}>
            <Text style={{ color: apiOnline ? colors.green : colors.red, fontSize: 12, fontWeight: "600" }}>
              {apiOnline ? "API connected" : "API unreachable"}
            </Text>
          </View>
        </View>

        <FlatList
          data={sorted}
          keyExtractor={(item) => String(item.id)}
          ListHeaderComponent={
            <>
              <SensorOverview telemetry={telemetry} />
              <Text style={styles.sectionTitle}>Incidents</Text>
              {sorted.length === 0 && <Text style={styles.muted}>No incidents reported yet.</Text>}
            </>
          }
          renderItem={({ item }) => (
            <IncidentRow incident={item} onPress={() => navigation.navigate("IncidentDetail", { incidentId: item.id })} />
          )}
          contentContainerStyle={{ paddingBottom: 24 }}
        />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: colors.bg },
  container: { flex: 1, padding: 16 },
  header: { flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 },
  h1: { color: colors.text, fontSize: 24, fontWeight: "700" },
  muted: { color: colors.muted, fontSize: 13 },
  badge: { borderRadius: 999, paddingHorizontal: 10, paddingVertical: 4 },
  sectionTitle: { color: colors.text, fontSize: 16, fontWeight: "600", marginTop: 8, marginBottom: 8 },
});