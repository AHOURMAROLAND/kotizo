import { useState } from 'react'
import {
    View, Text, TextInput, TouchableOpacity,
    StyleSheet, ActivityIndicator, Alert, KeyboardAvoidingView, Platform
} from 'react-native'
import { useAuth } from '../../hooks/useAuth'

export default function LoginScreen({ navigation }) {
    const { connexion } = useAuth()
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [loading, setLoading] = useState(false)

    const handleLogin = async () => {
        if (!email || !password) {
            Alert.alert('Erreur', 'Remplissez tous les champs')
            return
        }
        setLoading(true)
        try {
            await connexion(email.trim().toLowerCase(), password)
        } catch (error) {
            const msg = error.response?.data?.error || 'Erreur de connexion'
            Alert.alert('Erreur', msg)
        } finally {
            setLoading(false)
        }
    }

    return (
        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.container}>
            <View style={styles.inner}>
                <Text style={styles.logo}>Kotizo</Text>
                <Text style={styles.subtitle}>Cotisations collectives simplifiees</Text>

                <TextInput
                    style={styles.input}
                    placeholder="Email"
                    value={email}
                    onChangeText={setEmail}
                    keyboardType="email-address"
                    autoCapitalize="none"
                    placeholderTextColor="#999"
                />
                <TextInput
                    style={styles.input}
                    placeholder="Mot de passe"
                    value={password}
                    onChangeText={setPassword}
                    secureTextEntry
                    placeholderTextColor="#999"
                />

                <TouchableOpacity style={styles.btn} onPress={handleLogin} disabled={loading}>
                    {loading
                        ? <ActivityIndicator color="#fff" />
                        : <Text style={styles.btnText}>Se connecter</Text>
                    }
                </TouchableOpacity>

                <TouchableOpacity onPress={() => navigation.navigate('Register')}>
                    <Text style={styles.link}>Pas de compte ? S'inscrire</Text>
                </TouchableOpacity>
            </View>
        </KeyboardAvoidingView>
    )
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#fff' },
    inner: { flex: 1, justifyContent: 'center', paddingHorizontal: 24 },
    logo: { fontSize: 36, fontWeight: 'bold', color: '#1D9E75', textAlign: 'center', marginBottom: 8 },
    subtitle: { fontSize: 14, color: '#888', textAlign: 'center', marginBottom: 40 },
    input: { borderWidth: 1, borderColor: '#e0e0e0', borderRadius: 12, padding: 14, fontSize: 15, marginBottom: 14, color: '#222' },
    btn: { backgroundColor: '#1D9E75', padding: 16, borderRadius: 12, alignItems: 'center', marginTop: 8 },
    btnText: { color: '#fff', fontSize: 16, fontWeight: '600' },
    link: { textAlign: 'center', color: '#1D9E75', marginTop: 20, fontSize: 14 },
})