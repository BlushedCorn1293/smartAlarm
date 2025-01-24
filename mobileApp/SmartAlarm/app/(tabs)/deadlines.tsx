import { View, Text, StyleSheet, FlatList, TouchableOpacity, Switch } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ThemedText } from '@/components/ThemedText';
import { useFocusEffect, useNavigation } from '@react-navigation/native'; // Import hooks
import { useColorScheme } from 'react-native';
import { useState, useEffect, useRef } from 'react';
import React from 'react';
import { IconSymbol } from '@/components/ui/IconSymbol';

import AsyncStorage from '@react-native-async-storage/async-storage';
// import { useApi } from '../context/ApiContext';

// /home/kavan/Code_Personal_Projects/SmartAlarm/context/ApiContext.js
export default function DeadlinesScreen() {

    // const { apiUrl } =? route?.params || {};
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

    const examColor = colorScheme === 'light' ? '#FF7F7F' : '#B22222'; // LightSalmonRed for light mode, FireBrick for dark mode
    const courseworkColor = colorScheme === 'light' ? '#6CA6CD' : '#1E3A8A'; // SkyBlue for light mode, Darker Blue for dark mode

    const [deadlines, setDeadlines] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedDeadlines, setSelectedDeadlines] = useState(new Set()); // Store selected deadlines
    const [isSelectionMode, setIsSelectionMode] = useState(false); // Track if we're in selection mode


    // Fetch deadlines from the API
    const fetchDeadlines = async () => {
        setError(null); // Clear any existing errors
        if (!apiUrl) {
            console.error('API URL is not available');
            return;  // Don't proceed if the API URL is not set
        }
        try {
            const response = await fetch(`http://${apiUrl}/api/deadlines`);
            if (!response.ok) {
                throw new Error('Failed to fetch deadlines');
            }
            const data = await response.json();
            // Sort deadlines by date
            const sortedDeadlines = data.deadlines.sort((a, b) => {
                const dateA = new Date(a.dateTime.year, a.dateTime.month - 1, a.dateTime.day, a.dateTime.hour, a.dateTime.minute, a.dateTime.second || 0);
                const dateB = new Date(b.dateTime.year, b.dateTime.month - 1, b.dateTime.day, b.dateTime.hour, b.dateTime.minute, b.dateTime.second || 0);
                return dateA - dateB;
            });
            setDeadlines(sortedDeadlines);
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    useFocusEffect(
        React.useCallback(() => {
            // Re-fetch deadlines when coming back to this screen
            fetchDeadlines();
        }, [apiUrl]) // Add apiUrl as a dependency so it refetches when apiUrl changes
    );

    if (loading) {
        return (
            <SafeAreaView style={styles.container}>
                <ThemedText>Loading deadlines...</ThemedText>
            </SafeAreaView>
        );
    }

    const handleDeadlineLongPress = (id) => {
        // Toggle selection mode on long press
        setIsSelectionMode(true);
        setSelectedDeadlines((prevSelectedDeadlines) => {
            const newSelectedDeadlines = new Set(prevSelectedDeadlines);
            if (newSelectedDeadlines.has(id)) {
                newSelectedDeadlines.delete(id);
            } else {
                newSelectedDeadlines.add(id);
            }
            return newSelectedDeadlines;
        });
    };

    const handleDeadlinePress = (id) => {
        if (isSelectionMode) {
            setSelectedDeadlines((prevSelectedDeadlines) => {
                const newSelectedDeadlines = new Set(prevSelectedDeadlines);
                if (newSelectedDeadlines.has(id)) {
                    newSelectedDeadlines.delete(id);
                } else {
                    newSelectedDeadlines.add(id);
                }
                return newSelectedDeadlines;
            });
        } else {
            navigation.navigate('details/deadlineDetail', { deadlineId: id });
        }
    };
    const deleteSelectedDeadlines = async () => {
        try {
            for (const deadlineId of selectedDeadlines) {
                const response = await fetch(`http://${apiUrl}/api/deadlines/${deadlineId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                if (!response.ok) {
                    console.log(`Failed to delete deadline ${deadlineId}`);
                    continue;
                }

                const responseData = await response.json();
                console.log(`Deleted deadline ${deadlineId}:`, responseData);
            }

            fetchDeadlines();
            setSelectedDeadlines(new Set());
            setIsSelectionMode(false); // Exit selection mode after deleting
        } catch (error) {
            console.error('Error deleting deadlines:', error);
        }
    };

    const cancelDeleteMode = () => {
        setIsSelectionMode(false);
        setSelectedDeadlines(new Set()); // Deselect all deadlines
    };

    const renderDeadline = ({ item }) => (
        <TouchableOpacity
            onPress={() => handleDeadlinePress(item.id)}
            onLongPress={() => handleDeadlineLongPress(item.id)}
        >
            <View
                style={[
                    styles.deadlineItem,
                    { backgroundColor: item.type === 'Exam' ? examColor : courseworkColor }
                ]}
            >

                {isSelectionMode && (
                    <TouchableOpacity
                        onPress={() => handleDeadlinePress(item.id)}
                        style={{ paddingRight: 15 }}>
                        <IconSymbol
                            name={selectedDeadlines.has(item.id) ? 'check.fill' : 'check.empty'}
                            size={32}
                            color={colorScheme === 'dark' ? '#F9F9F9' : '#333'} />
                    </TouchableOpacity>
                )}

                <View style={styles.deadlineDetails}>
                    <ThemedText style={styles.deadlineName}>{item.name}</ThemedText>
                    <ThemedText style={styles.deadlineDeadline}>
                        {item.dateTime.day.toString()} {new Date(item.dateTime.year, item.dateTime.month - 1).toLocaleString('default', { month: 'short' })}
                        {item.type === 'Exam' ? " (EX)" : " (CW)"}
                    </ThemedText>
                </View>
            </View >
        </TouchableOpacity >
    );

    return (
        <SafeAreaView style={styles.container}>
            <ThemedText type='title'>Deadlines</ThemedText>
            {/* Display error message if error exists */}
            {error && (
                <View style={styles.errorContainer}>
                    <ThemedText style={styles.errorText}>{error}</ThemedText>
                </View>
            )}

            <FlatList
                data={deadlines}
                renderItem={renderDeadline}
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
                        onPress={deleteSelectedDeadlines}
                    >
                        <IconSymbol name="trash" size={64} color="#FFF" />
                    </TouchableOpacity>
                </>
            )}

            {!isSelectionMode && (
                // Floating Plus Button
                <TouchableOpacity
                    style={[
                        styles.floatingButton,
                        { backgroundColor: colorScheme === 'dark' ? '#007AFF' : '#FFF' }, // Dynamic background color
                    ]}
                    onPress={() => navigation.navigate('details/editDetails/editDeadline',
                        { deadlineId: null } // Pass null to create a new alarm
                    )} // Navigate to the create deadline screen
                >
                    <IconSymbol name="add.circle" size={64} color={colorScheme === 'dark' ? '#FFF' : '#007AFF'} />
                </TouchableOpacity>
            )}
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 20
    },
    deadlineItem: {
        flexDirection: 'row',
        alignItems: 'center',
        padding: 15,
        marginVertical: 5,
        borderRadius: 10,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 5,
        elevation: 3
    },
    deadlineDetails: {
        flexDirection: 'column'
    },
    deadlineName: {
        fontSize: 18,
        fontWeight: 'bold'
    },
    deadlineDeadline: {
        fontSize: 16,
    },
    switch: {
        marginLeft: 10
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