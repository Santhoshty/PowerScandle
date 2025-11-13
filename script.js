// Global variables will be initialized here
let allCharacters = [];
let character1 = null;
let character2 = null;
let playerScore = 0;
let roundsPlayed = 0;


// --- 1. Fetch Data and Initialize Game ---
async function fetchData() {
    try {
        // Fetch the data from the Flask endpoint
        const response = await fetch('http://127.0.0.1:8004/api/data');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        allCharacters = await response.json();
        
        if (allCharacters.length < 2) {
            document.getElementById('feedback').innerHTML = "<p style='color: red;'>Error: Not enough character data to start the game (need at least 2).</p>";
            return;
        }

        console.log("Data fetched successfully:", allCharacters);
        // CRITICAL DEBUG STEP: Attempt to initialize the game
        try {
            initializeGame();
        } catch (e) {
             document.getElementById('feedback').innerHTML = `<p style='color: red;'>**Rendering Error in initializeGame()**<br>Check console for details.</p>`;
             console.error("Game Initialization Failed:", e);
        }

    } catch (error) {
        console.error('Error fetching data:', error);
        // Ensure the error message is correctly displayed in the catch block
        document.getElementById('feedback').innerHTML = `<p style='color: red;'>Failed to load game data. Is the Flask server running? Error: ${error.message}</p>`;
    }
}

// --- 2. Game Initialization Logic ---
function initializeGame() {

    character1 = allCharacters[0];
    character2 = allCharacters[1];

    console.log("Character 1:", character1);
    console.log("Character 2:", character2);

    // 1. Update the Score Display
    // Ensure you have a score element in your HTML (see HTML update below)
    document.getElementById('player-score').textContent = playerScore;

    // 2. Update the HTML elements (Card 1)
    // Using 'Character' key for name and 'Source Image' key for image URL
    document.querySelector('#card1 .character-name').textContent = character1.Character;
    document.querySelector('#card1 .character-image').src = character1["Source Image"] || 'https://placehold.co/100x100/cccccc/000000?text=NO+IMG';
    document.querySelector('#card1 .character-image').alt = character1.Character;
    
    // 3. Update the HTML elements (Card 2)
    // Using 'Character' key for name and 'Source Image' key for image URL
    document.querySelector('#card2 .character-name').textContent = character2.Character;
    document.querySelector('#card2 .character-image').src = character2["Source Image"] || 'https://placehold.co/100x100/cccccc/000000?text=NO+IMG';
    document.querySelector('#card2 .character-image').alt = character2.Character;
    
    // 4. Clear feedback and set prompt
    document.getElementById('feedback').innerHTML = '<h3 class="text-xl font-bold">Who Will Win?</h2>';
    
    // 5. Hide the power levels for the start of the round and enable buttons
    document.getElementById('card1-stats').classList.add('hidden');
    document.getElementById('card2-stats').classList.add('hidden');
    document.getElementById('card1-button').disabled = false;
    document.getElementById('card2-button').disabled = false;
}


// --- 3. Guessing Logic (called by the button's onclick) ---
window.makeGuess = function(guessCardNumber) {
    // Disable buttons immediately to prevent multiple clicks
    document.getElementById('card1-button').disabled = true;
    document.getElementById('card2-button').disabled = true;

    if (!character1 || !character2) {
        document.getElementById('feedback').innerHTML = "<p style='color: orange;'>Game not initialized. Please refresh.</p>";
        return;
    }

    // CRITICAL FIX: Explicitly convert Power Level strings to numbers for comparison
    const power1 = parseFloat(character1["Power Level"]);
    const power2 = parseFloat(character2["Power Level"]);
    
    const feedbackElement = document.getElementById('feedback');
    let message = "";
    let isCorrect = false;

    // Show power levels after the guess
    document.getElementById('card1-stats').classList.remove('hidden');
    document.getElementById('card2-stats').classList.remove('hidden');
    
    // Display the original, non-parsed Power Level string
    document.getElementById('card1-power').textContent = character1["Tier"];
    document.getElementById('card2-power').textContent = character2["Tier"];


    // Determine the truly strongest character using the numerically parsed values
    const strongestCharacter = (power1 > power2) ? character1 : character2;
    const weakestCharacter = (power1 < power2) ? character1 : character2;

    // Get names
    const name1 = character1.Character;
    const name2 = character2.Character;

    // Check for a tie
    if (power1 === power2) {
        message = `It's a tie! Both ${name1} and ${name2} have a Power Level of ${character1["Power Level"]}.`;
        isCorrect = false; 
    } else {
        // Determine the user's chosen character based on the button clicked
        const guessedCharacter = (guessCardNumber === 1) ? character1 : character2;
        
        if (guessedCharacter === strongestCharacter) {
            isCorrect = true;
            message = `🎉 Correct! ${guessedCharacter.Character} (Power Level: ${guessedCharacter["Power Level"]}) is stronger than ${weakestCharacter.Character} (Power Level: ${weakestCharacter["Power Level"]}).`;
        } else {
            isCorrect = false;
            message = `❌ Incorrect. ${guessedCharacter.Character} (Power Level: ${guessedCharacter["Power Level"]}) is weaker than the true strongest, ${strongestCharacter.Character} (Power Level: ${strongestCharacter["Power Level"]}).`;
        }

    if (isCorrect) {
        // Increment the global score variable (assuming 'playerScore' is defined globally)
        playerScore++; 
        // Update the score display element
        document.getElementById('player-score').textContent = playerScore;
    }

    else {playerScore = 0} //Change Points to 0 When Lost
    
    // Update the feedback message with the final result
    feedbackElement.innerHTML = `<h2 class="text-xl font-bold">${message}</h2>`;
    
    // Add a "Next Round" button to the feedback area
    feedbackElement.innerHTML += `
        <button onclick="startNextRound()" 
                class="action-button mt-4 px-6 py-2 bg-green-600 hover:bg-green-500 rounded-lg font-semibold shadow-lg">
            Start Next Round
        </button>
    `;
    }

    // Display the result
    feedbackElement.innerHTML = `<h2 class='text-xl font-bold p-2 text-${isCorrect ? 'green' : 'red'}-400'>${message}</h2>`;

    // After a short delay, start a new round
    setTimeout(() => {
        initializeGame();
    }, 3000); // 3-second delay before the next round starts
};


// --- 4. Start the game by fetching data when the page loads ---
document.addEventListener('DOMContentLoaded', fetchData);