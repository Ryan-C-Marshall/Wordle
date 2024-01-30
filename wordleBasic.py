LETTER_OFFSET = -97  # the ascii code for 'a'. Used for indexing in lists.
BEST_WORDS_MAX_LENGTH = 5  # the maximum number of top words that the program will display
WIN = True
CONTINUE = False

def getAllWords():
    """
    Gets all the words from the "words.txt" file.
    :return: A list of the words (without new line characters)
    """
    words = []
    with open("words.txt", "r") as file:
        for s in file.readlines():
            words.append(s[0:5])  # removes the \n at the end
        file.close()
    return words


def validWord(word, grey, yellow, green):
    """
    Checks if the given word is a possible wordle solution given the current grey, yellow, and green letters known.
    :param word: The word to check
    :param grey: The grey letters (letters not in the word)
    :param yellow: The yellow letters as a list of tuples: (spot, letter).
    :param green: The green letters as a list of tuples: (spot, letter).
    :return: A boolean indicating whether the word is a possible answer to the wordle.
    """
    for letter in grey:
        if letter in word:
            return False

    for (spot, letter) in green:
        if word[spot] != letter:
            return False

    for (spot, letter) in yellow:
        if (letter not in word) or (word[spot] == letter):
            return False

    return True


def updatePossibleWords(possibleWords, grey, yellow, green):
    """
    Updates the list of possible answers based on whether they are still valid answers.
    :param possibleWords: The old list of possible words
    :param grey: The grey letters (letters not in the word)
    :param yellow: The yellow letters as a list of tuples: (spot, letter).
    :param green: The green letters as a list of tuples: (spot, letter).
    :return: A new list of possible answers.
    """
    newPossibleWords = []
    for word in possibleWords:
        if validWord(word, grey, yellow, green):
            newPossibleWords.append(word)

    return newPossibleWords


def getWordScore(word, letterScores, posLetterScores, yellow, green):
    """
    Calculates the score of a word based on what we currently know about the wordle. A score reflects how much
    information this word is expected to provide, if guessed.
    :param word: The word to be scored.
    :param letterScores: A dictionary of 26 letters and their frequencies within the current pool of possible answers.
    :param posLetterScores: A list of 5 frequency lists indicating the letters' frequencies in each position in a word.
    :param yellow: The yellow letters as a list of tuples: (spot, letter).
    :param green: The green letters as a list of tuples: (spot, letter).
    :return: The score for this word; how useful it would be as a guess.
    """
    wordScore = 0

    for spot, letter in enumerate(word):
        alreadySeen = letter in word[0:spot]

        if letter not in [l for (_, l) in yellow]:  # letter is not in yellow
            if letter not in [l for (_, l) in green] and not alreadySeen:  # not in green and not duplicate

                wordScore += (letterScores[ord(letter) + LETTER_OFFSET] / 5 +
                              posLetterScores[spot][ord(letter) + LETTER_OFFSET])
                # increase by amount this letter is in possible words and amount this letter is in the right place

        elif letter not in [l for (_, l) in green]:  # letter is in yellow, not green
            if (spot, letter) not in yellow and not alreadySeen:  # not at this spot in yellow and not duplicate
                wordScore += posLetterScores[spot][ord(letter) + LETTER_OFFSET]
                # increase by amount this letter is in the right spot

    return wordScore


def getLetterScores(possibleWords):
    """
    Counts the frequency of each letter within the current pool of possible answers, and returns both the total
    frequency of each letter, and the frequency for each position (0 - 4) within the word for each letter.
    :param possibleWords: The current pool of possible answers.
    :return: letterScores: the frequency of each letter within the current pool of possible answers.
    :return: posLetterScores: a list of 5 frequency lists, each representing the frequency of letters for that
    position in the word.
    """
    # number of letters total
    letterScores = [0 for _ in range(26)]
    # number of each letter in each spot
    posLetterScores = [[0 for _ in range(26)] for _ in range(5)]

    # count all the letters, update the scores
    for word in possibleWords:
        for spot, letter in enumerate(word):
            letterScores[ord(letter) + LETTER_OFFSET] += 1
            posLetterScores[spot][ord(letter) + LETTER_OFFSET] += 1

    return letterScores, posLetterScores


