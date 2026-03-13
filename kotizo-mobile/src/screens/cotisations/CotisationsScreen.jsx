import { useState, useEffect } from 'react'
import { View, Text, FlatList, TouchableOpacity, StyleSheet, ActivityIndicator, RefreshControl } from 'react-native'
import api from '../../services/api'

export default function CotisationsScreen({ navigation }) {
    const [cotisations, setCotisations] = useState([])
    const [loading, setLoading] = useState(true)
    const [refreshing, setRefreshing] = useState(false)

    useEffect(() => { charger() }, [])

    const charger = async () => {
        try {
            const res = await api.get('/cotisations/')
            setCotisations(res.data)
        } catch {}
        finally { setLoading(false) }
    }

    const onRefresh = async () => {
        setRefreshing(true)
        await charger()
        setRefreshing(false)
    }

    if (loading) return <View style={styles.center}><ActivityIndicator size="large" color="#1D9E75" /></View>

    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.title}>Mes cotisations</Text>
                <TouchableOpacity style={styles.btnNew} onPress={() => navigation.navigate('CreerCotisation')}>
                    <Text style={styles.btnNewText}>+ Nouvelle</Text>
                </TouchableOpacity>
            </View>
            <FlatList
                data={cotisations}
                keyExtractor={(item) => item.id}
                refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
                contentContainerStyle={{ padding: 16, gap: 10 }}
                ListEmptyComponent={<Text style={styles.empty}>Aucune cotisation creee</Text>}
                renderItem={({ item }) => (
                    <TouchableOpacity style={styles.card} onPress={() => navigation.navigate('CotisationDetail', { slug: item.slug })}>
                        <View style={styles.cardRow}>
                            <Text style={styles.cardNom}>{item.nom}</Text>
                            <View style={[styles.badge, { backgroundColor: item.statut === 'active' ? '#E1F5EE' : '#F1EFE8' }]}>
                                <Text style={[styles.badgeText, { color: item.statut === 'active' ? '#0F6E56' : '#5F5E5A' }]}>{item.statut}</Text>
                            </View>
                        </View>
                        <Text style={styles.cardMontant}>{item.montant_unitaire} FCFA x {item.nombre_participants} participants</Text>
                        <View style={styles.progressBar}>
                            <View style={[styles.progressFill, { width: `${item.progression}%` }]} />
                        </View>
                        <Text style={styles.progressText}>{item.participants_payes}/{item.nombre_participants} payes</Text>
                    </TouchableOpacity>
                )}
            />
        </View>
    )
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#f8f9fa' },
    center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
    header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, paddingTop: 50, backgroundColor: '#fff' },
    title: { fontSize: 20, fontWeight: '600', color: '#222' },
    btnNew: { backgroundColor: '#1D9E75', paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20 },
    btnNewText: { color: '#fff', fontSize: 13, fontWeight: '500' },
    card: { backgroundColor: '#fff', borderRadius: 12, padding: 16, borderWidth: 0.5, borderColor: '#e0e0e0' },
    cardRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 },
    cardNom: { fontSize: 15, fontWeight: '600', color: '#222', flex: 1 },
    cardMontant: { fontSize: 12, color: '#888', marginBottom: 10 },
    badge: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 20 },
    badgeText: { fontSize: 11, fontWeight: '500' },
    progressBar: { height: 4, backgroundColor: '#f0f0f0', borderRadius: 4, marginBottom: 6 },
    progressFill: { height: 4, backgroundColor: '#1D9E75', borderRadius: 4 },
    progressText: { fontSize: 11, color: '#888' },
    empty: { textAlign: 'center', color: '#888', marginTop: 40 },
})