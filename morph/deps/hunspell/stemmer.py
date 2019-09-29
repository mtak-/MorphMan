import os

HUNSPELL_DIR = os.path.dirname(__file__)

def stemmer(hspell, word):
	"""
	Uses hunspell to grab the stem of a word.

	:param hspell: hunspell instance to use.
	:param word: word whose stem you want to try to detect.
	:return: word stem.
	"""
	analysis = hspell.stem(word)
	if len(analysis):
		return analysis[0].decode("utf-8")
	else:
		return word
