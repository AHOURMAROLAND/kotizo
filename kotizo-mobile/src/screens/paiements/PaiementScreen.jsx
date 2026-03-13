import { View, Text, StyleSheet, ActivityIndicator } from 'react-native'
import { WebView } from 'react-native-webview'

export default function PaiementScreen({ route, navigation }) {
    const { payment_url, montant } = route.params

    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.title}>Paiement — {montant} FCFA</Text>
            </View>
            <WebView
                source={{ uri: payment_url }}
                startInLoadingState
                renderLoading={() => <ActivityIndicator size="large" color="#1D9E75" style={styles.loader} />}
                onNavigationStateChange={(state) => {
                    if (state.url.includes('paiement-success')) {
                        navigation.reset({ index: 0, routes: [{ name: 'Main' }] })
                    }
                    if (state.url.includes('paiement-cancel')) {
                        navigation.goBack()
                    }
                }}
            />
        </View>
    )
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#fff' },
    header: { padding: 16, paddingTop: 50, backgroundColor: '#fff', borderBottomWidth: 0.5, borderBottomColor: '#e0e0e0' },
    title: { fontSize: 16, fontWeight: '600', color: '#222' },
    loader: { flex: 1 },
})