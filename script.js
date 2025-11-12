// The dedicated API endpoint for a random pair
const API_URL_RANDOM = 'http://127.0.0.1:5000/api/characters/random'; 
let currentItems = [];

/**
 * Fetches a single pair of random characters from the API.
 * This function is called every time a new round is needed.
 */
async function loadNewRound() {
    try {
        // Clear previous feedback immediately to show the game is loading
        document.getElementById('feedback').textContent = 'Loading next round...';
        
        // 1. Fetch data for TWO characters from the server's random endpoint
        const response = await fetch(API_URL_RANDOM); 
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // 2. The response is a JSON array of two objects
        const data = await response.json(); 
        
        if (!Array.isArray(data) || data.length < 2) {
            throw new Error("API returned insufficient data.");
        }

        currentItems = data;
        console.log('New round loaded:', currentItems.map(item => item.name));

        // 3. Update Card 1
        const card1 = document.getElementById('card1');
        // Use 'image_url' and 'power_level' as named in the Python API
        card1.querySelector('.character-image').src = currentItems[0].image_url;
        card1.querySelector('.character-name').textContent = currentItems[0].name;
        
        // 4. Update Card 2
        const card2 = document.getElementById('card2');
        card2.querySelector('.character-image').src = currentItems[1].image_url;
        card2.querySelector('.character-name').textContent = currentItems[1].name;

        // 5. Clear feedback for the guess
        document.getElementById('feedback').textContent = '';

    } catch (error) {
        console.error('Failed to load new round:', error);
        document.getElementById('feedback').textContent = 
            '🛑 Error loading game data. Please ensure the Python server is running.';
    }
}

function makeGuess(choice) {
    const chosenItem = currentItems[choice - 1];
    const otherItem = currentItems[choice === 1 ? 1 : 0];
    const feedbackElement = document.getElementById('feedback');

    // Compare the 'power_level' attribute from the API
    if (chosenItem.power_level > otherItem.power_level) {
        feedbackElement.textContent = 'Correctomondo!.';
        // Add logic to update streak
    } else {
        feedbackElement.textContent = 'Wrong! The other one had a higher rating.';
        // Add logic to reset streak
    }
    
    // Display power levels after the guess
    feedbackElement.textContent += ` (${currentItems[0].power_level} vs ${currentItems[1].power_level})`;

    // Load a new round after a delay
    setTimeout(loadNewRound, 3000);
}

// Start the game when the page loads
window.onload = async () => {
    // Start the game directly by loading the first round from the API
    loadNewRound();
};