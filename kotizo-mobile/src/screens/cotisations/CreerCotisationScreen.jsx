import { useState } from 'react'
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator, Alert } from 'react-native'
import api from '../../services/api'

export default function CreerCotisationScreen({ navigation }) {
    const [form, setForm] = useState({ nom: '', description: '', montant_unitaire: '', nombre_participants: '', numero_receveur: '' })
    const [loading, setLoading] = useState(false)
    const update = (key, val) => setForm((prev) => ({ ...prev, [key]: val }))

    const handleCreer = async () => {
        setLoading(true)
        try {
            const date_expiration = new Date()
            date_expiration.setDate(date_expiration.getDate() + 7)
            await api.post('/cotisations/', {
                ...form,
                montant_unitaire: parseInt(form.montant_unitaire),
                nombre_participants: parseInt(form.nombre_participants),
                date_expiration: date_expiration.toISOString(),
            })
            Alert.alert('Succes', 'Cotisation creee !', [{ text: 'OK', onPress: () => navigation.goBack() }])
        } catch (error) {
            const errors = error.response?.data
            const msg = errors ? Object.values(errors).flat().join('\n') : 'Erreur creation'
            Alert.alert('Erreur', msg)
        } finally {
            setLoading(false)
        }
    }

    return (
        <ScrollView style={styles.container}>
            <View style={styles.header}>
                <TouchableOpacity onPress={() => navigation.goBack()}>
                    <Text style={styles.back}>Retour</Text>
                </TouchableOpacity>
                <Text style={styles.title}>Nouvelle cotisation</Text>
            </View>
            {[
                { key: 'nom', placeholder: 'Nom de la cotisation' },
                { key: 'description', placeholder: 'Description (optionnel)' },
                { key: 'montant_unitaire', placeholder: 'Montant par personne (FCFA)', keyboardType: 'numeric' },
                { key: 'nombre_participants', placeholder: 'Nombre de participants', keyboardType: 'numeric' },
                { key: 'numero_receveur', placeholder: 'Votre numero receveur (ex: 90000000)', keyboardType: 'phone-pad' },
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
            <Text style={styles.note}>La cotisation expirera dans 7 jours par defaut.</Text>
            <TouchableOpacity style={styles.btn} onPress={handleCreer} disabled={loading}>
                {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Creer la cotisation</Text>}
            </TouchableOpacity>
        </ScrollView>
    )
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#fff' },
    header: { padding: 16, paddingTop: 50 },
    back: { color: '#1D9E75', fontSize: 14, marginBottom: 8 },
    title: { fontSize: 22, fontWeight: '600', color: '#222', marginBottom: 16 },
    input: { borderWidth: 1, borderColor: '#e0e0e0', borderRadius: 12, padding: 14, fontSize: 15, marginHorizontal: 16, marginBottom: 12, color: '#222' },
    note: { fontSize: 12, color: '#888', marginHorizontal: 16, marginBottom: 16 },
    btn: { backgroundColor: '#1D9E75', margin: 16, padding: 16, borderRadius: 12, alignItems: 'center' },
    btnText: { color: '#fff', fontSize: 16, fontWeight: '600' },
})