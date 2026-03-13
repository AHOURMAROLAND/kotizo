import { useState, useEffect } from 'react'
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, ActivityIndicator, Alert } from 'react-native'
import api from '../../services/api'

export default function CotisationDetailScreen({ route, navigation }) {
    const { slug } = route.params
    const [cotisation, setCotisation] = useState(null)
    const [loading, setLoading] = useState(true)
    const [payLoading, setPayLoading] = useState(false)

    useEffect(() => { charger() }, [])

    const charger = async () => {
        try {
            const res = await api.get(`/cotisations/${slug}/`)
            setCotisation(res.data)
        } catch {}
        finally { setLoading(false) }
    }

    const rejoindre = async () => {
        try {
            await api.post(`/cotisations/${slug}/rejoindre/`)
            await charger()
            Alert.alert('Succes', 'Vous avez rejoint la cotisation. Procedez au paiement.')
        } catch (error) {
            Alert.alert('Erreur', error.response?.data?.error || 'Erreur')
        }
    }

    const payer = async () => {
        setPayLoading(true)
        try {
            const res = await api.post(`/paiements/initier/${slug}/`)
            navigation.navigate('Paiement', { payment_url: res.data.payment_url, montant: res.data.montant })
        } catch (error) {
            Alert.alert('Erreur', error.response?.data?.error || 'Erreur paiement')
        } finally {
            setPayLoading(false)
        }
    }

    if (loading) return <View style={styles.center}><ActivityIndicator size="large" color="#1D9E75" /></View>
    if (!cotisation) return <View style={styles.center}><Text>Cotisation introuvable</Text></View>

    return (
        <ScrollView style={styles.container}>
            <View style={styles.header}>
                <TouchableOpacity onPress={() => navigation.goBack()}>
                    <Text style={styles.back}>Retour</Text>
                </TouchableOpacity>
                <Text style={styles.title}>{cotisation.nom}</Text>
            </View>
            <View style={styles.card}>
                <Text style={styles.label}>Montant unitaire</Text>
                <Text style={styles.value}>{cotisation.montant_unitaire} FCFA</Text>
                <Text style={styles.label}>Participants</Text>
                <Text style={styles.value}>{cotisation.participants_payes}/{cotisation.nombre_participants}</Text>
                <Text style={styles.label}>Statut</Text>
                <Text style={styles.value}>{cotisation.statut}</Text>
                <Text style={styles.label}>Expiration</Text>
                <Text style={styles.value}>{new Date(cotisation.date_expiration).toLocaleDateString('fr-FR')}</Text>
                <View style={styles.progressBar}>
                    <View style={[styles.progressFill, { width: `${cotisation.progression}%` }]} />
                </View>
                <Text style={styles.progressText}>{cotisation.progression}% complete</Text>
            </View>
            {!cotisation.est_createur && cotisation.statut === 'active' && (
                <View style={styles.actions}>
                    {!cotisation.ma_participation && (
                        <TouchableOpacity style={styles.btn} onPress={rejoindre}>
                            <Text style={styles.btnText}>Rejoindre</Text>
                        </TouchableOpacity>
                    )}
                    {cotisation.ma_participation?.statut === 'en_attente' && (
                        <TouchableOpacity style={styles.btn} onPress={payer} disabled={payLoading}>
                            {payLoading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Payer {cotisation.montant_unitaire} FCFA</Text>}
                        </TouchableOpacity>
                    )}
                    {cotisation.ma_participation?.statut === 'paye' && (
                        <View style={styles.paye}>
                            <Text style={styles.payeText}>Paiement confirme</Text>
                        </View>
                    )}
                </View>
            )}
        </ScrollView>
    )
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#f8f9fa' },
    center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
    header: { padding: 16, paddingTop: 50, backgroundColor: '#fff' },
    back: { color: '#1D9E75', fontSize: 14, marginBottom: 8 },
    title: { fontSize: 22, fontWeight: '600', color: '#222' },
    card: { backgroundColor: '#fff', margin: 16, borderRadius: 12, padding: 16, borderWidth: 0.5, borderColor: '#e0e0e0' },
    label: { fontSize: 12, color: '#888', marginTop: 10 },
    value: { fontSize: 16, fontWeight: '500', color: '#222' },
    progressBar: { height: 6, backgroundColor: '#f0f0f0', borderRadius: 4, marginTop: 16, marginBottom: 6 },
    progressFill: { height: 6, backgroundColor: '#1D9E75', borderRadius: 4 },
    progressText: { fontSize: 12, color: '#888' },
    actions: { padding: 16 },
    btn: { backgroundColor: '#1D9E75', padding: 16, borderRadius: 12, alignItems: 'center' },
    btnText: { color: '#fff', fontSize: 16, fontWeight: '600' },
    paye: { backgroundColor: '#E1F5EE', padding: 16, borderRadius: 12, alignItems: 'center' },
    payeText: { color: '#0F6E56', fontSize: 15, fontWeight: '500' },
})