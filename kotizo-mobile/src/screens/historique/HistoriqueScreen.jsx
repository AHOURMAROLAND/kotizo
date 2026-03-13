import { useState, useEffect } from 'react'
import { View, Text, FlatList, StyleSheet, ActivityIndicator, TouchableOpacity } from 'react-native'
import AsyncStorage from '@react-native-async-storage/async-storage'
import api from '../../services/api'

const ONGLETS = ['Cotisations', 'Participations', 'Quick Pay', 'Transactions']

export default function HistoriqueScreen() {
    const [onglet, setOnglet] = useState(0)
    const [data, setData] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => { charger() }, [onglet])

    const charger = async () => {
        setLoading(true)
        try {
            let res
            if (onglet === 0) res = await api.get('/cotisations/')
            if (onglet === 1) res = await api.get('/cotisations/participations/mes/')
            if (onglet === 2) res = await api.get('/quickpay/')
            if (onglet === 3) res = await api.get('/paiements/historique/')
            setData(res.data)
            await AsyncStorage.setItem(`historique_${onglet}`, JSON.stringify(res.data))
        } catch {
            const cached = await AsyncStorage.getItem(`historique_${onglet}`)
            if (cached) setData(JSON.parse(cached))
        } finally {
            setLoading(false)
        }
    }

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Historique</Text>
            <View style={styles.onglets}>
                {ONGLETS.map((label, i) => (
                    <TouchableOpacity key={i} style={[styles.onglet, onglet === i && styles.ongletActive]} onPress={() => setOnglet(i)}>
                        <Text style={[styles.ongletText, onglet === i && styles.ongletTextActive]}>{label}</Text>
                    </TouchableOpacity>
                ))}
            </View>
            {loading
                ? <ActivityIndicator size="large" color="#1D9E75" style={{ marginTop: 40 }} />
                : <FlatList
                    data={data}
                    keyExtractor={(item) => item.id?.toString()}
                    contentContainerStyle={{ padding: 16, gap: 10 }}
                    ListEmptyComponent={<Text style={styles.empty}>Aucune donnee</Text>}
                    renderItem={({ item }) => (
                        <View style={styles.item}>
                            <Text style={styles.itemTitle}>{item.nom || item.type_transaction || item.code || 'Element'}</Text>
                            <Text style={styles.itemSub}>{item.statut} — {item.montant || item.montant_unitaire || ''} FCFA</Text>
                        </View>
                    )}
                />
            }
        </View>
    )
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#f8f9fa' },
    title: { fontSize: 20, fontWeight: '600', color: '#222', padding: 16, paddingTop: 50, backgroundColor: '#fff' },
    onglets: { flexDirection: 'row', backgroundColor: '#fff', borderBottomWidth: 0.5, borderBottomColor: '#e0e0e0' },
    onglet: { flex: 1, padding: 10, alignItems: 'center' },
    ongletActive: { borderBottomWidth: 2, borderBottomColor: '#1D9E75' },
    ongletText: { fontSize: 11, color: '#888' },
    ongletTextActive: { color: '#1D9E75', fontWeight: '600' },
    item: { backgroundColor: '#fff', borderRadius: 12, padding: 14, borderWidth: 0.5, borderColor: '#e0e0e0' },
    itemTitle: { fontSize: 14, fontWeight: '500', color: '#222' },
    itemSub: { fontSize: 12, color: '#888', marginTop: 4 },
    empty: { textAlign: 'center', color: '#888', marginTop: 40 },
})