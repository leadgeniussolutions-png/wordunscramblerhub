// Standard letter values for scoring
const SCRABBLE_POINTS = {
  a: 1, b: 3, c: 3, d: 2, e: 1, f: 4, g: 2, h: 4, i: 1, j: 8, k: 5, l: 1, m: 3,
  n: 1, o: 1, p: 3, q: 10, r: 1, s: 1, t: 1, u: 1, v: 4, w: 4, x: 8, y: 4, z: 10
};

const WWF_POINTS = {
  a: 1, b: 4, c: 4, d: 2, e: 1, f: 4, g: 3, h: 3, i: 1, j: 10, k: 5, l: 2, m: 4,
  n: 2, o: 1, p: 4, q: 10, r: 1, s: 1, t: 1, u: 2, v: 5, w: 4, x: 8, y: 3, z: 10
};

// General English letter frequencies for sorting Wordle suggestions
const LETTER_FREQUENCIES = {
  e: 12.02, t: 9.10, a: 8.12, o: 7.68, i: 7.31, n: 6.95, s: 6.28, r: 6.02, h: 5.92,
  d: 4.32, l: 3.98, u: 2.88, c: 2.71, m: 2.61, f: 2.30, y: 2.11, w: 2.09, g: 2.03,
  p: 1.82, b: 1.49, v: 1.11, k: 0.69, x: 0.17, q: 0.11, j: 0.10, z: 0.07
};

/**
 * Builds a character frequency map for a given string
 */
function getCharCounts(str) {
  const counts = {};
  for (let i = 0; i < str.length; i++) {
    const char = str[i].toLowerCase();
    counts[char] = (counts[char] || 0) + 1;
  }
  return counts;
}

/**
 * Checks if a dictionary word can be formed by a subset of input letters,
 * accounting for wildcards ('?', '*', or ' ').
 * Returns { canForm: boolean, wildcardsUsed: number, normalPointsScrabble: number, normalPointsWwf: number }
 */
function canFormWord(word, inputCounts, totalWildcards) {
  const wordCounts = getCharCounts(word);
  let wildcardsNeeded = 0;
  
  let scrabbleScore = 0;
  let wwfScore = 0;

  for (const char in wordCounts) {
    const needed = wordCounts[char];
    const available = inputCounts[char] || 0;
    
    if (needed > available) {
      const diff = needed - available;
      wildcardsNeeded += diff;
      
      // The characters covered by available tiles score points;
      // the remaining letters covered by wildcards score 0 points.
      if (available > 0) {
        scrabbleScore += (SCRABBLE_POINTS[char] || 0) * available;
        wwfScore += (WWF_POINTS[char] || 0) * available;
      }
    } else {
      // All occurrences of this letter are covered by normal input tiles
      scrabbleScore += (SCRABBLE_POINTS[char] || 0) * needed;
      wwfScore += (WWF_POINTS[char] || 0) * needed;
    }
  }

  if (wildcardsNeeded <= totalWildcards) {
    return {
      canForm: true,
      wildcardsUsed: wildcardsNeeded,
      scrabbleScore: scrabbleScore,
      wwfScore: wwfScore
    };
  }
  
  return { canForm: false };
}

/**
 * Word Unscrambler Solver
 * Inputs:
 *   - rack: string of letters (may include '?', '*', ' ')
 *   - options: { startsWith: string, endsWith: string, contains: string, length: number }
 */
function solveUnscrambler(rack, options = {}) {
  // 1. Prepare Rack
  let letters = "";
  let wildcards = 0;
  
  for (let i = 0; i < rack.length; i++) {
    const char = rack[i].toLowerCase();
    if (char === '?' || char === '*' || char === ' ') {
      wildcards++;
    } else if (/[a-z]/.test(char)) {
      letters += char;
    }
  }
  
  const inputCounts = getCharCounts(letters);
  const maxWordLen = letters.length + wildcards;
  
  // Prepare constraints
  const startsWith = (options.startsWith || "").trim().toLowerCase();
  const endsWith = (options.endsWith || "").trim().toLowerCase();
  const contains = (options.contains || "").trim().toLowerCase();
  const targetLength = options.length ? parseInt(options.length) : null;
  
  const results = [];
  
  // 2. Search the dictionary
  // Loop through allowed word lengths
  const minSearchLen = Math.max(2, targetLength || 2);
  const maxSearchLen = Math.min(12, targetLength || maxWordLen);
  
  if (minSearchLen > maxSearchLen || !window.DICTIONARY) {
    return [];
  }
  
  for (let len = minSearchLen; len <= maxSearchLen; len++) {
    const wordsStr = window.DICTIONARY[len];
    if (!wordsStr) continue;
    
    // Split the space-separated words
    const words = wordsStr.split(' ');
    
    for (let i = 0; i < words.length; i++) {
      const word = words[i];
      
      // A. Fast constraint pre-filtering
      if (targetLength && word.length !== targetLength) continue;
      if (startsWith && !word.startsWith(startsWith)) continue;
      if (endsWith && !word.endsWith(endsWith)) continue;
      if (contains && !word.includes(contains)) continue;
      
      // B. Subset validation with wildcards
      const match = canFormWord(word, inputCounts, wildcards);
      if (match.canForm) {
        results.push({
          word: word,
          length: word.length,
          scrabbleScore: match.scrabbleScore,
          wwfScore: match.wwfScore
        });
      }
    }
  }
  
  // Sort results by Scrabble score descending, then alphabetically
  return results.sort((a, b) => {
    if (b.scrabbleScore !== a.scrabbleScore) {
      return b.scrabbleScore - a.scrabbleScore;
    }
    return a.word.localeCompare(b.word);
  });
}

