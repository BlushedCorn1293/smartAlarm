import * as React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import AlarmScreen from './(tabs)/alarms'; // Assuming your component is in `screens/AlarmsScreen`
import AlarmDetailScreen from './details/alarmDetail'; // The new screen for individual alarm details
import DeadlineScreen from './(tabs)/deadlines'; // Assuming your component is in `screens/DeadlinesScreen`
import DeadlineDetailScreen from './details/deadlineDetail'; // The new screen for individual deadline details
import EditDeadlineScreen from './details/editDetails/editDeadline'; // The new screen for editing deadlines
import SettingsScreen from './(tabs)/settings';
import { ApiProvider } from './context/ApiContext'; // Adjust path based on your folder structure
import { useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

const Stack = createStackNavigator();

export default function Navigation() {

    // Initialize the apiUrl state here
    const [apiUrl, setApiUrl] = React.useState('');

    // Fetch the saved API URL from AsyncStorage when the component is mounted
    useEffect(() => {
        const loadApiUrl = async () => {
            try {
                const savedUrl = await AsyncStorage.getItem('apiUrl');
                if (savedUrl) {
                    setApiUrl(savedUrl);
                }
            } catch (error) {
                console.error('Error loading API URL:', error);
            }
        };

        loadApiUrl();
    }, []);

    return (
        <NavigationContainer>
            <Stack.Navigator initialRouteName="Alarms">
                <Stack.Screen name="Alarms" component={AlarmScreen} />
                <Stack.Screen name="AlarmDetail" component={AlarmDetailScreen} options={{ title: 'Alarm Details' }} />

                {/* Passing apiUrl as initialParams to DeadlinesScreen */}
                <Stack.Screen
                    name="Deadlines"
                    component={DeadlineScreen}
                    initialParams={{ apiUrl }}  // Pass the apiUrl to DeadlinesScreen
                />
                <Stack.Screen name="DeadlineDetail" component={DeadlineDetailScreen} options={{ title: 'Deadline Details' }} />
                <Stack.Screen name="EditDeadline" component={EditDeadlineScreen} />

                {/* Settings Screen */}
                <Stack.Screen
                    name="Settings"
                    component={SettingsScreen}
                    initialParams={{ apiUrl }}  // Pass apiUrl to SettingsScreen as well
                />
            </Stack.Navigator>
































































































            {/* <Stack.Navigator initialRouteName="Alarms">
                <Stack.Screen name="Alarms" component={AlarmScreen} />
                <Stack.Screen name="AlarmDetail" component={AlarmDetailScreen} options={{ title: 'Alarm Details' }} />
            </Stack.Navigator>

            <Stack.Navigator initialRouteName="Deadlines">
                <Stack.Screen name="Deadlines" component={DeadlineScreen} initialParams={{ apiUrl }} />
                <Stack.Screen name="DeadlineDetail" component={DeadlineDetailScreen} options={{ title: 'Deadline Details' }} />
                <Stack.Screen name="EditDeadline" component={EditDeadlineScreen} />
            </Stack.Navigator>

            <Stack.Navigator initialRouteName="Settings">
                <Stack.Screen
                    name="Settings"
                    component={SettingsScreen}
                />
            </Stack.Navigator> */}
        </NavigationContainer>
    );
}
