import os


def legalTransformation(word1, word2):
	''' Takes 2 words and checks that there is a legal transform from one to the other
	A transform is legal when the words are the same except for one letter

	Args:
		word1 (string): The first word
		word2 (string): The second word

	Return:
		bool: True if there is a legal transform netween the words
	'''
	if len(word1) != len(word2) or len(word1) < 1:
		# The words must be the same length
		return False
	foundMissmatch = False
	for idx in xrange(len(word1)):
		if word1[idx] != word2[idx]:
			if foundMissmatch:
				# This is the second different letter
				return False
			foundMissmatch = True
	# Return True if exactly one letter is different
	return foundMissmatch


class OrganisedDictionary(object):
	''' Represents a dictionary of words in an organised state
	Words are transformed into a number of hashed numbers which define the sets the words belong to
	A set of words is a list of words that can transform into eachother

	Args:
		word (list of string): The dictionary of words
	'''
	def __init__(self, words):
		self.__words = words
		self.__hashedWords = {}
		if len(self.__words) == 0:
			return
		self.__wordLength = len(self.__words[0])
		for word in self.__words:
			if len(word) != self.__wordLength:
				raise ValueError

			# Transform each word into all the hash codes that represent matching transforms
			hashNumbers = self.__getAllWordHashNumbers(word)
			for hashNumber in hashNumbers:
				self.__hashedWords.setdefault(hashNumber, set()).add(word)

	def __getAllWordHashNumbers(self, word):
		''' Gets the numbers that represent the sets the word belongs to

		Args:
			word (string): The word to test

		Returns:
			list of int: The hash numbers representing the sets
		'''
		hashNumbers = []
		# One at a time, replace each letter with '_'
		# Then hash these strings into numbers
		for idx in xrange(len(word)):
			editWord = word[:idx] + '_' + word[idx+1:]
			hashNumbers.append(hash(editWord))
		return hashNumbers

	def getTransformableWords(self, word):
		''' For the given word, find all words in the dictionary that are legally transformable from it

		Args:
			word (string): The word to transform from

		Returns:
			list of string: All words that can be transferred to from the given word
		'''
		matchingWords = set()
		assert(word in self.__words)
		# Get the hash codes representing the n different ways to match (one for each letter)
		hashNumbers = self.__getAllWordHashNumbers(word)
		# Add all words in each set
		for hashNumber in hashNumbers:
			matchingWords.update(self.__hashedWords[hashNumber])
		matchingWords.remove(word)
		transformableWords = []
		# We still have to test each word as a valid transform
		# because different strings can hash to the same number
		for matchWord in matchingWords:
			if legalTransformation(word, matchWord):
				transformableWords.append(matchWord)
		return transformableWords


class SearchPath(object):
	''' Represents a list of words, each one transforming to the next by changing one letter

	Args:
		firstWord (string): The first word in the list
	'''
	def __init__(self, firstWord=None):
		self.__words = []
		if firstWord is not None:
			self.addWord(firstWord)

	@property
	def words(self):
		''' 
		Returns:
			list of string: The words in the path
		'''
		return self.__words

	@property
	def lastWord(self):
		''' 
		Returns:
			string: The last word in the path
		'''
		return self.__words[-1]

	@property
	def numTransformations(self):
		''' 
		Returns:
			int: The number of transformations the search path represents
		'''
		return len(self.__words) - 1

	def addWord(self, word):
		''' Adds a new word to the search path

		Args:
			word (string): The word to add
		'''
		self.__words.append(word)

	def makeCopy(self):
		''' Makes a duplicate copy of this object

		Returns:
			SearchPath: The copy
		'''
		copySearchPath = SearchPath()
		for word in self.__words:
			copySearchPath.addWord(word)
		return copySearchPath


class DictionaryDash(object):
	''' Takes a dictionary of words and provides methods to get the shortest paths 
	between pairs of words in the dictionary by changing one letter at a time

	Args:
		dictionary (list of string): The dictionary of words
	'''
	def __init__(self, dictionary):
		self.__dictionary = dictionary
		self.__organisedDictionary = OrganisedDictionary(self.__dictionary)
		self.__reachedWords = []
		self.__searchPaths = []

	def getShortestTransformationSequence(self, startWord, endWord):
		''' Get the shortest seuqnce of words that transform the first word 
		into startWord into endWord, changing one letter at a time

		Args:
			startWord (string): The word at the start of the sequence
			endWord (string): The word at the end of the sequence

		Returns:
			list of string: On of the shortest sequences of words that transform 
				from start to end if one exists, otherwise None
		'''
		self.__targetWord = endWord
		self.__reachedWords = [startWord]
		self.__searchPaths = [SearchPath(startWord)]
		self.__successfulPath = None
		self.__finished = False
		# Starting with one search path we will branch into all 
		# possible next words creating new paths and repeating
		# A path is finished when it reaches the target word 
		# or a word that another path has already reached
		# We're done when all paths are finished or one of them reaches the target
		while not self.__finished:
			self.__extendPaths()
		return self.__successfulPath

	def __extendPaths(self):
		''' Where possible extend all the existing paths of transformations by one 
		word, creating new paths when there is more than one next word
		'''
		searchPaths = []
		# Extend each path to all next words
		for searchPath in self.__searchPaths:
			# These are the possible next words for this path
			nextWords = self.__organisedDictionary.getTransformableWords(searchPath.lastWord)
			validNextWords = []
			# Filter out all words that have been reached already
			for word in nextWords:
				if word not in self.__reachedWords:
					validNextWords.append(word)
			if not validNextWords:
				# No un-visited transformation from this word so path is at a dead end
				continue
			if self.__targetWord in validNextWords:
				# Found the target word!
				self.__successfulPath = searchPath
				self.__successfulPath.addWord(self.__targetWord)
				self.__finished = True
				break
			# This path goes back onto the list of unfinished search paths
			searchPaths.append(searchPath)
			word = validNextWords.pop()
			# If there's more than one valid transformation then we need to make new search paths
			for validNextWord in validNextWords:
				# The new search path is the same as the old until this next word
				newSearchPath = searchPath.makeCopy()
				newSearchPath.addWord(validNextWord)
				searchPaths.append(newSearchPath)
				self.__reachedWords.append(validNextWord)
			# Extend the existing path
			searchPath.addWord(word)
			self.__reachedWords.append(word)
		self.__searchPaths = searchPaths
		if not self.__searchPaths:
			self.__finished = True

def lengthOfShortestTransform(startWord, endWord, dictionary):
	''' Return the length of the shortest transformation path from the 
	startWord to the endWord using words in the given dictionary

	Args:
		startWord (string): The word to start from
		endWord (string): The target word to end at

	Result:
		int: The number of transformations in the shortest path or -1 if there is no path
	'''
	if startWord not in dictionary:
		dictionary.append(startWord)
	if endWord not in dictionary:
		dictionary.append(endWord)
	dictionaryDash = DictionaryDash(dictionary)
	searchPath = dictionaryDash.getShortestTransformationSequence(startWord, endWord)
	if searchPath is None:
		return -1
	return searchPath.numTransformations
