import os

HUNSPELL_DIR = os.path.dirname(__file__)

def stemmer(hspell, word):
	"""
	Uses hunspell to grab the stem of a word.

	:param hspell: hunspell instance to use.
	:param word: word whose stem you want to try to detect.
	:return: word stem.
	"""
	# check lower case first
	word_l = word.lower()
	analysis = hspell.stem(word_l)
	if len(analysis):
		return (word_l, analysis[0].decode("utf-8"))
	
	# proper names Дагестан for example
	word_c = word.capitalize()
	analysis = hspell.stem(word_c)
	if len(analysis):
		return (word_c, analysis[0].decode("utf-8"))
	
	# not found! conservatively assume it's a new word, but liberally assume
	# it's not a proper noun.
	return (word_l, word_l)
