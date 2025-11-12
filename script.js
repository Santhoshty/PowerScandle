//replace the word 'static' with 'vignette'

const imgURL1 = 'https://vignette.wikia.nocookie.net/vsbattles/images/2/29/Sandwormsschoenherr.jpg';
const imgURL2 = 'https://vignette.wikia.nocookie.net/vsbattles/images/b/be/Honey_Lemon_Render.png/revision/latest/scale-to-width-down/400?cb=20190404133937';

const API_URL = 'http://127.0.0.1:5000/api/characters'; // Server URL
let scranData = []; // Data will be stored here after fetching
let currentItems = [];

/**
 * Fetches character data from the Python API and stores it in scranData.
 */
async function fetchData() {
    try {
        // Fetch data from the running Python server
        const response = await fetch(API_URL); 
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        // Parse the JSON response
        scranData = await response.json(); 
        console.log('Data loaded from Python:', scranData);
        return true; // Indicate success
    } catch (error) {
        console.error('Could not fetch data:', error);
        // Display an error message to the user if fetch fails
        document.getElementById('feedback').textContent = 'Error loading game data. Check the Python server.';
        return false; // Indicate failure
    }
}

function loadNewRound() {
    // Ensure there's data to pick from
    if (scranData.length < 2) {
        console.error("Not enough data to load a new round.");
        return;
    }

    // Pick two random characters
    let index1 = Math.floor(Math.random() * scranData.length);
    let index2 = Math.floor(Math.random() * scranData.length);
    while (index1 === index2) {
        index2 = Math.floor(Math.random() * scranData.length);
    }
    currentItems = [scranData[index1], scranData[index2]];

    // ... (rest of the card update logic) ...
    // Update Card 1
    const card1 = document.getElementById('card1');
    card1.querySelector('.character-image').src = currentItems[0].image;
    card1.querySelector('.character-name').textContent = currentItems[0].name;
    // Update Card 2
    const card2 = document.getElementById('card2');
    card2.querySelector('.character-image').src = currentItems[1].image;
    card2.querySelector('.character-name').textContent = currentItems[1].name;

    // Clear previous feedback
    document.getElementById('feedback').textContent = '';
}

function makeGuess(choice) {
    const chosenItem = currentItems[choice - 1];
    const otherItem = currentItems[choice === 1 ? 1 : 0];
    const feedbackElement = document.getElementById('feedback');

    // Compare ratings and give feedback
    if (chosenItem.rating > otherItem.rating) {
        feedbackElement.textContent = 'Correctomondo!.';
        // Add logic to update streak
    } else {
        feedbackElement.textContent = 'Wrong! The other one had a higher rating.';
        // Add logic to reset streak
    }
    
    // Display ratings after the guess
    feedbackElement.textContent += ` (${currentItems[0].rating}% vs ${currentItems[1].rating}%)`;

    // Load a new round after a delay
    setTimeout(loadNewRound, 3000);
}

Start the game when the page loads
window.onload = async () => {
    // 1. Fetch the data from the Python backend
    const dataLoaded = await fetchData();

    // 2. If successful, start the game
    if (dataLoaded && scranData.length >= 2) {
        loadNewRound();
    } else if (scranData.length < 2) {
         document.getElementById('feedback').textContent = 'Error: Not enough data loaded to start the game.';
    }
};
