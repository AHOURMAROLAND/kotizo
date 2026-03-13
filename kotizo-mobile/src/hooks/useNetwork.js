import { useEffect, useState } from 'react'
import NetInfo from '@react-native-community/netinfo'
import { useNavigation } from '@react-navigation/native'

export function useNetwork() {
    const [isConnected, setIsConnected] = useState(true)
    const navigation = useNavigation()

    useEffect(() => {
        const unsubscribe = NetInfo.addEventListener((state) => {
            const connected = state.isConnected && state.isInternetReachable
            setIsConnected(connected)
            if (!connected) {
                navigation.reset({ index: 0, routes: [{ name: 'Historique' }] })
            }
        })
        return () => unsubscribe()
    }, [])

    return isConnected
}