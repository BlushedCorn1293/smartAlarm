import { useEffect, useState } from 'react';
import { View, Text, StyleSheet, PanResponder, TextInput, Button, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ThemedText } from '@/components/ThemedText'; // Assuming you have this component
import { useRoute, useNavigation } from '@react-navigation/native';
import { useColorScheme, Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';


export default function EditDeadlineScreen() {
    const colorScheme = useColorScheme();

    const borderColor = colorScheme === 'light' ? '#333' : '#F9F9F9';
    const saveButtonColor = colorScheme === 'light' ? '#007AFF' : '#0A84FF'; // iOS blue for Save
    const cancelButtonColor = colorScheme === 'light' ? '#DDDDDD' : '#444'; // Light gray in light mode, dark gray in dark mode

    const activeBackgroundColor = colorScheme === 'light' ? '#007AFF' : '#0A84FF'; // Active button color
    const defaultBackgroundColor = colorScheme === 'light' ? '#f0f0f0' : '#222'; // Default button color
    const activeTextColor = colorScheme === 'light' ? '#fff' : '#fff'; // Text color for active button
    const defaultTextColor = colorScheme === 'light' ? '#333' : '#ccc'; // Text color for default button

    const navigation = useNavigation();
    const route = useRoute();

    const { deadlineId } = route.params;
    const currentDate = new Date();
    const [deadline, setDeadline] = useState({
        name: '',
        type: '',
        dateTime: {
            year: currentDate.getFullYear(),
            month: currentDate.getMonth() + 1,  // Months are 0-based, so we add 1
            day: currentDate.getDate(),
            hour: 12,
            minute: 0
        },
    });

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

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
    useEffect(() => {
        if (!apiUrl) {
            console.error('API URL is not available');
            return;  // Don't proceed if the API URL is not set
        }
        const fetchDeadline = async () => {
            try {
                const response = await fetch(`http://${apiUrl}/api/deadlines/` + deadlineId);
                if (!response.ok) {
                    if (response.status === 404) {
                        // If the server responds with a 404 status, use the default deadline
                        console.warn('Deadline not found, using default deadline.');
                        return;
                    } else {
                        // Handle other error statuses
                        throw new Error(`Failed to fetch deadline. Status: ${response.status}`);
                    }
                }
                const deadline = await response.json();
                setDeadline(deadline);

            } catch (error) {
                setError(error.message);
            } finally {
                setLoading(false);
            }
        };

        fetchDeadline();
    }, [apiUrl]);

    useEffect(() => {
        // Dynamically hide the header
        navigation.setOptions({
            headerShown: false,
        });
    }, [navigation]);

    const handleSaveChanges = async () => {
        // Validate if all required fields are provided
        const invalidFields = [];

        // Check if any field in deadline is null, undefined, or an empty string
        Object.entries(deadline).forEach(([key, value]) => {
            if (value === null || value === undefined || (typeof value === 'string' && value.trim() === '')) {
                invalidFields.push(key);
            }
        });

        // If there are invalid fields, show the error message
        if (invalidFields.length > 0) {
            setError(`The following fields are required: ${invalidFields.join(', ')}`);
            return;  // Exit the function if any fields are invalid
        }

        console.log('Updated Deadline:', deadline);

        try {
            // Determine the HTTP method and URL based on whether we're editing or creating a new deadline
            const method = deadlineId ? 'PUT' : 'POST'; // Use POST for new deadline, PUT for existing deadline
            const endpoint = deadlineId
                ? `http://${apiUrl}/api/deadlines/${deadlineId}`  // Use the deadline ID for existing deadlines
                : `http://${apiUrl}/api/deadlines`;            // Use the /deadlines endpoint for new deadlines

            // Send the updated deadline to the server with a POST request
            const response = await fetch(endpoint, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(deadline), // Send the updated data in the request body
            });

            // Check if the response is successful
            if (!response.ok) {
                console.log(`URL: ${endpoint}`);
                throw new Error(`Failed to ${deadlineId ? 'update' : 'create'} deadline`);
            }

            const responseData = await response.json(); // Parse the response as JSON

            // Handle the response from the server if needed
            console.log(`${deadlineId ? 'Updated' : 'Created'} Deadline Response:`, responseData);

            navigation.goBack(); // Go back to the previous screen

        } catch (error) {
            setError(`Error ${deadlineId ? 'updating' : 'creating'} deadline: ${error.message}`);
            // Handle error (you can show a message or alert to the user)
        }
    };

    if (loading) {
        return (
            <SafeAreaView style={styles.container}>
                <ThemedText>Loading deadline...</ThemedText>
            </SafeAreaView>
        );
    }

    const hourResponder = PanResponder.create({
        onStartShouldSetPanResponder: () => true,
        onPanResponderMove: (e, gestureState) => {
            // Swipe up to decrease hour, swipe down to increase hour
            if (gestureState.dy < -20) {
                setDeadline(prevDeadline => ({
                    ...prevDeadline,
                    dateTime: {
                        ...prevDeadline.dateTime,
                        hour: prevDeadline.dateTime.hour === 23 ? 0 : prevDeadline.dateTime.hour + 1
                    }
                })); // Decrease hour
            } else if (gestureState.dy > 20) {
                setDeadline(prevDeadline => ({
                    ...prevDeadline,
                    dateTime: {
                        ...prevDeadline.dateTime,
                        hour: prevDeadline.dateTime.hour === 0 ? 23 : prevDeadline.dateTime.hour - 1
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
                setDeadline(prevDeadline => ({
                    ...prevDeadline,
                    dateTime: {
                        ...prevDeadline.dateTime,
                        minute: prevDeadline.dateTime.minute === 59 ? 0 : prevDeadline.dateTime.minute + 1
                    }
                })); // Decrease minutes
            } else if (gestureState.dy > 20) {
                setDeadline(prevDeadline => ({
                    ...prevDeadline,
                    dateTime: {
                        ...prevDeadline.dateTime,
                        minute: prevDeadline.dateTime.minute === 0 ? 59 : prevDeadline.dateTime.minute - 1
                    }
                })); // Increase minutes
            }
        },
    });

    const dayResponder = PanResponder.create({
        onStartShouldSetPanResponder: () => true,
        onPanResponderMove: (e, gestureState) => {
            if (gestureState.dy < -20) {
                setDeadline(prevDeadline => {
                    const daysInMonth = new Date(prevDeadline.dateTime.year, prevDeadline.dateTime.month, 0).getDate(); // Get days in the current month
                    return {
                        ...prevDeadline,
                        dateTime: {
                            ...prevDeadline.dateTime,
                            day: prevDeadline.dateTime.day === daysInMonth ? 1 : prevDeadline.dateTime.day + 1 // Wrap around to 1 after the last day
                        }
                    };
                });
            } else if (gestureState.dy > 20) {
                setDeadline(prevDeadline => {
                    const daysInMonth = new Date(prevDeadline.dateTime.year, prevDeadline.dateTime.month, 0).getDate();
                    return {
                        ...prevDeadline,
                        dateTime: {
                            ...prevDeadline.dateTime,
                            day: prevDeadline.dateTime.day === 1 ? daysInMonth : prevDeadline.dateTime.day - 1 // Wrap around to the last day of the month
                        }
                    };
                });
            }
        },
    });

    const validateDayForMonth = (month, year) => {
        const daysInMonth = new Date(year, month, 0).getDate(); // Get the number of days in the month
        setDeadline(prevDeadline => {
            const adjustedDay = prevDeadline.dateTime.day > daysInMonth ? daysInMonth : prevDeadline.dateTime.day;
            return {
                ...prevDeadline,
                dateTime: {
                    ...prevDeadline.dateTime,
                    day: adjustedDay
                }
            };
        });
    };

    const monthResponder = PanResponder.create({
        onStartShouldSetPanResponder: () => true,
        onPanResponderMove: (e, gestureState) => {
            if (gestureState.dy < -20) {
                setDeadline(prevDeadline => {
                    const newMonth = prevDeadline.dateTime.month === 12 ? 1 : prevDeadline.dateTime.month + 1;
                    validateDayForMonth(newMonth, prevDeadline.dateTime.year); // Validate day
                    return {
                        ...prevDeadline,
                        dateTime: {
                            ...prevDeadline.dateTime,
                            month: newMonth
                        }
                    };
                });
            } else if (gestureState.dy > 20) {
                setDeadline(prevDeadline => {
                    const newMonth = prevDeadline.dateTime.month === 1 ? 12 : prevDeadline.dateTime.month - 1;
                    validateDayForMonth(newMonth, prevDeadline.dateTime.year); // Validate day
                    return {
                        ...prevDeadline,
                        dateTime: {
                            ...prevDeadline.dateTime,
                            month: newMonth
                        }
                    };
                });
            }
        },
    });

    const yearResponder = PanResponder.create({
        onStartShouldSetPanResponder: () => true,
        onPanResponderMove: (e, gestureState) => {
            if (gestureState.dy < -20) {
                setDeadline(prevDeadline => {
                    const newYear = prevDeadline.dateTime.year + 1;
                    validateDayForMonth(prevDeadline.dateTime.month, newYear); // Validate day
                    return {
                        ...prevDeadline,
                        dateTime: {
                            ...prevDeadline.dateTime,
                            year: newYear
                        }
                    };
                });
            } else if (gestureState.dy > 20) {
                setDeadline(prevDeadline => {
                    const newYear = prevDeadline.dateTime.year - 1;
                    validateDayForMonth(prevDeadline.dateTime.month, newYear); // Validate day
                    return {
                        ...prevDeadline,
                        dateTime: {
                            ...prevDeadline.dateTime,
                            year: newYear
                        }
                    };
                });
            }
        },
    });


    return (
        <SafeAreaView style={styles.container}>
            {/* Display error message if error exists */}
            {error && (
                <View style={styles.errorContainer}>
                    <ThemedText style={styles.errorText}>{error}</ThemedText>
                </View>
            )}

            <ThemedText type='title' style={{ paddingBottom: 10 }}>
                {deadlineId ? 'Update' : 'Create'} Deadline
            </ThemedText>{/* Deadline Name Input */}
            <View style={styles.deadlineNameSection}>
                <ThemedText type="defaultSemiBold">Deadline Name</ThemedText>
                <ThemedText>
                    <TextInput
                        style={[styles.deadlineNameInput, { borderColor: colorScheme === 'light' ? '#000' : '#fff' }, { color: colorScheme === 'light' ? '#000' : '#fff' }]}
                        value={deadline.name}
                        onChangeText={(text) => setDeadline({ ...deadline, name: text })}
                        placeholder="Enter Deadline Name"
                        placeholderTextColor={colorScheme === 'light' ? '#888' : '#ccc'}
                    />
                </ThemedText>
            </View>

            <View style={styles.timePicker}>
                {/* Hour Picker */}
                <View style={[styles.timeSection, { borderColor: borderColor }]} {...hourResponder.panHandlers}>
                    <ThemedText style={styles.timeText}>{String(deadline.dateTime.hour).padStart(2, '0')}</ThemedText>
                </View>

                <ThemedText style={styles.colon}>:</ThemedText>

                {/* Minute Picker */}
                <View style={[styles.timeSection, { borderColor: borderColor }]} {...minuteResponder.panHandlers}>
                    <ThemedText style={styles.timeText}>{String(deadline.dateTime.minute).padStart(2, '0')}</ThemedText>
                </View>
            </View>

            <View style={styles.timePicker}>
                {/* Day Picker */}
                <View style={[styles.timeSection, { borderColor: borderColor }]} {...dayResponder.panHandlers}>
                    <ThemedText style={styles.timeText}>{String(deadline.dateTime.day).padStart(2, '0')}</ThemedText>
                </View>

                <View style={[styles.timeSection, { borderColor: borderColor }]} {...monthResponder.panHandlers}>
                    <ThemedText style={styles.timeText}>{String(deadline.dateTime.month).padStart(2, '0')}</ThemedText>
                </View>

                <View style={[styles.timeSection, { borderColor: borderColor }]} {...yearResponder.panHandlers}>
                    <ThemedText style={styles.timeText}>{String(deadline.dateTime.year)}</ThemedText>
                </View>
            </View>

            <View >
                <ThemedText style={styles.label}>Type:</ThemedText>
                <View style={styles.toggleButtonContainer}>
                    <TouchableOpacity
                        style={[
                            styles.toggleButton,
                            {
                                backgroundColor: deadline.type === 'Exam' ? activeBackgroundColor : defaultBackgroundColor,
                                borderColor: borderColor,
                            },
                        ]}
                        onPress={() => setDeadline({ ...deadline, type: 'Exam' })}
                    >
                        <ThemedText
                            style={{
                                color: deadline.type === 'Exam' ? activeTextColor : defaultTextColor,
                            }}
                        >
                            Exam
                        </ThemedText>
                    </TouchableOpacity>
                    <TouchableOpacity
                        style={[
                            styles.toggleButton,
                            {
                                backgroundColor: deadline.type === 'Coursework' ? activeBackgroundColor : defaultBackgroundColor,
                                borderColor: borderColor,
                            },
                        ]}
                        onPress={() => setDeadline({ ...deadline, type: 'Coursework' })}
                    >
                        <ThemedText
                            style={{
                                color: deadline.type === 'Coursework' ? activeTextColor : defaultTextColor,
                            }}
                        >
                            Coursework
                        </ThemedText>
                    </TouchableOpacity>
                </View>
            </View>

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
};


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
    },
    deadlineNameInput: {
        borderWidth: 1,
        borderRadius: 8,
        padding: 10,
        width: '100%',
        fontSize: 18,
    },
    timePicker: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingBottom: 20,
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
        backgroundColor: '#007AFF',
        borderRadius: 10,
    },
    toggleButtonContainer: {
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
        marginVertical: 10,
    },
    toggleButton: {
        padding: 10,
        borderWidth: 1,
        borderRadius: 5,
        marginHorizontal: 5,
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
