# Dictionary representing the morse code chart
MORSE_CODE_DICT = {'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----', ', ': '--..--', '.': '.-.-.-', '?': '..--..', '/': '-..-.', '-': '-....-', '(': '-.--.', ')': '-.--.-', ',': '--..--'}
LETTERS_DICT = {v: k for k, v in MORSE_CODE_DICT.items()}
letters = MORSE_CODE_DICT.keys()
morse_letters = MORSE_CODE_DICT.values()


def check_letter(message: str, *, cipher: bool) -> bool:
	message = message.strip().upper()

	res = True
	if cipher:
		check = list(letters)
		check.append(' ')
	else:
		check = morse_letters
		message = message.replace(' / ', ' ').split(' ')

	for letter in message:
		if letter not in check and letter != ' ':
			res = False
	return res


def encrypt(message: str) -> str:
	message = message.upper()

	my_cipher = ''
	for myletter in message:
		if myletter != ' ':
			my_cipher += MORSE_CODE_DICT[myletter] + ' '
		else:
			my_cipher += '/ '
	return my_cipher


# This function is used to decrypt Morse code to English
def decrypt(message: str) -> str:
	message = message.strip()
	output = ''

	words = [word.split(' ') for word in message.split(' / ')]

	for word in words:
		for letter in word:
			output += LETTERS_DICT[letter]
		output += ' '

	return output.strip()
