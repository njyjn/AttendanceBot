import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

question_bank = {
	'total': 'How many youths came today, total?',
	'l': 'How many servers including yourself?',
	'f':'How many (F)reshies?',
	'nb':'How many (N)ew (B)elievers?',
	'nc':'How many (N)ew (C)omers?',
	'v':'How many (V)isitors?',
	'ir': 'How many (IR)regulars?',
}

question_order = ['total', 'l', 'f', 'ir', 'nb', 'nc', 'v',]

question_limit = len(question_order)
