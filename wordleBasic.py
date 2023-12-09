def getAllWords():
    words = []
    with open("words.txt", "r") as file:
        for s in file.readlines():
            words.append(s[0:5])  # removes the \n at the end
        file.close()
    return words


def validWord(word, grey, yellow, green):
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
    newPossibleWords = []
    for word in possibleWords:
        if validWord(word, grey, yellow, green):
            newPossibleWords.append(word)

    return newPossibleWords


def getWordScore(word, letterScores, posLetterScores, yellow, green):
    wordScore = 0

    for spot, letter in enumerate(word):
        alreadySeen = letter in word[0:spot]

        if letter not in [l for (_, l) in yellow]:  # letter is not in yellow
            if letter not in [l for (_, l) in green] and not alreadySeen:  # not in green and not duplicate

                wordScore += letterScores[ord(letter) - 97] / 5 + posLetterScores[spot][ord(letter) - 97]
                # increase by amount this letter is in possible words and amount this letter is in the right place

        elif letter not in [l for (_, l) in green]:  # letter is in yellow, not green
            if (spot, letter) not in yellow and not alreadySeen:  # not at this spot in yellow and not duplicate
                wordScore += posLetterScores[spot][ord(letter) - 97]
                # increase by amount this letter is in the right spot

    return wordScore


def selectWords(possibleWords, yellow, green):
    # number of letters total
    letterScores = [0 for _ in range(26)]
    # number of each letter in each spot
    posLetterScores = [[0 for _ in range(26)] for _ in range(5)]

    # count all the letters, update the scores
    for word in possibleWords:
        for spot, letter in enumerate(word):
            letterScores[ord(letter) - 97] += 1
            posLetterScores[spot][ord(letter) - 97] += 1

    # find the high score
    bestWords = []
    bestPossibleWords = []
    highScore = 0
    highPossibleWordScore = 0

    for word in allWords:
        wordScore = getWordScore(word, letterScores, posLetterScores, yellow, green)

        highScore = updateHighScores(word, wordScore, highScore, bestWords)
        if word in possibleWords:
            highPossibleWordScore = updateHighScores(word, wordScore, highPossibleWordScore, bestPossibleWords)

    return bestWords, bestPossibleWords


def updateHighScores(word, wordScore, highScore, bestWords):
    if len(bestWords) < 5:
        bestWords.append((wordScore, word))
        bestWords.sort()
    elif wordScore > highScore:
        bestWords[0] = (wordScore, word)
        bestWords.sort()

    return bestWords[0][0]


def updateLists(default, greyLetters, yellowLetters, greenLetters):
    inputtedWord = input("Enter the word you inputted, or 'x' for the top suggested word: ").lower()
    if inputtedWord == "x":
        inputtedWord = default
    elif inputtedWord == "w":
        return "win"

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

    # printing
    # print("Grey: " + str(greyLetters))
    # print("Yellow: " + str(yellowLetters))
    # print("Green: " + str(greenLetters))

    return "continue"


def play():
    possibleWords = allWords.copy()
    greyLetters = []  # list of letters
    yellowLetters = []  # list of tuples (spot [0 - 4], letter)
    greenLetters = []  # list of tuples (spot [0 - 4], letter)
    bestWord = ""

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

        if updateLists(bestWord[1], greyLetters, yellowLetters, greenLetters) == "win":
            return "You won!\n"
        possibleWords = updatePossibleWords(possibleWords, greyLetters, yellowLetters, greenLetters)

    return "Your word is " + possibleWords[0] + "!\n" if len(possibleWords) == 1 else "No words found."


allWords = getAllWords()

print(" -- Wordle Assistant --")
while True:
    print(play())
