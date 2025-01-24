import { Text, TouchableOpacity, View, StyleSheet, TextInput, useColorScheme, Button } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { ThemedText } from "@/components/ThemedText";
import { Image } from 'expo-image';
import { useEffect, useRef, useState } from "react";
import AsyncStorage from '@react-native-async-storage/async-storage';
// import { useApi } from '../context/ApiContext';
import { useFocusEffect } from '@react-navigation/native';
import React from "react";

export default function SettingsScreen() {
    const colorScheme = useColorScheme();

    const [apiUrl, setApiUrl] = useState('');
    const [draftApiUrl, setDraftApiUrl] = useState(''); // Temporary state for input

    const apiUrlRef = useRef(apiUrl);

    const [temperature, setTemperature] = useState(null);
    const [voltage, setVoltage] = useState(null);
    const [memoryUsage, setMemoryUsage] = useState(null);
    const [uptime, setUptime] = useState(null);
    // const [environment, setEnvironment] = useState(null);
    const [loading, setLoading] = useState(true);
    const [errors, setErrors] = useState({
        temperature: null,
        voltage: null,
        memoryUsage: null,
        uptime: null,
        // environment: null,
    });

    // Fetch from the API
    const fetchData = async () => {
        const fetchTemperature = async () => {
            try {
                const response = await fetch(`http://${apiUrlRef.current}/api/temperature`);
                if (!response.ok) throw new Error('Failed to fetch temperature');
                const data = await response.json();
                setTemperature(data.temperature);
            } catch (err) {
                setErrors(prev => ({ ...prev, temperature: err.message }));
            }
        };

        const fetchVoltage = async () => {
            try {
                const response = await fetch(`http://${apiUrlRef.current}/api/voltage`);
                if (!response.ok) throw new Error('Failed to fetch voltage');
                const data = await response.json();
                setVoltage(data.voltage);
            } catch (err) {
                setErrors(prev => ({ ...prev, voltage: err.message }));
            }
        };

        const fetchMemoryUsage = async () => {
            try {
                const response = await fetch(`http://${apiUrlRef.current}/api/memory_usage`);
                if (!response.ok) throw new Error('Failed to fetch memory usage');
                const data = await response.json();
                setMemoryUsage(data);
            } catch (err) {
                setErrors(prev => ({ ...prev, memoryUsage: err.message }));
            }
        };

        const fetchUptime = async () => {
            try {
                const response = await fetch(`http://${apiUrlRef.current}/api/uptime`);

                if (!response.ok) throw new Error('Failed to fetch uptime');
                const data = await response.json();
                setUptime(data.uptime_seconds);
                if (data.uptime_seconds !== null) {
                    const hours = Math.floor(data.uptime_seconds / 3600);
                    const minutes = Math.floor((data.uptime_seconds % 3600) / 60);
                    const seconds = data.uptime_seconds % 60;
                    setUptime(`${hours}h ${minutes}m ${seconds}s`);
                }
            } catch (err) {
                setErrors(prev => ({ ...prev, uptime: err.message }));
            }
        };

        // const fetchEnvironment = async () => {
        //     try {
        //         const response = await fetch(`http://${apiUrl}/api/environment`);
        //         if (!response.ok) throw new Error('Failed to fetch environment');
        //         const data = await response.json();
        //         setEnvironment(data);
        //     } catch (err) {
        //         setErrors(prev => ({ ...prev, environment: err.message }));
        //     }
        // };

        // Fetch all data
        await fetchTemperature();
        await fetchVoltage();
        await fetchMemoryUsage();
        await fetchUptime();
        // fetchEnvironment();

        setLoading(false);
    };

    // Use useFocusEffect to call fetchData only when the page is focused
    useFocusEffect(
        React.useCallback(() => {
            // Fetch initial data when screen is focused
            fetchData();

            // Set interval to refresh every second (1000ms)
            const intervalId = setInterval(() => {
                fetchData();
            }, 1000);

            // Cleanup the interval when the component is unfocused
            return () => clearInterval(intervalId);
        }, [apiUrl]) // Only trigger this effect when the apiUrl changes
    );


    // Fetch the saved API URL from AsyncStorage when the component is mounted
    useEffect(() => {
        const loadApiUrl = async () => {
            try {
                const savedUrl = await AsyncStorage.getItem('apiUrl');
                if (savedUrl) {
                    setApiUrl(savedUrl);
                    setDraftApiUrl(savedUrl);
                }
            } catch (error) {
                console.error('Error loading API URL:', error);
            }
        };

        loadApiUrl();
    }, []);

    // Save API URL to AsyncStorage
    const saveApiUrl = async () => {
        try {
            await AsyncStorage.setItem('apiUrl', draftApiUrl);
            setApiUrl(draftApiUrl);
            alert('API URL saved!');
        } catch (error) {
            console.error('Error saving API URL:', error);
        }
    };

    useEffect(() => {
        apiUrlRef.current = apiUrl;
        setTemperature(null);
        setVoltage(null);
        setMemoryUsage(null);
        setUptime(null);
    }, [apiUrl]);

    return (
        <SafeAreaView style={styles.container}>
            <ThemedText type="title">Settings</ThemedText>
            <View style={styles.urlInput}>
                <ThemedText type="defaultSemiBold">Pico IP address</ThemedText>

                <ThemedText>
                    <TextInput
                        style={[styles.urlInput, { borderColor: colorScheme === 'light' ? '#000' : '#fff' }, { color: colorScheme === 'light' ? '#000' : '#fff' }]}
                        value={draftApiUrl}
                        onChangeText={setDraftApiUrl}
                        placeholder={apiUrl === '' ? "Enter IP address where API is hosted" : apiUrl}
                        placeholderTextColor={colorScheme === 'light' ? '#888' : '#ccc'}
                    />
                </ThemedText>
                <TouchableOpacity
                    onPress={() => saveApiUrl()}
                >
                    <ThemedText>Save</ThemedText>
                </TouchableOpacity>
            </View>

            {loading ? (
                <ThemedText>Loading data...</ThemedText>
            ) : (
                <View>
                    <ThemedText>CPU Temperature: {temperature !== null ? `${temperature}°C` : errors.temperature || 'Loading...'}</ThemedText>
                    <ThemedText>System Voltage: {voltage !== null ? `${voltage} V` : errors.voltage || 'Loading...'}</ThemedText>
                    <ThemedText>Free Memory: {memoryUsage?.free_memory !== null ? `${memoryUsage?.free_memory} bytes` : errors.memoryUsage || 'Loading...'}</ThemedText>
                    <ThemedText>Total Memory: {memoryUsage?.total_memory !== null ? `${memoryUsage?.total_memory} bytes` : errors.memoryUsage || 'Loading...'}</ThemedText>
                    <ThemedText>System Uptime: {uptime !== null ? `${uptime}` : errors.uptime || 'Loading...'}</ThemedText>
                    {/* <ThemedText>Environment: {environment !== null ? `${environment}°C, ${environment}%` : errors.environment || 'Loading...'}</ThemedText> */}
                </View>
            )}

            <Image source="settingsIcon.png" />
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
    urlInput: {
        borderWidth: 1,
        borderRadius: 8,
        padding: 10,
        width: '100%',
        fontSize: 18,
    },
});
