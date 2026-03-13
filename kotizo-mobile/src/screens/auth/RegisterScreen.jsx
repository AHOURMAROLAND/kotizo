import { useState } from 'react'
import {
    View, Text, TextInput, TouchableOpacity,
    StyleSheet, ActivityIndicator, Alert,
    KeyboardAvoidingView, Platform, ScrollView
} from 'react-native'
import api from '../../services/api'

export default function RegisterScreen({ navigation }) {
    const [form, setForm] = useState({
        email: '', nom: '', prenom: '', telephone: '',
        pays: 'TG', password: '', password_confirm: '',
    })
    const [cgu, setCgu] = useState(false)
    const [politique, setPolitique] = useState(false)
    const [age, setAge] = useState(false)
    const [loading, setLoading] = useState(false)

    const update = (key, val) => setForm((prev) => ({ ...prev, [key]: val }))

    const handleRegister = async () => {
        if (!cgu || !politique || !age) {
            Alert.alert('Erreur', 'Vous devez accepter les 3 conditions')
            return
        }
        setLoading(true)
        try {
            await api.post('/auth/inscription/', { ...form, cgu_acceptees: cgu, politique_confidentialite: politique, age_confirme: age })
            Alert.alert('Succes', 'Compte cree ! Verifiez votre email.', [
                { text: 'OK', onPress: () => navigation.navigate('Login') }
            ])
        } catch (error) {
            const errors = error.response?.data
            const msg = errors ? Object.values(errors).flat().join('\n') : 'Erreur inscription'
            Alert.alert('Erreur', msg)
        } finally {
            setLoading(false)
        }
    }

    return (
        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={{ flex: 1 }}>
            <ScrollView style={styles.container} contentContainerStyle={styles.inner}>
                <Text style={styles.title}>Creer un compte</Text>

                {[
                    { key: 'prenom', placeholder: 'Prenom' },
                    { key: 'nom', placeholder: 'Nom' },
                    { key: 'email', placeholder: 'Email', keyboardType: 'email-address' },
                    { key: 'telephone', placeholder: 'Telephone (ex: 90000000)', keyboardType: 'phone-pad' },
                    { key: 'password', placeholder: 'Mot de passe', secure: true },
                    { key: 'password_confirm', placeholder: 'Confirmer mot de passe', secure: true },
                ].map((field) => (
                    <TextInput
                        key={field.key}
                        style={styles.input}
                        placeholder={field.placeholder}
                        placeholderTextColor="#999"
                        value={form[field.key]}
                        onChangeText={(val) => update(field.key, val)}
                        keyboardType={field.keyboardType || 'default'}
                        secureTextEntry={field.secure || false}
                        autoCapitalize="none"
                    />
                ))}

                {[
                    { val: cgu, set: setCgu, label: "J'accepte les CGU" },
                    { val: politique, set: setPolitique, label: "J'accepte la politique de confidentialite" },
                    { val: age, set: setAge, label: "J'ai 18 ans ou plus" },
                ].map((item, i) => (
                    <TouchableOpacity key={i} style={styles.checkRow} onPress={() => item.set(!item.val)}>
                        <View style={[styles.checkbox, item.val && styles.checkboxActive]}>
                            {item.val && <Text style={styles.checkmark}>ok</Text>}
                        </View>
                        <Text style={styles.checkLabel}>{item.label}</Text>
                    </TouchableOpacity>
                ))}

                <TouchableOpacity style={styles.btn} onPress={handleRegister} disabled={loading}>
                    {loading
                        ? <ActivityIndicator color="#fff" />
                        : <Text style={styles.btnText}>S'inscrire</Text>
                    }
                </TouchableOpacity>

                <TouchableOpacity onPress={() => navigation.navigate('Login')}>
                    <Text style={styles.link}>Deja un compte ? Se connecter</Text>
                </TouchableOpacity>
            </ScrollView>
        </KeyboardAvoidingView>
    )
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#fff' },
    inner: { padding: 24, paddingTop: 50 },
    title: { fontSize: 26, fontWeight: '600', color: '#222', marginBottom: 24 },
    input: { borderWidth: 1, borderColor: '#e0e0e0', borderRadius: 12, padding: 14, fontSize: 15, marginBottom: 12, color: '#222' },
    checkRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 12, gap: 10 },
    checkbox: { width: 22, height: 22, borderRadius: 6, borderWidth: 1.5, borderColor: '#ccc', justifyContent: 'center', alignItems: 'center' },
    checkboxActive: { backgroundColor: '#1D9E75', borderColor: '#1D9E75' },
    checkmark: { color: '#fff', fontSize: 10, fontWeight: '700' },
    checkLabel: { flex: 1, fontSize: 13, color: '#444' },
    btn: { backgroundColor: '#1D9E75', padding: 16, borderRadius: 12, alignItems: 'center', marginTop: 16 },
    btnText: { color: '#fff', fontSize: 16, fontWeight: '600' },
    link: { textAlign: 'center', color: '#1D9E75', marginTop: 20, fontSize: 14 },
})