def selectWords(possibleWords, yellow, green):
    """
    Selects the best words based on their scores.
    :param possibleWords: The current pool of possible answers.
    :param yellow: The yellow letters as a list of tuples: (spot, letter).
    :param green: The green letters as a list of tuples: (spot, letter).
    :return: The best words as an ordered list, and the best words that are still possible as an ordered list.
    """
    letterScores, posLetterScores = getLetterScores(possibleWords)

    # find the high score
    bestWords = []
    bestPossibleWords = []
    cutoffScore = 0
    highPossibleWordScore = 0

    for word in allWords:
        wordScore = getWordScore(word, letterScores, posLetterScores, yellow, green)

        cutoffScore = updateBestWords(word, wordScore, cutoffScore, bestWords)
        if word in possibleWords:
            highPossibleWordScore = updateBestWords(word, wordScore, highPossibleWordScore, bestPossibleWords)

    return bestWords, bestPossibleWords


def updateBestWords(word, wordScore, cutoffScore, bestWords):
    """
    Updates the bestWords list to include the given word, if its score is high enough to make the list.
    :param word: The word to add to the list
    :param wordScore: The word's score
    :param cutoffScore: The worst score within the bestWords list; the cutoff to make the list.
    :param bestWords: The list that will be updated.
    :return: The new worst score within the bestWords list.
    """
    if len(bestWords) < BEST_WORDS_MAX_LENGTH:
        bestWords.append((wordScore, word))
        bestWords.sort()
    elif wordScore > cutoffScore:
        bestWords[0] = (wordScore, word)
        bestWords.sort()

    return bestWords[0][0]


def updateLists(default, greyLetters, yellowLetters, greenLetters):
    """
    Takes input from the user to retrieve feedback on the most recent guess. Updates the running info
    (greyLetters, yellowLetters, greenLetters) to match.
    :param default: The best word that the program suggested to guess.
    :param greyLetters: The running list of grey letters (letters not part of the word).
    :param yellowLetters: The running list of yellow letters and their positions.
    :param greenLetters: The running list of green letters and their positions.
    :return: WIN if the game is over, otherwise CONTINUE
    """
    # could add input validation, but only I really use this.

    inputtedWord = input("Enter the word you inputted, or 'x' for the top suggested word: ").lower()
    if inputtedWord == "x":
        inputtedWord = default
    elif inputtedWord == "w":
        return WIN

    # again, not a clear prompt and no input validation. Again, only I really use this.

    wordColours = input("Enter the colours returned, with 0 for grey, 1 for yellow, and 2 for green: ")

    for i in range(5):
        letter = inputtedWord[i]
        if wordColours[i] == "0" and letter not in greyLetters:
            greyLetters.append(letter)
        elif wordColours[i] == "2" and (i, letter) not in greenLetters:
            greenLetters.append((i, letter))
            for j in range(5):
                if (j, letter) in yellowLetters:
                    yellowLetters.remove((j, letter))
        elif wordColours[i] == "1" and (i, letter) not in yellowLetters:
            yellowLetters.append((i, letter))

    return CONTINUE


def play():
    """
    The main game loop. Calculates the possible words, displays the guessing info to the user, then takes user input
    and updates the game lists. Continues until the word has been narrowed down to one option, or no words matching
    the specifications have been found.
    """
    possibleWords = allWords.copy()
    greyLetters = []  # list of letters
    yellowLetters = []  # list of tuples (spot [0 - 4], letter)
    greenLetters = []  # list of tuples (spot [0 - 4], letter)

    while len(possibleWords) > 1:
        bestWords, bestPossibleWords = selectWords(possibleWords, yellowLetters, greenLetters)
        bestWord = bestWords[-1]

        print("Number of possible words: " + str(len(possibleWords)))
        print("Top possible words:")
        for word in bestPossibleWords:
            print(str(int(word[0])) + ": " + str(word[1]))
        print("\nBest words:")
        for word in bestWords:
            print(str(int(word[0])) + ": " + str(word[1]))

        if updateLists(bestWord[1], greyLetters, yellowLetters, greenLetters) == WIN:
            return "You won!\n"
        possibleWords = updatePossibleWords(possibleWords, greyLetters, yellowLetters, greenLetters)

    print("Your word is " + possibleWords[0] + "!\n" if len(possibleWords) == 1 else "No words found.")


allWords = getAllWords()

print(" -- Wordle Assistant --")
playAgain = True
while playAgain:
    play()

    playAgain = input("Would you like to play again? (y/n): ").lower()[0] == "y"
