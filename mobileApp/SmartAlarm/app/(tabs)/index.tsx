import { Text, View, StyleSheet, Pressable, FlatList, useColorScheme, AppRegistry } from "react-native";
import { Link } from 'expo-router'
import { SafeAreaView } from "react-native-safe-area-context";
import { ThemedText } from "@/components/ThemedText";
import { StatusBar } from 'expo-status-bar';
import { IconSymbol } from '@/components/ui/IconSymbol';
import { Colors } from '@/constants/Colors';
import React from "react";
import { useEffect, useState } from "react";
import { ScreenContainer } from "react-native-screens";
import { ApiProvider } from "../context/ApiContext";
import Navigation from "../navigation";
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useFocusEffect } from '@react-navigation/native';

export default function Index() {
  const colorScheme = useColorScheme();

  const buttonIconSize = 80;
  const [isConnected, setIsConnected] = useState(false); // New state for connection status

  // Data array for buttons
  const DATA = [
    { id: '1', title: 'Deadlines', href: '/deadlines', style: styles.deadlineButton, icon: 'calendar.fill' },
    { id: '2', title: 'Settings', href: '/settings', style: styles.settingsButton, icon: 'settings.fill' },
    { id: '3', title: 'Alarms', href: '/alarms', style: styles.alarmsButton, icon: 'alarm.fill' },
    { id: '4', title: 'Sync', href: '/sync', style: styles.syncButton, icon: 'sync.fill' },
  ];

  const iconColor = colorScheme === 'light' ? '#696969' : '#000000'; // Dark grey for light mode and black for dark mode

  const renderItem = ({ item }) => (
    <Link href={item.href}>
      <View style={[styles.button, item.style]}>
        <IconSymbol size={buttonIconSize} name={item.icon} color={iconColor} />
      </View>
    </Link>
  );

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

  // Function to test the response from the /api route
  const testApiResponse = async () => {
    if (!apiUrl) return;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000); // Timeout after 2 seconds

    try {
      const response = await fetch(`http://${apiUrl}/api`, { signal: controller.signal });

      clearTimeout(timeoutId);
      if (response.ok) {
        setIsConnected(true); // Set connected if the API responds successfully
      } else {
        setIsConnected(false);
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        console.error('Fetch request timed out');
      } else {
        console.error('Fetch error:', error);
      }
      setIsConnected(false); // Set not connected if there’s an error
    }
  };

  // Using useFocusEffect to run testApiResponse only when the page is in focus
  useFocusEffect(
    React.useCallback(() => {
      if (apiUrl) {
        const intervalId = setInterval(() => {
          testApiResponse();
        }, 2500);

        // Clear the interval when the page is unfocused
        return () => clearInterval(intervalId);
      }
    }, [apiUrl]) // Only run when apiUrl changes
  );
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="auto" />
      <ThemedText type="title">Home Page</ThemedText>

      <FlatList
        data={DATA}
        renderItem={renderItem}
        keyExtractor={item => item.id}
        numColumns={2} // Set number of columns to 2 for grid layout
        columnWrapperStyle={styles.row} // Apply styles to each row
        contentContainerStyle={styles.contentContainer}
      />

      {/* Display the connection status */}
      <View style={[styles.connectionStatus, isConnected ? styles.connected : styles.notConnected]}>
        <ThemedText style={styles.connectionStatusText}>
          {isConnected ? 'Connected' : 'Not Connected'}
        </ThemedText>
      </View>
    </SafeAreaView >
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },

  button: {
    aspectRatio: 1, // Makes the button square
    width: 100,
    height: 100,
    borderRadius: 12, // Rounded corners
    justifyContent: 'center', // Center items horizontally
    alignItems: 'center', // Center items vertically
    margin: 10, // Margin around each
  },

  row: {
    justifyContent: 'space-between', // Space between columns
    marginBottom: 10, // Margin between rows
  },
  contentContainer: {
    paddingBottom: 20,              // Optional: extra padding at the bottom
    paddingLeft: 10,                   // Optional: padding around the grid
  },

  deadlineButton: {
    backgroundColor: '#FF5733', // Specific color for deadlines
  },

  settingsButton: {
    backgroundColor: '#3498DB', // Specific color for settings
  },

  alarmsButton: {
    backgroundColor: '#F1C40F', // Specific color for alarms
  },

  syncButton: {
    backgroundColor: '#2ECC71', // Specific color for sync
  },
  connectionStatus: {
    padding: 10,
    borderRadius: 8,
    marginTop: 20,
    alignItems: 'center',
    justifyContent: 'center',
    width: '60%',
  },

  connected: {
    backgroundColor: '#2ECC71', // Green for connected
  },

  notConnected: {
    backgroundColor: '#E74C3C', // Red for not connected
  },

  connectionStatusText: {
    color: '#FFF', // White text for better contrast
    fontWeight: 'bold',
  },


});
