import { useCallback, useEffect, useState } from "react";
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, SafeAreaView, ActivityIndicator } from "react-native";
import { api } from "../api";
import { colors, severityColor } from "../theme";

export default function IncidentDetailScreen({ route, navigation }) {
  const { incidentId } = route.params;
  const [incident, setIncident] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    try {
      const data = await api.incident(incidentId);
      setIncident(data);
    } catch (e) {
      setError(e.message);
    }
  }, [incidentId]);

  useEffect(() => {
    load();
  }, [load]);

  const act = async (fn) => {
    setBusy(true);
    setError(null);
    try {
      await fn();
      await load();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  if (!incident) {
    return (
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.centered}>
          <ActivityIndicator color={colors.accent} />
          <Text style={styles.muted}>Loading incident...</Text>
        </View>
      </SafeAreaView>
    );
  }

  const sevColor = severityColor(incident.severity);

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.backLink}>‹ Back</Text>
        </TouchableOpacity>

        <View style={styles.headerRow}>
          <Text style={styles.h1}>Incident {incident.event_id.slice(0, 8)}</Text>
          <View style={[styles.pill, { backgroundColor: sevColor + "30" }]}>
            <Text style={{ color: sevColor, fontWeight: "700", fontSize: 12 }}>{incident.severity.toUpperCase()}</Text>
          </View>
        </View>

        <Text style={styles.muted}>
          {incident.room} · {incident.device_id} · {new Date(incident.timestamp + "Z").toLocaleString()}
        </Text>

        <Text style={styles.summary}>{incident.alert_summary}</Text>

        <View style={styles.grid}>
          <DetailStat label="Category" value={incident.category} />
          <DetailStat label="Confidence" value={`${Math.round(incident.confidence * 100)}%`} />
          <DetailStat label="Review status" value={incident.review_status} />
          <DetailStat label="Notification" value={incident.notification_status} />
        </View>

        <Text style={styles.sectionTitle}>Evidence</Text>
        {incident.evidence.length === 0 ? (
          <Text style={styles.muted}>No supporting evidence recorded.</Text>
        ) : (
          incident.evidence.map((e, i) => (
            <Text key={i} style={styles.bullet}>
              • {e}
            </Text>
          ))
        )}

        <Text style={styles.sectionTitle}>Recommended action</Text>
        <Text style={styles.body}>{incident.recommended_action || "—"}</Text>

        {incident.snapshot_ref && <Text style={styles.muted}>Camera snapshot: {incident.snapshot_ref}</Text>}

        <View style={styles.actions}>
          {incident.review_status === "pending" && (
            <>
              <TouchableOpacity
                disabled={busy}
                style={[styles.btn, { backgroundColor: colors.green }]}
                onPress={() => act(() => api.reviewIncident(incident.id, "approved", "abimbola"))}
              >
                <Text style={styles.btnText}>Approve</Text>
              </TouchableOpacity>
              <TouchableOpacity
                disabled={busy}
                style={[styles.btn, { backgroundColor: colors.red }]}
                onPress={() => act(() => api.reviewIncident(incident.id, "rejected", "abimbola"))}
              >
                <Text style={styles.btnText}>Reject</Text>
              </TouchableOpacity>
            </>
          )}
          {incident.review_status === "approved" && incident.notification_status !== "sent" && (
            <TouchableOpacity
              disabled={busy}
              style={[styles.btn, { backgroundColor: colors.accent }]}
              onPress={() => act(() => api.notifyIncident(incident.id))}
            >
              <Text style={styles.btnText}>Send notification</Text>
            </TouchableOpacity>
          )}
        </View>

        {error && <Text style={styles.error}>{error}</Text>}

        {incident.notification_payload && (
          <View style={styles.notifyBox}>
            <Text style={styles.sectionTitle}>Sent notification</Text>
            <Text style={styles.body}>SMS: {incident.notification_payload.sms_text}</Text>
            <Text style={styles.body}>Email subject: {incident.notification_payload.email_subject}</Text>
            <Text style={[styles.body, styles.muted]}>{incident.notification_payload.email_body}</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

function DetailStat({ label, value }) {
  return (
    <View style={styles.statBox}>
      <Text style={styles.statLabel}>{label.toUpperCase()}</Text>
      <Text style={styles.statValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: colors.bg },
  container: { padding: 16 },
  centered: { flex: 1, alignItems: "center", justifyContent: "center" },
  backLink: { color: colors.accent, fontSize: 15, marginBottom: 12 },
  headerRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  h1: { color: colors.text, fontSize: 20, fontWeight: "700" },
  pill: { borderRadius: 999, paddingHorizontal: 10, paddingVertical: 4 },
  muted: { color: colors.muted, fontSize: 13 },
  summary: { color: colors.text, fontSize: 15, marginVertical: 10 },
  grid: { flexDirection: "row", flexWrap: "wrap", gap: 12, marginBottom: 8 },
  statBox: { width: "45%" },
  statLabel: { color: colors.muted, fontSize: 11, textTransform: "uppercase" },
  statValue: { color: colors.text, fontSize: 14, marginTop: 2, textTransform: "capitalize" },
  sectionTitle: { color: colors.muted, fontSize: 13, textTransform: "uppercase", marginTop: 16, marginBottom: 6 },
  bullet: { color: colors.text, fontSize: 14, marginBottom: 2 },
  body: { color: colors.text, fontSize: 14 },
  actions: { flexDirection: "row", gap: 10, marginTop: 20 },
  btn: { paddingHorizontal: 16, paddingVertical: 10, borderRadius: 8 },
  btnText: { color: "#08122b", fontWeight: "700", fontSize: 14 },
  error: { color: colors.red, marginTop: 10 },
  notifyBox: { marginTop: 20, borderTopWidth: 1, borderTopColor: colors.border, paddingTop: 12 },
});