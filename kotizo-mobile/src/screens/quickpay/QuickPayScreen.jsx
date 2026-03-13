import { useState } from 'react'
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, Alert, ScrollView } from 'react-native'
import api from '../../services/api'

export default function QuickPayScreen({ navigation }) {
    const [form, setForm] = useState({ montant: '', description: '', numero_receveur: '' })
    const [loading, setLoading] = useState(false)
    const [quickpay, setQuickpay] = useState(null)
    const update = (key, val) => setForm((prev) => ({ ...prev, [key]: val }))

    const handleCreer = async () => {
        setLoading(true)
        try {
            const res = await api.post('/quickpay/', {
                ...form,
                montant: parseInt(form.montant),
            })
            setQuickpay(res.data)
        } catch (error) {
            const errors = error.response?.data
            Alert.alert('Erreur', errors ? Object.values(errors).flat().join('\n') : 'Erreur')
        } finally {
            setLoading(false)
        }
    }

    if (quickpay) return (
        <View style={styles.container}>
            <View style={styles.success}>
                <Text style={styles.successTitle}>Quick Pay cree !</Text>
                <Text style={styles.code}>{quickpay.code}</Text>
                <Text style={styles.montant}>{quickpay.montant} FCFA</Text>
                <Text style={styles.lien}>kotizo.app/qp/{quickpay.code}</Text>
                <Text style={styles.expire}>Expire dans 1 heure</Text>
                <TouchableOpacity style={styles.btn} onPress={() => setQuickpay(null)}>
                    <Text style={styles.btnText}>Nouveau Quick Pay</Text>
                </TouchableOpacity>
            </View>
        </View>
    )

    return (
        <ScrollView style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.title}>Quick Pay</Text>
                <Text style={styles.subtitle}>Generez un lien de paiement instantane</Text>
            </View>
            {[
                { key: 'montant', placeholder: 'Montant (FCFA)', keyboardType: 'numeric' },
                { key: 'description', placeholder: 'Description (optionnel)' },
                { key: 'numero_receveur', placeholder: 'Votre numero receveur', keyboardType: 'phone-pad' },
            ].map((field) => (
                <TextInput
                    key={field.key}
                    style={styles.input}
                    placeholder={field.placeholder}
                    placeholderTextColor="#999"
                    value={form[field.key]}
                    onChangeText={(val) => update(field.key, val)}
                    keyboardType={field.keyboardType || 'default'}
                />
            ))}
            <TouchableOpacity style={styles.btn} onPress={handleCreer} disabled={loading}>
                {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Generer le lien</Text>}
            </TouchableOpacity>
        </ScrollView>
    )
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#fff' },
    header: { padding: 16, paddingTop: 50 },
    title: { fontSize: 22, fontWeight: '600', color: '#222' },
    subtitle: { fontSize: 13, color: '#888', marginTop: 4, marginBottom: 16 },
    input: { borderWidth: 1, borderColor: '#e0e0e0', borderRadius: 12, padding: 14, fontSize: 15, marginHorizontal: 16, marginBottom: 12, color: '#222' },
    btn: { backgroundColor: '#1D9E75', margin: 16, padding: 16, borderRadius: 12, alignItems: 'center' },
    btnText: { color: '#fff', fontSize: 16, fontWeight: '600' },
    success: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 24 },
    successTitle: { fontSize: 22, fontWeight: '600', color: '#222', marginBottom: 16 },
    code: { fontSize: 36, fontWeight: '700', color: '#1D9E75', letterSpacing: 4, marginBottom: 8 },
    montant: { fontSize: 20, color: '#222', marginBottom: 8 },
    lien: { fontSize: 13, color: '#888', marginBottom: 8 },
    expire: { fontSize: 12, color: '#BA7517', marginBottom: 24 },
})