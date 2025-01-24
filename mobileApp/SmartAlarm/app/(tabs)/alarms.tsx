import { ThemedText } from '@/components/ThemedText';
import { View, Text, StyleSheet, FlatList, Switch, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import React, { useEffect, useState } from 'react';
import { useColorScheme } from 'react-native';
import { useNavigation, useFocusEffect } from '@react-navigation/native'; // Import hooks
import AsyncStorage from '@react-native-async-storage/async-storage';
import { IconSymbol } from '@/components/ui/IconSymbol';

export default function AlarmScreen() {

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

    // Log the updated apiUrl whenever it changes
    useEffect(() => {
        if (apiUrl) {
            console.log('Updated API URL:', apiUrl);
        }
    }, [apiUrl]); // Dependency array ensures this runs whenever `apiUrl` changes

    const colorScheme = useColorScheme();
    const navigation = useNavigation();
    const [selectedAlarms, setSelectedAlarms] = useState(new Set()); // Store selected alarms
    const [isSelectionMode, setIsSelectionMode] = useState(false); // Track if we're in selection mode

    const [alarms, setAlarms] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const toggleAlarm = (id) => {
        const updatedAlarms = alarms.map((alarm) =>
            alarm.id === id ? { ...alarm, isOn: !alarm.isOn } : alarm
        );
        setAlarms(updatedAlarms);
        handleAlarmToggle(id, updatedAlarms.find((alarm) => alarm.id === id));
    };

    const handleAlarmToggle = async (alarmId, updatedAlarm) => {
        console.log('Updated Alarm:', updatedAlarm);

        try {
            // Send the updated alarm to the server with a POST request
            const response = await fetch(`http://${apiUrl}/api/alarms/${alarmId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updatedAlarm), // Send the updated data in the request body
            });

            // Check if the response is successful
            if (!response.ok) {
                console.log(`URL: http://${apiUrl}/api/alarms/${alarmId}`);
                throw new Error('Failed to update alarm');
            }

            const responseData = await response.json(); // Parse the response as JSON

            // Handle the response from the server if needed
            console.log('Server Response:', responseData);

        } catch (error) {
            console.error('Error updating alarm:', error);
            // Handle error (you can show a message or alert to the user)
        }
    };

    // Fetch alarms from the API
    const fetchAlarms = async () => {
        setError(null); // Clear any existing errors
        if (!apiUrl) {
            console.error('API URL is not available');
            return;  // Don't proceed if the API URL is not set
        }
        try {
            const response = await fetch(`http://${apiUrl}/api/alarms`);
            if (!response.ok) {
                throw new Error('Failed to fetch alarms');
            }
            const data = await response.json();

            // Sort alarms by time
            const sortedAlarms = data.alarms.sort((a, b) => {
                const timeA = `${a.time.hour.toString().padStart(2, '0')}${a.time.minute.toString().padStart(2, '0')}${a.time.second.toString().padStart(2, '0')}`;
                const timeB = `${b.time.hour.toString().padStart(2, '0')}${b.time.minute.toString().padStart(2, '0')}${b.time.second.toString().padStart(2, '0')}`;
                return timeA - timeB;
            });
            setAlarms(sortedAlarms);
        } catch (error) {
            setError(error.message);
        }
        finally {
            setLoading(false);
        }
    };

    useFocusEffect(
        React.useCallback(() => {
            // Re-fetch alarms when coming back to this screen
            fetchAlarms();
        }, [apiUrl]) // Add apiUrl as a dependency so it refetches when apiUrl changes
    );


    if (loading) {
        return (
            <SafeAreaView style={styles.container}>
                <ThemedText>Loading alarms...</ThemedText>
            </SafeAreaView>
        );
    }



    const handleAlarmLongPress = (id) => {
        // Toggle selection mode on long press
        setIsSelectionMode(true);
        setSelectedAlarms((prevSelectedAlarms) => {
            const newSelectedAlarms = new Set(prevSelectedAlarms);
            if (newSelectedAlarms.has(id)) {
                newSelectedAlarms.delete(id);
            } else {
                newSelectedAlarms.add(id);
            }
            return newSelectedAlarms;
        });
    };

    const handleAlarmPress = (id) => {
        if (isSelectionMode) {
            setSelectedAlarms((prevSelectedAlarms) => {
                const newSelectedAlarms = new Set(prevSelectedAlarms);
                if (newSelectedAlarms.has(id)) {
                    newSelectedAlarms.delete(id);
                } else {
                    newSelectedAlarms.add(id);
                }
                return newSelectedAlarms;
            });
        } else {
            navigation.navigate('details/alarmDetail', { alarmId: id });
        }
    };

    const deleteSelectedAlarms = async () => {
        try {
            for (const alarmId of selectedAlarms) {
                const response = await fetch(`http://${apiUrl}/api/alarms/${alarmId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                if (!response.ok) {
                    console.log(`Failed to delete alarm ${alarmId}`);
                    continue;
                }

                const responseData = await response.json();
                console.log(`Deleted alarm ${alarmId}:`, responseData);
            }

            fetchAlarms();
            setSelectedAlarms(new Set());
            setIsSelectionMode(false); // Exit selection mode after deleting
        } catch (error) {
            console.error('Error deleting alarms:', error);
        }
    };

    const cancelDeleteMode = () => {
        setIsSelectionMode(false);
        setSelectedAlarms(new Set()); // Deselect all alarms
    };

    const renderAlarm = ({ item }) => (
        <TouchableOpacity
            onPress={() => handleAlarmPress(item.id)}
            onLongPress={() => handleAlarmLongPress(item.id)}
        >
            <View
                style={[
                    styles.alarmItem,
                    { backgroundColor: colorScheme === 'dark' ? '#333' : '#F9F9F9' },
                ]}
            >
                {isSelectionMode && (
                    <TouchableOpacity
                        onPress={() => handleAlarmPress(item.id)}
                        style={{ paddingRight: 15 }}>
                        <IconSymbol
                            name={selectedAlarms.has(item.id) ? 'check.fill' : 'check.empty'}
                            size={32}
                            color={colorScheme === 'dark' ? '#F9F9F9' : '#333'} />
                    </TouchableOpacity>
                )}

                <View style={styles.alarmDetails}>
                    <ThemedText style={styles.alarmName}>{item.name}</ThemedText>
                    <ThemedText style={styles.alarmTime}>
                        {item.time.hour.toString().padStart(2, '0')}:
                        {item.time.minute.toString().padStart(2, '0')}
                    </ThemedText>
                </View>


                {!isSelectionMode && (
                    <Switch
                        value={item.isOn}
                        onValueChange={() => toggleAlarm(item.id)}
                        style={styles.switch}
                    />
                )}
            </View>
        </TouchableOpacity>
    );
    return (
        <SafeAreaView style={styles.container}>
            <ThemedText type="title">Alarms</ThemedText>
            {/* Display error message if error exists */}
            {error && (
                <View style={styles.errorContainer}>
                    <ThemedText style={styles.errorText}>{error}</ThemedText>
                </View>
            )}

            <FlatList
                data={alarms}
                renderItem={renderAlarm}
                keyExtractor={(item) => item.id}
            />

            {isSelectionMode && (
                <>
                    {/*  Cancel button */}
                    <TouchableOpacity
                        style={[
                            styles.floatingButton,
                            {
                                backgroundColor: colorScheme === 'dark' ? '#ccc' : '#bbb',
                            },
                        ]}
                        onPress={cancelDeleteMode}
                    >
                        <IconSymbol name="close" size={64} color="#FFF" />
                    </TouchableOpacity>

                    {/*  Delete button */}
                    <TouchableOpacity
                        style={[
                            styles.floatingButton,
                            {
                                backgroundColor: colorScheme === 'dark' ? '#FF4C4C' : '#FF6347',
                                right: 100,
                            },
                        ]}
                        onPress={deleteSelectedAlarms}
                    >
                        <IconSymbol name="trash" size={64} color="#FFF" />
                    </TouchableOpacity>
                </>
            )}


            {!isSelectionMode && (
                // Floating button to create a new alarm
                < TouchableOpacity
                    style={[
                        styles.floatingButton,
                        {
                            backgroundColor: colorScheme === 'dark' ? '#007AFF' : '#FFF',
                            right: 100
                        }, // Dynamic background color
                    ]}
                    onPress={() => navigation.navigate('details/alarmDetail',
                        { alarmId: null } // Pass null to create a new alarm
                    )} // Navigate to the create alarm screen
                >
                    <IconSymbol name="add.circle" size={64} color={colorScheme === 'dark' ? '#FFF' : '#007AFF'} />
                </TouchableOpacity>
            )}
        </SafeAreaView >
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 20
    },
    alarmItem: {
        padding: 15,
        paddingRight: 20,
        marginVertical: 10,
        borderRadius: 8,
        width: '100%',
        alignItems: 'center',
        flexDirection: 'row',
        justifyContent: 'space-between'
    },
    alarmDetails: {
        flex: 1,
        justifyContent: 'center'
    },
    alarmName: {
        fontSize: 18,
        fontWeight: 'bold'
    },
    alarmTime: {
        fontSize: 16,
        color: '#888'
    },
    switch: {
        transform: [{ scaleX: 1.1 }, { scaleY: 1.1 }]
    },
    floatingButton: {
        position: 'absolute',
        bottom: 20,
        right: 20,
        zIndex: 10,
        width: 64, // Set the width
        height: 64, // Set the height
        borderRadius: 32, // Make it circular
        justifyContent: 'center', // Center the icon
        alignItems: 'center', // Center the icon
        shadowColor: '#000', // Optional shadow for elevation
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.25,
        shadowRadius: 4,
        elevation: 10, // Shadow for Android
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
