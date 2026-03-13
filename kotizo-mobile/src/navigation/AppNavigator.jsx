import { NavigationContainer } from '@react-navigation/native'
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs'
import { createStackNavigator } from '@react-navigation/stack'
import { useAuth } from '../hooks/useAuth'

import LoginScreen from '../screens/auth/LoginScreen'
import RegisterScreen from '../screens/auth/RegisterScreen'
import VerifyEmailScreen from '../screens/auth/VerifyEmailScreen'

import DashboardScreen from '../screens/dashboard/DashboardScreen'
import CotisationsScreen from '../screens/cotisations/CotisationsScreen'
import CotisationDetailScreen from '../screens/cotisations/CotisationDetailScreen'
import CreerCotisationScreen from '../screens/cotisations/CreerCotisationScreen'
import PaiementScreen from '../screens/paiements/PaiementScreen'
import QuickPayScreen from '../screens/quickpay/QuickPayScreen'
import HistoriqueScreen from '../screens/historique/HistoriqueScreen'
import AgentIAScreen from '../screens/agent_ia/AgentIAScreen'
import ProfilScreen from '../screens/profil/ProfilScreen'

const Stack = createStackNavigator()
const Tab = createBottomTabNavigator()


function TabNavigator() {
    return (
        <Tab.Navigator
            screenOptions={{
                headerShown: false,
                tabBarActiveTintColor: '#1D9E75',
                tabBarInactiveTintColor: '#888',
                tabBarStyle: { paddingBottom: 5, height: 60 },
            }}
        >
            <Tab.Screen name="Dashboard" component={DashboardScreen} options={{ title: 'Accueil' }} />
            <Tab.Screen name="Cotisations" component={CotisationsScreen} options={{ title: 'Cotisations' }} />
            <Tab.Screen name="QuickPay" component={QuickPayScreen} options={{ title: 'Quick Pay' }} />
            <Tab.Screen name="Historique" component={HistoriqueScreen} options={{ title: 'Historique' }} />
            <Tab.Screen name="Profil" component={ProfilScreen} options={{ title: 'Profil' }} />
        </Tab.Navigator>
    )
}


export default function AppNavigator() {
    const { user, loading } = useAuth()

    if (loading) return null

    return (
        <NavigationContainer>
            <Stack.Navigator screenOptions={{ headerShown: false }}>
                {user ? (
                    <>
                        <Stack.Screen name="Main" component={TabNavigator} />
                        <Stack.Screen name="CotisationDetail" component={CotisationDetailScreen} />
                        <Stack.Screen name="CreerCotisation" component={CreerCotisationScreen} />
                        <Stack.Screen name="Paiement" component={PaiementScreen} />
                        <Stack.Screen name="AgentIA" component={AgentIAScreen} />
                    </>
                ) : (
                    <>
                        <Stack.Screen name="Login" component={LoginScreen} />
                        <Stack.Screen name="Register" component={RegisterScreen} />
                        <Stack.Screen name="VerifyEmail" component={VerifyEmailScreen} />
                    </>
                )}
            </Stack.Navigator>
        </NavigationContainer>
    )
}