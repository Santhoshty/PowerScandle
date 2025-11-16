javascript

// This file is intended to be used as a Cloudflare Worker using the 'cheerio' library for HTML parsing.
// You would add 'cheerio' as a dependency in your package.json.
import * as cheerio from 'cheerio';

const VS_BATTLE_URL = "https://vsbattles.fandom.com/wiki/Special:Random";

// Map Tier strings to numerical power levels
const powerLevelMap = {
    '11-C': 10, '11-B': 20, '11-A': 30, '10-C': 40, '10-B': 50, '10-A': 60,
    '9-C': 70, '9-B': 80, '9-A': 90, '8-C': 100, 'High 8-C': 110, '8-B': 120,
    '8-A': 130, 'Low 7-C': 140, '7-C': 150, 'High 7-C': 160, 'Low 7-B': 170,
    '7-B': 180, '7-A': 190, 'High 7-A': 200, '6-C': 210, 'High 6-C': 220,
    'Low 6-B': 225, '6-B': 230, 'High 6-B': 240, '6-A': 250, 'High 6-A': 260,
    '5-C': 270, 'Low 5-B': 280, '5-B': 290, '5-A': 300, 'High 5-A': 310,
    'Low 4-C': 320, '4-C': 330, 'High 4-C': 340, '4-B': 350, '4-A': 360,
    '3-C': 370, '3-B': 380, '3-A': 390, 'High 3-A': 400, 'Low 2-C': 410,
    '2-C': 420, '2-B': 430, '2-A': 440, 'Low 1-C': 450, '1-C': 460,
    'High 1-C': 470, '1-B': 480, 'High 1-B': 490, 'Low 1-A': 500, '1-A': 510,
    'High 1-A': 520, '0': 530, 'Unknown': 365, 'Varies': 120
};

/**
 * Helper to fetch a URL and parse it with Cheerio
 * Follows redirects automatically.
 */
async function fetchPage(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    const html = await response.text();
    const currentUrl = response.url; // Get the final URL after redirects (e.g., from Special:Random)
    return { $: cheerio.load(html), currentUrl };
}

/**
 * Extracts the Tier value from the Cheerio object.
 */
function getTier($) {
    // Find the <a> tag with text 'Tier'
    const tierLink = $('a:contains("Tier")').filter((i, el) => $(el).text() === 'Tier');
    
    if (tierLink.length > 0) {
        // Find the parent's next sibling <b> tag
        const tierValueTag = tierLink.parent().nextAll('b').first();
        
        if (tierValueTag.length > 0) {
            return tierValueTag.text().trim();
        }
    }
    return null;
}

/**
 * Extracts the main character image link using multiple methods for reliability.
 */
function getImageLink($) {
    // Attempt 1: Target the image within the main information box (<aside> tag)
    const mainImage = $('aside img').first();
    if (mainImage.length > 0) {
        const src = mainImage.attr('src');
        if (src && src.includes('static.wikia.nocookie')) {
            return src.replace('static', 'vignette');
        }
    }
    
    // Attempt 2 (Fallback): Find the third image source on the page
    const images = $('img');
    let validImageCount = 0;
    for (let i = 0; i < images.length; i++) {
        const src = $(images[i]).attr('src');
        if (src && src.includes('static.wikia.nocookie')) {
            validImageCount++;
            if (validImageCount === 3) {
                return src.replace('static', 'vignette');
            }
        }
    }
    return null;
}

/**
 * Main function to scrape a single random character
 */
async function scrapeCharacter() {
    let tierValue, characterName, imageLink, powerLevel, finalUrl;
    let iterations = 0;
    const MAX_ITERATIONS = 10;

    while (iterations < MAX_ITERATIONS) {
        iterations++;
        console.log(`Fetching random page, iteration ${iterations}...`);
        
        try {
            const { $, currentUrl } = await fetchPage(VS_BATTLE_URL);
            finalUrl = currentUrl;

            // Get Character Name
            const pageTitle = $('title').text();
            characterName = pageTitle.split(' |', 1)[0].trim();

            // Get Tier Value
            tierValue = getTier($);

            if (tierValue === null) {
                console.log(`Tier Invalid for ${characterName}. Retrying...`);
                // Wait briefly before retrying in a real deployment might be wise, but Cloudflare Workers are fast.
                continue; // Skip the rest of the loop and try again
            }

            // Get Image Link
            imageLink = getImageLink($);
            if (imageLink === null) {
                console.log(`Could not find a reliable image for ${characterName}.`);
            }

            // Get Power Level
            powerLevel = powerLevelMap[tierValue] || 0;

            // If we successfully found a tier, we break the loop
            break; 

        } catch (error) {
            console.error(`Scraping error during iteration ${iterations}:`, error);
            if (iterations === MAX_ITERATIONS) throw error;
        }
    }

    if (tierValue === null) {
        throw new Error("Failed to find a valid character tier after maximum iterations.");
    }

    return {
        Character: characterName,
        Tier: tierValue,
        "Source Image": imageLink,
        "Power Level": powerLevel,
        URL: finalUrl
    };
}

/**
 * The main event handler for the Cloudflare Worker Fetch event.
 */
export default {
    async fetch(request, env, ctx) {
        try {
            // Collect data for 21 characters concurrently (or sequentially if you prefer)
            const count = 21;
            const dataPromises = [];

            for (let i = 0; i < count; i++) {
                // We run these sequentially to avoid hammering the source site simultaneously with the *same* random request
                // This simulates the sleep you had in Python better.
                dataPromises.push(scrapeCharacter());
                await new Promise(resolve => setTimeout(resolve, 200)); // Sleep equivalent
            }

            const allCharacterData = await Promise.all(dataPromises);

            return new Response(JSON.stringify(allCharacterData, null, 4), {
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*' // Enable CORS for development
                },
            });
        } catch (e) {
            return new Response(`Error: ${e.message}`, { status: 500 });
        }
    }
};

