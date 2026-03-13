import { useState, useEffect } from 'react'
import {
    View, Text, ScrollView, TouchableOpacity,
    StyleSheet, ActivityIndicator, RefreshControl
} from 'react-native'
import { useAuth } from '../../hooks/useAuth'
import api from '../../services/api'

export default function DashboardScreen({ navigation }) {
    const { user } = useAuth()
    const [cotisations, setCotisations] = useState([])
    const [loading, setLoading] = useState(true)
    const [refreshing, setRefreshing] = useState(false)

    useEffect(() => {
        charger()
    }, [])

    const charger = async () => {
        try {
            const res = await api.get('/cotisations/')
            setCotisations(res.data.slice(0, 3))
        } catch {}
        finally { setLoading(false) }
    }

    const onRefresh = async () => {
        setRefreshing(true)
        await charger()
        setRefreshing(false)
    }

    if (loading) return (
        <View style={styles.center}>
            <ActivityIndicator size="large" color="#1D9E75" />
        </View>
    )

    return (
        <ScrollView
            style={styles.container}
            refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        >
            <View style={styles.header}>
                <Text style={styles.bonjour}>Bonjour, {user?.prenom}</Text>
                <View style={styles.badge}>
                    <Text style={styles.badgeText}>{user?.niveau}</Text>
                </View>
            </View>

            <View style={styles.actionsRow}>
                <TouchableOpacity style={styles.actionBtn} onPress={() => navigation.navigate('CreerCotisation')}>
                    <Text style={styles.actionIcon}>+</Text>
                    <Text style={styles.actionLabel}>Cotisation</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.actionBtn} onPress={() => navigation.navigate('QuickPay')}>
                    <Text style={styles.actionIcon}>Q</Text>
                    <Text style={styles.actionLabel}>Quick Pay</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.actionBtn} onPress={() => navigation.navigate('Historique')}>
                    <Text style={styles.actionIcon}>H</Text>
                    <Text style={styles.actionLabel}>Historique</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.actionBtn} onPress={() => navigation.navigate('AgentIA')}>
                    <Text style={styles.actionIcon}>IA</Text>
                    <Text style={styles.actionLabel}>Assistant</Text>
                </TouchableOpacity>
            </View>

            <Text style={styles.sectionTitle}>Mes cotisations recentes</Text>

            {cotisations.length === 0 ? (
                <View style={styles.empty}>
                    <Text style={styles.emptyText}>Aucune cotisation. Creez-en une !</Text>
                </View>
            ) : (
                cotisations.map((cot) => (
                    <TouchableOpacity
                        key={cot.id}
                        style={styles.card}
                        onPress={() => navigation.navigate('CotisationDetail', { slug: cot.slug })}
                    >
                        <View style={styles.cardRow}>
                            <Text style={styles.cardNom}>{cot.nom}</Text>
                            <View style={[styles.statut, { backgroundColor: cot.statut === 'active' ? '#E1F5EE' : '#F1EFE8' }]}>
                                <Text style={[styles.statutText, { color: cot.statut === 'active' ? '#0F6E56' : '#5F5E5A' }]}>
                                    {cot.statut}
                                </Text>
                            </View>
                        </View>
                        <Text style={styles.cardMontant}>{cot.montant_unitaire} FCFA</Text>
                        <View style={styles.progressBar}>
                            <View style={[styles.progressFill, { width: `${cot.progression}%` }]} />
                        </View>
                        <Text style={styles.progressText}>{cot.participants_payes}/{cot.nombre_participants} participants</Text>
                    </TouchableOpacity>
                ))
            )}
        </ScrollView>
    )
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#f8f9fa' },
    center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
    header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 20, paddingTop: 50, backgroundColor: '#fff' },
    bonjour: { fontSize: 20, fontWeight: '600', color: '#222' },
    badge: { backgroundColor: '#E1F5EE', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 20 },
    badgeText: { color: '#0F6E56', fontSize: 12, fontWeight: '500' },
    actionsRow: { flexDirection: 'row', justifyContent: 'space-around', backgroundColor: '#fff', padding: 16, marginTop: 8 },
    actionBtn: { alignItems: 'center', gap: 4 },
    actionIcon: { width: 48, height: 48, backgroundColor: '#E1F5EE', borderRadius: 24, textAlign: 'center', textAlignVertical: 'center', fontSize: 16, fontWeight: '600', color: '#1D9E75' },
    actionLabel: { fontSize: 11, color: '#666' },
    sectionTitle: { fontSize: 16, fontWeight: '600', color: '#222', padding: 16, paddingBottom: 8 },
    card: { backgroundColor: '#fff', marginHorizontal: 16, marginBottom: 10, borderRadius: 12, padding: 16, borderWidth: 0.5, borderColor: '#e0e0e0' },
    cardRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 },
    cardNom: { fontSize: 15, fontWeight: '600', color: '#222', flex: 1 },
    cardMontant: { fontSize: 13, color: '#666', marginBottom: 10 },
    statut: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 20 },
    statutText: { fontSize: 11, fontWeight: '500' },
    progressBar: { height: 4, backgroundColor: '#f0f0f0', borderRadius: 4, marginBottom: 6 },
    progressFill: { height: 4, backgroundColor: '#1D9E75', borderRadius: 4 },
    progressText: { fontSize: 11, color: '#888' },
    empty: { padding: 30, alignItems: 'center' },
    emptyText: { color: '#888', fontSize: 14 },
})