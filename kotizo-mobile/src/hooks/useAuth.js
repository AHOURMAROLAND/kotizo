import { useState, useEffect } from 'react'
import AsyncStorage from '@react-native-async-storage/async-storage'
import api from '../services/api'

export function useAuth() {
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        chargerUser()
    }, [])

    const chargerUser = async () => {
        try {
            const token = await AsyncStorage.getItem('access_token')
            if (token) {
                const res = await api.get('/auth/moi/')
                setUser(res.data)
            }
        } catch {
            await AsyncStorage.multiRemove(['access_token', 'refresh_token'])
        } finally {
            setLoading(false)
        }
    }

    const connexion = async (email, password) => {
        const res = await api.post('/auth/connexion/', { email, password })
        await AsyncStorage.setItem('access_token', res.data.access)
        await AsyncStorage.setItem('refresh_token', res.data.refresh)
        setUser(res.data.user)
        return res.data
    }

    const deconnexion = async () => {
        const refresh = await AsyncStorage.getItem('refresh_token')
        try { await api.post('/auth/deconnexion/', { refresh }) } catch {}
        await AsyncStorage.multiRemove(['access_token', 'refresh_token'])
        setUser(null)
    }

    return { user, loading, connexion, deconnexion, chargerUser }
}