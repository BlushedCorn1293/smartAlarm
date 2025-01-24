import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, PanResponder, TextInput, Button, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ThemedText } from '@/components/ThemedText'; // Assuming you have this component
import { useRoute } from '@react-navigation/native';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { useColorScheme } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function AlarmDetailScreen() {
    const colorScheme = useColorScheme();

    const borderColor = colorScheme === 'light' ? '#333' : '#F9F9F9';
    const saveButtonColor = colorScheme === 'light' ? '#007AFF' : '#0A84FF'; // iOS blue for Save
    const cancelButtonColor = colorScheme === 'light' ? '#DDDDDD' : '#444'; // Light gray in light mode, dark gray in dark mode

    const navigation = useNavigation();
    const route = useRoute();
    // const { alarm, onSave } = route.params;
    const { alarmId } = route.params;
    console.log('Alarm ID:', alarmId);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    // const [alarmName, setAlarmName] = useState(alarm.name); // Alarm name state
    // const [hours, setHours] = useState(alarm.time.hour); // Initial hour
    // const [minutes, setMinutes] = useState(alarm.time.minute); // Initial minutes

    const [alarm, setAlarm] = useState({
        name: '',
        day: 0,
        time: {
            hour: 0,
            minute: 0,
            second: 0
        },
        isOn: true,
    });

    const [apiUrl, setApiUrl] = useState('');

    // Fetch the saved API URL from AsyncStorage when the component is mounted
    useEffect(() => {
        const loadApiUrl = async () => {
            try {
                const savedUrl = await AsyncStorage.getItem('apiUrl');
                if (savedUrl) {
                    setApiUrl(savedUrl);
                }
                console.log('API URL:', apiUrl);
            } catch (error) {
                console.error('Error loading API URL:', error);
            }
        };

        loadApiUrl();
    }, []);

    useEffect(() => {
        // Dynamically hide the header
        navigation.setOptions({
            headerShown: false,
        });
    }, [navigation]);

    // Fetch alarm from the api
    useEffect(() => {
        if (!apiUrl) {
            console.error('API URL is not available');
            return;  // Don't proceed if the API URL is not set
        }
        const fetchAlarm = async () => {
            try {
                const response = await fetch(`http://${apiUrl}/api/alarms/` + alarmId);
                if (!response.ok) {
                    if (response.status === 404) {
                        // If the server responds with a 404 status, use the default alarm
                        console.warn('Alarm not found, using default alarm.');
                        return;
                    } else {
                        // Handle other error statuses
                        throw new Error(`Failed to fetch alarm. Status: ${response.status}`);
                    }
                }
                const alarm = await response.json();
                setAlarm(alarm);

            } catch (error) {
                console.error('Error fetching alarm:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchAlarm();
    }, [apiUrl]);

    const handleSaveChanges = async () => {
        // Validate if all required fields are provided
        const invalidFields = [];
        setAlarm({ ...alarm, isOn: true });

        // Check if any field in alarm is null, undefined, or an empty string
        Object.entries(alarm).forEach(([key, value]) => {
            if (value === null || value === undefined || (typeof value === 'string' && value.trim() === '')) {
                invalidFields.push(key);
            }
        });

        // If there are invalid fields, show the error message
        if (invalidFields.length > 0) {
            setError(`The following fields are required: ${invalidFields.join(', ')}`);
            return;  // Exit the function if any fields are invalid
        }
        console.log('Updated Alarm:', alarm);

        try {
            // Determine the HTTP method and URL based on whether we're editing or creating a new alarm
            const method = alarmId ? 'PUT' : 'POST'; // Use POST for new alarm, PUT for existing alarm
            const endpoint = alarmId
                ? `http://${apiUrl}/api/alarms/${alarmId}`  // Use the alarm ID for existing alarms
                : `http://${apiUrl}/api/alarms`;            // Use the /alarms endpoint for new alarms


            console.log('Alarm Request Body:', JSON.stringify(alarm));

            // Send the updated alarm to the server with a POST request
            const response = await fetch(endpoint, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(alarm), // Send the updated data in the request body
            });

            // Check if the response is successful
            if (!response.ok) {
                console.log(`URL: ${endpoint}`);
                throw new Error(`Failed to ${alarmId ? 'update' : 'create'} alarm`);
            }

            const responseData = await response.json(); // Parse the response as JSON

            // Handle the response from the server if needed
            console.log(`${alarmId ? 'Updated' : 'Created'} Alarm Response:`, responseData);

            navigation.goBack(); // Go back to the previous screen

        } catch (error) {
            setError(`Error ${alarmId ? 'updating' : 'creating'} alarm: ${error.message}`);
            // Handle error (you can show a message or alert to the user)
        }
    };

    // PanResponder for hour adjustment
    const hourResponder = PanResponder.create({
        onStartShouldSetPanResponder: () => true,
        onPanResponderMove: (e, gestureState) => {
            // Swipe up to decrease hour, swipe down to increase hour
            if (gestureState.dy < -20) {
                setAlarm(prevAlarm => ({
                    ...prevAlarm,
                    time: {
                        ...prevAlarm.time,
                        hour: prevAlarm.time.hour === 23 ? 0 : prevAlarm.time.hour + 1
                    }
                })); // Decrease hour
            } else if (gestureState.dy > 20) {
                setAlarm(prevAlarm => ({
                    ...prevAlarm,
                    time: {
                        ...prevAlarm.time,
                        hour: prevAlarm.time.hour === 0 ? 23 : prevAlarm.time.hour - 1
                    }
                })); // Increase hour
            }
        },
    });

    // PanResponder for minute adjustment
    const minuteResponder = PanResponder.create({
        onStartShouldSetPanResponder: () => true,
        onPanResponderMove: (e, gestureState) => {
            // Swipe up to decrease minutes, swipe down to increase minutes
            if (gestureState.dy < -20) {
                setAlarm(prevAlarm => ({
                    ...prevAlarm,
                    time: {
                        ...prevAlarm.time,
                        minute: prevAlarm.time.minute === 59 ? 0 : prevAlarm.time.minute + 1
                    }
                })); // Decrease minutes
            } else if (gestureState.dy > 20) {
                setAlarm(prevAlarm => ({
                    ...prevAlarm,
                    time: {
                        ...prevAlarm.time,
                        minute: prevAlarm.time.minute === 0 ? 59 : prevAlarm.time.minute - 1
                    }
                })); // Increase minutes
            }
        },
    });


    if (loading) {
        return (
            <SafeAreaView style={styles.container}>
                <ThemedText>Loading alarm...</ThemedText>
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView style={styles.container}>
            {/* Display error message if error exists */}
            {error && (
                <View style={styles.errorContainer}>
                    <ThemedText style={styles.errorText}>{error}</ThemedText>
                </View>
            )}


            <ThemedText type='title' style={{ paddingBottom: 10 }}>
                {alarmId ? 'Update' : 'Create'} Alarm
            </ThemedText>

            {/* Alarm Name Input */}
            <View style={styles.alarmNameSection}>
                <ThemedText type="defaultSemiBold" >Alarm Name</ThemedText>
                <ThemedText>
                    <TextInput
                        style={[styles.alarmNameInput, { borderColor: borderColor }, { color: colorScheme === 'light' ? '#000' : '#fff' }]}
                        value={alarm.name}
                        onChangeText={(text) => setAlarm({ ...alarm, name: text })}
                        placeholder="Enter Alarm Name"
                        placeholderTextColor={colorScheme === 'light' ? '#888' : '#ccc'}
                    />
                </ThemedText>

            </View>

            <View style={styles.timePicker}>
                {/* Hour Picker */}
                <View style={[styles.timeSection, { borderColor: borderColor }]} {...hourResponder.panHandlers}>
                    <ThemedText style={styles.timeText}>{String(alarm.time.hour).padStart(2, '0')}</ThemedText>
                </View>

                <ThemedText style={styles.colon}>:</ThemedText>

                {/* Minute Picker */}
                <View style={[styles.timeSection, { borderColor: borderColor }]} {...minuteResponder.panHandlers}>
                    <ThemedText style={styles.timeText}>{String(alarm.time.minute).padStart(2, '0')}</ThemedText>
                </View>

            </View>

            {/* Buttons */}
            <View style={styles.buttonContainer}>
                <TouchableOpacity
                    style={[styles.button, { backgroundColor: cancelButtonColor }]}
                    onPress={() => navigation.goBack()}
                >
                    <ThemedText style={styles.buttonText}>Cancel</ThemedText>
                </TouchableOpacity>
                <TouchableOpacity
                    style={[styles.button, { backgroundColor: saveButtonColor }]}
                    onPress={handleSaveChanges}
                >
                    <ThemedText style={[styles.buttonText, { color: "#FFFFFF" }]}>Save</ThemedText>
                </TouchableOpacity>

            </View>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 20,
    },
    alarmNameSection: {
        width: '100%',
        marginBottom: 25,
    },
    alarmNameInput: {
        borderWidth: 1,
        borderRadius: 8,
        padding: 10,
        width: '100%',
        fontSize: 18,
    },
    timePicker: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    timeSection: {
        height: 100,
        width: 100,
        borderWidth: 1,
        borderRadius: 8,
        marginHorizontal: 10,
        justifyContent: 'center',
        alignItems: 'center',
    },
    timeText: {
        fontSize: 40,
        fontWeight: 'bold',
        textAlign: 'center',
        lineHeight: 50,
    },
    colon: {
        fontSize: 40,
        fontWeight: 'bold',
        alignItems: 'center',
        lineHeight: 50,
    },
    buttonContainer: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        width: '100%',
        marginTop: 30,
    },
    button: {
        flex: 1,
        padding: 15,
        borderRadius: 10,
        alignItems: 'center',
        marginHorizontal: 10,
    },
    buttonText: {
        fontSize: 18,
        fontWeight: 'bold',
    },
    errorContainer: {
        wordWrap: 'break-word',
        backgroundColor: '#f8d7da',
        borderColor: '#f5c6cb',
        borderWidth: 1,
        padding: 10,
        width: '85%',
        marginBottom: 20,
        borderRadius: 5,
        alignContent: 'center',
        justifyContent: 'center',
    },
    errorText: {
        color: 'red',
        fontSize: 16,
        fontWeight: 'bold',
        textAlign: 'center',
    },
});
