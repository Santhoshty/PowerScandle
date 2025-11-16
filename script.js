// Global variables will be initialized here
let allCharacters = [];
let character1 = null;
let character2 = null;
let playerScore = 0;
// roundsPlayed is redundant, let's stick to currentRound
let currentRound = 1;
let characterIndex = 0; // Starts at 0, uses allCharacters[0] and allCharacters[1] for the first round
const MAX_ROUNDS = 10;

// --- 1. Fetch Data and Initialize Game ---
async function fetchData() {
    try {
        // Fetch the data from the Flask endpoint
        const response = await fetch('http://127.0.0.1:5000/api/data');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        allCharacters = await response.json();
        
        // **Critical: Ensure data is sufficient before proceeding**
        if (allCharacters.length < 2) {
            document.getElementById('feedback').innerHTML = "<p style='color: red;'>Error: Not enough character data to start the game (need at least 2).</p>";
            return;
        }

        // Shuffle the characters array to make the game more random
        //allCharacters.sort(() => Math.random() - 0.5); 

        console.log("Data fetched successfully:", allCharacters);
        
        // CRITICAL FIX: Start the first round after data is fetched
        try {
            startRound(); // Call the renamed function to start the first round
        } catch (e) {
             document.getElementById('feedback').innerHTML = `<p style='color: red;'>**Rendering Error in startRound()**<br>Check console for details.</p>`;
             console.error("Game Initialization Failed:", e);
        }

    } catch (error) {
        console.error('Error fetching data:', error);
        // Ensure the error message is correctly displayed in the catch block
        document.getElementById('feedback').innerHTML = `<p style='color: red;'>Failed to load game data. Is the Flask server running? Error: ${error.message}</p>`;
    }
}

function createCharacterLink(character) {
    // We access the URL property from the character object
    const url = character.URL; 
    // We access the Character name property from the character object
    const name = character.Character; 
    
    // Return an HTML anchor tag string
    return `<a href="${url}" target="_blank" rel="noopener noreferrer">${name}</a>`;
}

// --- 2. Game Round Logic (Renamed and Improved) ---
function startRound() {

// 1. Check if the game is over
    if (currentRound > MAX_ROUNDS) {
        // Handle Game Over logic here (e.g., display final score, reset button)
document.getElementById('feedback').innerHTML = '<h2 class="text-2xl font-bold text-green-500 **mb-4**">Game Over! </h2><p class="text-xl">Your final score is: ' + playerScore + '/' + MAX_ROUNDS + '</p>';        console.log("Game Over! Final Score:", playerScore);
        
        // Optionally disable buttons or show a restart option
        document.getElementById('card1-button').disabled = true;
        document.getElementById('card2-button').disabled = true;

        return; // Stop execution
    }

    // Ensure we don't go past the available characters
    // Using 2 characters per round, so index + 1 must be less than array length
    if (characterIndex + 1 >= allCharacters.length) {
        console.warn("Ran out of characters. Stopping game.");
        // End the game if there aren't enough characters left for a full round
        currentRound = MAX_ROUNDS + 1; // Force Game Over
        startRound(); // Rerun to hit the Game Over logic above
        return; 
    }

    // Select the next two characters based on the current index
    character1 = allCharacters[characterIndex];
    character2 = allCharacters[characterIndex + 1];

    console.log(`--- Starting Round ${currentRound} ---`);
    console.log("Character 1:", character1.Character);
    console.log("Character 2:", character2.Character);

    // 2. Update the Score and Round Display (assuming you add a round display element)
    document.getElementById('player-score').textContent = playerScore;
    document.getElementById('round-number').textContent = `${currentRound}`;
    // document.getElementById('round-number').textContent = currentRound; // Uncomment if you add this HTML element

    // 3. Update the HTML elements (Card 1)
    document.querySelector('#card1 .character-name').textContent = character1.Character;
    document.querySelector('#card1 .character-image').src = character1["Source Image"] || 'https://placehold.co/100x100/cccccc/000000?text=NO+IMG';
    document.querySelector('#card1 .character-image').alt = character1.Character;
    
    // 4. Update the HTML elements (Card 2)
    document.querySelector('#card2 .character-name').textContent = character2.Character;
    document.querySelector('#card2 .character-image').src = character2["Source Image"] || 'https://placehold.co/100x100/cccccc/000000?text=NO+IMG';
    document.querySelector('#card2 .character-image').alt = character2.Character;
    
    // 5. Clear feedback and set prompt
    document.getElementById('feedback').innerHTML = `<h3 class="text-xl font-bold">Round ${currentRound}/${MAX_ROUNDS}: Who Will Win?</h2>`;
    
    // 6. Hide the power levels for the start of the round and enable buttons
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
        const characterTier1 = createCharacterLink(character1)
        const characterTier2 = createCharacterLink(character2)
        message = `It's a tie! Both <u>${characterTier1}</u> and <u>${characterTier2}</u> are equals. <br>Free Point!</br>`;
        isCorrect = true; 
    } else {
        // Determine the user's chosen character based on the button clicked
        const guessedCharacter = (guessCardNumber === 1) ? character1 : character2;
        const guessedCharacterLink = createCharacterLink(guessedCharacter);
        const strongestCharacterLink = createCharacterLink(strongestCharacter);
        const weakestCharacterLink = createCharacterLink(weakestCharacter);
        if (guessedCharacter === strongestCharacter) {
            isCorrect = true;
            // Use the linked name in the message
            message = `🎉 Correct! <u>${guessedCharacterLink}</u> is stronger than <u>${weakestCharacterLink}</u>`;
        } else {
            isCorrect = false;
            // Use the linked names in the message
            message = `❌ Incorrect. <u>${guessedCharacterLink}</u> is weaker than the true strongest, <u>${strongestCharacterLink}</u>`;
        }
    } // End of tie/non-tie check

    if (isCorrect) {
        // Increment the global score variable
        playerScore++; 
        // Update the score display element
        document.getElementById('player-score').textContent = playerScore;
    } 
    
    // Update the feedback message with the final result
    feedbackElement.innerHTML = `<h2 class='text-xl font-bold p-2 text-${isCorrect ? 'green' : 'red'}-400'>${message}</h2>`;
    
    // Add the "Next Round" button
    feedbackElement.innerHTML += `
        <button onclick="advanceGame()" 
                class="action-button mt-4 px-6 py-2 bg-green-600 hover:bg-green-500 rounded-lg font-semibold shadow-lg">
            Start Next Round
        </button>
    `;
    
    // CRITICAL FIX: Removed the automatic setTimeout call here.
    // The game now waits for the player to click the "Start Next Round" button, 
    // which calls the new `advanceGame` function.
};


// --- 4. Game Advancement Logic ---
window.advanceGame = function() {
    // 1. Increment the character index by 2 (to skip the characters just used)
    characterIndex += 2; 

    // 2. Increment the round number
    currentRound++;
    
    // 3. Start the next round (which will check for MAX_ROUNDS)
    startRound();
}


// --- 5. Start the game by fetching data when the page loads ---
document.addEventListener('DOMContentLoaded', fetchData);