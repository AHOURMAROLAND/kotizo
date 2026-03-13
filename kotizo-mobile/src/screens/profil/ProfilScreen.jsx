import { View, Text, TouchableOpacity, StyleSheet, Alert } from 'react-native'
import { useAuth } from '../../hooks/useAuth'

export default function ProfilScreen() {
    const { user, deconnexion } = useAuth()

    const handleDeconnexion = () => {
        Alert.alert('Deconnexion', 'Confirmer la deconnexion ?', [
            { text: 'Annuler', style: 'cancel' },
            { text: 'Deconnecter', style: 'destructive', onPress: deconnexion },
        ])
    }

    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <View style={styles.avatar}>
                    <Text style={styles.avatarText}>{user?.prenom?.[0]}{user?.nom?.[0]}</Text>
                </View>
                <Text style={styles.nom}>{user?.prenom} {user?.nom}</Text>
                <Text style={styles.email}>{user?.email}</Text>
                <View style={styles.badge}>
                    <Text style={styles.badgeText}>{user?.niveau}</Text>
                </View>
            </View>
            <View style={styles.section}>
                <TouchableOpacity style={styles.item}>
                    <Text style={styles.itemText}>Modifier le profil</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.item}>
                    <Text style={styles.itemText}>Verification identite</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.item}>
                    <Text style={styles.itemText}>Notifications</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.item}>
                    <Text style={styles.itemText}>Support</Text>
                </TouchableOpacity>
                <TouchableOpacity style={[styles.item, styles.itemDanger]} onPress={handleDeconnexion}>
                    <Text style={styles.itemTextDanger}>Se deconnecter</Text>
                </TouchableOpacity>
            </View>
        </View>
    )
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#f8f9fa' },
    header: { backgroundColor: '#fff', alignItems: 'center', padding: 24, paddingTop: 50 },
    avatar: { width: 72, height: 72, borderRadius: 36, backgroundColor: '#E1F5EE', justifyContent: 'center', alignItems: 'center', marginBottom: 12 },
    avatarText: { fontSize: 24, fontWeight: '600', color: '#1D9E75' },
    nom: { fontSize: 20, fontWeight: '600', color: '#222' },
    email: { fontSize: 13, color: '#888', marginTop: 4 },
    badge: { backgroundColor: '#E1F5EE', paddingHorizontal: 12, paddingVertical: 4, borderRadius: 20, marginTop: 8 },
    badgeText: { color: '#0F6E56', fontSize: 12, fontWeight: '500' },
    section: { margin: 16, backgroundColor: '#fff', borderRadius: 12, borderWidth: 0.5, borderColor: '#e0e0e0' },
    item: { padding: 16, borderBottomWidth: 0.5, borderBottomColor: '#e0e0e0' },
    itemText: { fontSize: 15, color: '#222' },
    itemDanger: { borderBottomWidth: 0 },
    itemTextDanger: { fontSize: 15, color: '#E24B4A' },
})