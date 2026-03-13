import { useState, useRef } from 'react'
import {
    View, Text, TextInput, TouchableOpacity,
    FlatList, StyleSheet, ActivityIndicator, KeyboardAvoidingView, Platform
} from 'react-native'
import api from '../../services/api'

export default function AgentIAScreen() {
    const [messages, setMessages] = useState([
        { id: '0', role: 'assistant', contenu: 'Bonjour ! Je suis votre assistant Kotizo. Comment puis-je vous aider ?' }
    ])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const flatListRef = useRef(null)

    const envoyer = async () => {
        if (!input.trim() || loading) return

        const msgUser = { id: Date.now().toString(), role: 'user', contenu: input.trim() }
        setMessages((prev) => [...prev, msgUser])
        setInput('')
        setLoading(true)

        try {
            const res = await api.post('/agent-ia/', { message: input.trim() })
            setMessages((prev) => [...prev, { id: res.data.id?.toString() || Date.now().toString(), ...res.data }])
        } catch {
            setMessages((prev) => [...prev, {
                id: Date.now().toString(),
                role: 'assistant',
                contenu: 'Desolee, une erreur est survenue. Veuillez reessayer.',
            }])
        } finally {
            setLoading(false)
        }
    }

    const renderMessage = ({ item }) => (
        <View style={[styles.bubble, item.role === 'user' ? styles.bubbleUser : styles.bubbleIA]}>
            <Text style={[styles.bubbleText, item.role === 'user' && styles.bubbleTextUser]}>
                {item.contenu}
            </Text>
        </View>
    )

    return (
        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.headerTitle}>Assistant Kotizo</Text>
            </View>

            <FlatList
                ref={flatListRef}
                data={messages}
                keyExtractor={(item) => item.id}
                renderItem={renderMessage}
                contentContainerStyle={styles.messagesList}
                onContentSizeChange={() => flatListRef.current?.scrollToEnd()}
            />

            {loading && (
                <View style={styles.typingContainer}>
                    <ActivityIndicator size="small" color="#1D9E75" />
                    <Text style={styles.typingText}>En train de repondre...</Text>
                </View>
            )}

            <View style={styles.inputRow}>
                <TextInput
                    style={styles.input}
                    placeholder="Posez votre question..."
                    value={input}
                    onChangeText={setInput}
                    placeholderTextColor="#999"
                    multiline
                />
                <TouchableOpacity style={styles.sendBtn} onPress={envoyer} disabled={loading}>
                    <Text style={styles.sendText}>Envoyer</Text>
                </TouchableOpacity>
            </View>
        </KeyboardAvoidingView>
    )
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#f8f9fa' },
    header: { padding: 16, paddingTop: 50, backgroundColor: '#fff', borderBottomWidth: 0.5, borderBottomColor: '#e0e0e0' },
    headerTitle: { fontSize: 18, fontWeight: '600', color: '#222' },
    messagesList: { padding: 16, gap: 10 },
    bubble: { maxWidth: '80%', padding: 12, borderRadius: 16, marginBottom: 8 },
    bubbleUser: { backgroundColor: '#1D9E75', alignSelf: 'flex-end', borderBottomRightRadius: 4 },
    bubbleIA: { backgroundColor: '#fff', alignSelf: 'flex-start', borderBottomLeftRadius: 4, borderWidth: 0.5, borderColor: '#e0e0e0' },
    bubbleText: { fontSize: 14, color: '#222', lineHeight: 20 },
    bubbleTextUser: { color: '#fff' },
    typingContainer: { flexDirection: 'row', alignItems: 'center', padding: 12, gap: 8 },
    typingText: { fontSize: 13, color: '#888' },
    inputRow: { flexDirection: 'row', padding: 12, backgroundColor: '#fff', borderTopWidth: 0.5, borderTopColor: '#e0e0e0', gap: 8 },
    input: { flex: 1, borderWidth: 1, borderColor: '#e0e0e0', borderRadius: 20, paddingHorizontal: 14, paddingVertical: 8, fontSize: 14, color: '#222', maxHeight: 80 },
    sendBtn: { backgroundColor: '#1D9E75', paddingHorizontal: 16, borderRadius: 20, justifyContent: 'center' },
    sendText: { color: '#fff', fontSize: 14, fontWeight: '500' },
})