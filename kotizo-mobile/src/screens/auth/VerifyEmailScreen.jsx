import { View, Text, TouchableOpacity, StyleSheet } from 'react-native'

export default function VerifyEmailScreen({ navigation }) {
    return (
        <View style={styles.container}>
            <Text style={styles.icon}>ok</Text>
            <Text style={styles.title}>Verifiez votre email</Text>
            <Text style={styles.subtitle}>Un lien de verification a ete envoye a votre adresse email. Cliquez dessus pour activer votre compte.</Text>
            <TouchableOpacity style={styles.btn} onPress={() => navigation.navigate('Login')}>
                <Text style={styles.btnText}>Aller a la connexion</Text>
            </TouchableOpacity>
        </View>
    )
}

const styles = StyleSheet.create({
    container: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24, backgroundColor: '#fff' },
    icon: { fontSize: 48, marginBottom: 16, color: '#1D9E75', fontWeight: '700' },
    title: { fontSize: 22, fontWeight: '600', color: '#222', marginBottom: 12, textAlign: 'center' },
    subtitle: { fontSize: 14, color: '#888', textAlign: 'center', lineHeight: 22, marginBottom: 32 },
    btn: { backgroundColor: '#1D9E75', padding: 16, borderRadius: 12, width: '100%', alignItems: 'center' },
    btnText: { color: '#fff', fontSize: 16, fontWeight: '600' },
})