/**
 * Wordle Solver Constraint Checker
 * Inputs:
 *   - green: Array of 5 strings (either character or empty)
 *   - yellow: Array of 5 Arrays of strings (letters present in word but NOT at this index)
 *   - grey: Array/Set of strings (letters not present in word, except if they are green/yellow in other positions)
 */
function solveWordle(green, yellow, grey) {
  if (!window.DICTIONARY) return [];
  
  // Wordle is strictly 5-letter words
  const wordsStr = window.DICTIONARY[5];
  if (!wordsStr) return [];
  const words = wordsStr.split(' ');
  
  // Normalize constraints
  const greenConstraint = green.map(c => c ? c.toLowerCase() : "");
  
  const yellowConstraint = yellow.map(arr => 
    (arr || []).map(c => c.toLowerCase()).filter(c => /[a-z]/.test(c))
  );
  
  // Collect all unique green/yellow letters
  const greenYellowLetters = new Set();
  greenConstraint.forEach(c => { if (c) greenYellowLetters.add(c); });
  yellowConstraint.forEach(arr => arr.forEach(c => greenYellowLetters.add(c)));
  
  // Grey letters are strictly excluded, EXCEPT if they are green or yellow elsewhere
  const greyConstraint = new Set(
    (grey || []).map(c => c.toLowerCase()).filter(c => /[a-z]/.test(c) && !greenYellowLetters.has(c))
  );
  
  const results = [];
  
  for (let i = 0; i < words.length; i++) {
    const word = words[i];
    let isMatch = true;
    
    // 1. Check Green (Exact index matches)
    for (let pos = 0; pos < 5; pos++) {
      const gc = greenConstraint[pos];
      if (gc && word[pos] !== gc) {
        isMatch = false;
        break;
      }
    }
    if (!isMatch) continue;
    
    // 2. Check Yellow (Contains, but wrong index)
    for (let pos = 0; pos < 5; pos++) {
      const ycList = yellowConstraint[pos];
      for (let j = 0; j < ycList.length; j++) {
        const yc = ycList[j];
        // Word must contain the letter, but NOT at this position
        if (!word.includes(yc) || word[pos] === yc) {
          isMatch = false;
          break;
        }
      }
      if (!isMatch) break;
    }
    if (!isMatch) continue;
    
    // 3. Check Grey (Strict Exclusions)
    for (let pos = 0; pos < 5; pos++) {
      if (greyConstraint.has(word[pos])) {
        isMatch = false;
        break;
      }
    }
    if (!isMatch) continue;
    
    // Word fits! Score it based on English letter frequency
    let frequencyScore = 0;
    const uniqueLetters = new Set(word);
    uniqueLetters.forEach(char => {
      frequencyScore += (LETTER_FREQUENCIES[char] || 0);
    });
    
    results.push({
      word: word,
      score: parseFloat(frequencyScore.toFixed(2))
    });
  }
  
  // Sort Wordle suggestions by frequency score descending
  return results.sort((a, b) => b.score - a.score);
}

/**
 * Word Scramble Generator
 * Inputs:
 *   - word: string to scramble
 * Returns: scrambled word (anagram)
 */
function scrambleWord(word) {
  const cleanWord = word.trim().toUpperCase();
  if (cleanWord.length <= 1) return cleanWord;
  
  const arr = cleanWord.split('');
  // Shuffle array (Fisher-Yates)
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    const temp = arr[i];
    arr[i] = arr[j];
    arr[j] = temp;
  }
  
  const scrambled = arr.join('');
  // Try again once if it equals original word
  if (scrambled === cleanWord && cleanWord.length > 2) {
    return scrambleWord(word);
  }
  return scrambled;
}
