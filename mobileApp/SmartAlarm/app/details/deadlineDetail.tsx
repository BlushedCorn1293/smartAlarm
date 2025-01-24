import { useEffect, useState, useCallback } from 'react';
import { View, Text, StyleSheet, PanResponder, TextInput, Button, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ThemedText } from '@/components/ThemedText'; // Assuming you have this component
import { useRoute, useNavigation, useFocusEffect } from '@react-navigation/native';
import { useColorScheme, Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

import React from 'react';

export default function DeadlineDetailScreen() {
    const colorScheme = useColorScheme();

    const labelColor = colorScheme === 'light' ? '#666' : '#CCC'; // Light gray for light mode, lighter gray for dark mode
    const cancelButtonColor = colorScheme === 'light' ? '#DDDDDD' : '#444'; // Light gray in light mode, dark gray in dark mode

    const navigation = useNavigation();
    const route = useRoute();

    const { deadlineId } = route.params;
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const [deadlineName, setDeadlineName] = useState(''); // Deadline name state
    const [deadlineType, setDeadlineType] = useState(''); // Deadline type state
    const [year, setYear] = useState(0); // Initial year
    const [month, setMonth] = useState(0); // Initial month
    const [day, setDay] = useState(0); // Initial day
    const [hour, setHour] = useState(0); // Initial hour
    const [minute, setMinute] = useState(0); // Initial minute

    const [daysUntilDeadline, setDaysUntilDeadline] = useState(0);
    const [hoursUntilDeadline, setHoursUntilDeadline] = useState(0);
    const [minutesUntilDeadline, setMinutesUntilDeadline] = useState(0);
    const [secondsUntilDeadline, setSecondsUntilDeadline] = useState(0);

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

    // Fetch deadline from the API
    const fetchDeadline = async () => {
        if (!apiUrl) {
            console.error('API URL is not available');
            return;  // Don't proceed if the API URL is not set
        }
        try {
            const response = await fetch(`http://${apiUrl}/api/deadlines/` + deadlineId);
            if (!response.ok) {
                throw new Error('Failed to fetch deadline');
            }
            const deadline = await response.json();
            setDeadlineName(deadline.name);
            setDeadlineType(deadline.type);
            setYear(deadline.dateTime.year);
            setMonth(deadline.dateTime.month);
            setDay(deadline.dateTime.day);
            setHour(deadline.dateTime.hour);
            setMinute(deadline.dateTime.minute);
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    useFocusEffect(
        React.useCallback(() => {
            // Re-fetch deadlines when coming back to this screen
            fetchDeadline();
        }, [apiUrl]) // Add apiUrl as a dependency so it refetches when apiUrl changes
    );

    useEffect(() => {
        if (loading) {
            return;
        }
        const MILLISECONDS_IN_A_DAY = 1000 * 3600 * 24;
        const MILLISECONDS_IN_AN_HOUR = 1000 * 3600;
        const MILLISECONDS_IN_A_MINUTE = 1000 * 60;
        const MILLISECONDS_IN_A_SECOND = 1000;

        const updateCountdown = () => {
            const deadlineDate = new Date(year, month - 1, day, hour, minute);
            const currentDate = new Date();
            const timeDifference = deadlineDate.getTime() - currentDate.getTime();

            // Calculate remaining time
            const daysUntilDeadline = Math.floor(timeDifference / MILLISECONDS_IN_A_DAY);
            const hoursUntilDeadline = Math.floor((timeDifference % MILLISECONDS_IN_A_DAY) / MILLISECONDS_IN_AN_HOUR);
            const minutesUntilDeadline = Math.floor((timeDifference % MILLISECONDS_IN_AN_HOUR) / MILLISECONDS_IN_A_MINUTE);
            const secondsUntilDeadline = Math.floor((timeDifference % MILLISECONDS_IN_A_MINUTE) / MILLISECONDS_IN_A_SECOND);

            // Update state
            setDaysUntilDeadline(daysUntilDeadline);
            setHoursUntilDeadline(hoursUntilDeadline);
            setMinutesUntilDeadline(minutesUntilDeadline);
            setSecondsUntilDeadline(secondsUntilDeadline);
        };

        // Update countdown immediately and set interval for real-time updates
        updateCountdown();
        const intervalId = setInterval(updateCountdown, 1000);

        // Cleanup interval on component unmount
        return () => clearInterval(intervalId);
    }, [year, month, day, hour, minute]);


    useEffect(() => {
        // Dynamically hide the header
        navigation.setOptions({
            headerShown: false,
        });
    }, [navigation]);

    const handleEdit = () => {
        navigation.navigate('details/editDetails/editDeadline', {
            deadlineId
        });
    };

    if (loading) {
        return (
            <SafeAreaView style={styles.container}>
                <ThemedText>Loading deadline...</ThemedText>
            </SafeAreaView>
        );
    }

    if (error) {
        return (
            <SafeAreaView style={styles.container}>
                <ThemedText style={styles.errorText}>Error: {error}</ThemedText>
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView style={styles.container}>
            <ThemedText type="title" style={{ paddingBottom: 10 }}>Deadline</ThemedText>
            <View style={styles.deadlineNameSection}>
                <ThemedText style={[styles.text, { color: labelColor }]}>Title:</ThemedText>
                <ThemedText style={styles.text}>{deadlineName}</ThemedText>

                <ThemedText style={[styles.text, { color: labelColor }]}>Type:</ThemedText>
                <ThemedText style={styles.text}>{deadlineType}</ThemedText>

                <ThemedText style={[styles.text, { color: labelColor }]}>Date:</ThemedText>
                <ThemedText style={styles.text}>{`${day}/${month}/${year}`}</ThemedText>

                <ThemedText style={[styles.text, { color: labelColor }]}>Time:</ThemedText>
                <ThemedText style={styles.text}>{`${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`}</ThemedText>
            </View>
            <View style={styles.countdownContainer}>
                <View style={styles.countdownItem}>
                    <ThemedText style={styles.countdownValue}>{daysUntilDeadline}</ThemedText>
                    <ThemedText style={[styles.countdownLabel, { color: labelColor }]}>Days</ThemedText>
                </View>
                <View style={styles.countdownItem}>
                    <ThemedText style={styles.countdownValue}>{hoursUntilDeadline}</ThemedText>
                    <ThemedText style={[styles.countdownLabel, { color: labelColor }]}>Hours</ThemedText>
                </View>
                <View style={styles.countdownItem}>
                    <ThemedText style={styles.countdownValue}>{minutesUntilDeadline}</ThemedText>
                    <ThemedText style={[styles.countdownLabel, { color: labelColor }]}>Minutes</ThemedText>
                </View>
                <View style={styles.countdownItem}>
                    <ThemedText style={styles.countdownValue}>{secondsUntilDeadline}</ThemedText>
                    <ThemedText style={[styles.countdownLabel, { color: labelColor }]}>Seconds</ThemedText>
                </View>
            </View>

            <View style={styles.buttonContainer}>
                <TouchableOpacity style={[styles.button, { backgroundColor: cancelButtonColor }]} onPress={navigation.goBack}>
                    <ThemedText>Back</ThemedText>
                </TouchableOpacity>
                <TouchableOpacity style={[styles.button, { backgroundColor: cancelButtonColor }]} onPress={handleEdit}>
                    <ThemedText>Edit</ThemedText>
                </TouchableOpacity>
            </View>
        </SafeAreaView >
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 20,
    },
    deadlineNameSection: {
        width: '100%',
        marginBottom: 25,
        paddingHorizontal: 15,
    },
    text: {
        fontSize: 16,
        marginBottom: 5,
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
    editButton: {
        marginTop: 20,
        padding: 15,
        borderRadius: 10,
    },
    countdownContainer: {
        flexDirection: 'row', // Align items in a row
        justifyContent: 'space-around', // Evenly distribute items with space around
        alignItems: 'center', // Center items vertically
        marginVertical: 20, // Add some spacing above and below
    },
    countdownItem: {
        alignItems: 'center', // Center each item (value and label)
        marginHorizontal: 10, // Space between each countdown item
    },
    countdownValue: {
        fontSize: 32, // Larger font for countdown values
        fontWeight: 'bold', // Bold to emphasize numbers
        lineHeight: 36,
    },
    countdownLabel: {
        fontSize: 16, // Smaller font for labels
    },
});
