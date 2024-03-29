"""
## This code is a slightly modified version of bocong's urbandictionary-py library (https://github.com/bocong/urbandictionary-py).
## All rights goes to them, and if they want me to remove this, do let me know. Here's the library's original License text, to avoid getting in legal issues.

The MIT License (MIT)

Copyright (c) 2016 bocong

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
from urllib.parse import quote as urlquote
from urllib.request import urlopen

UD_DEFID_URL = 'https://api.urbandictionary.com/v0/define?defid='
UD_DEFINE_URL = 'https://api.urbandictionary.com/v0/define?term='
UD_RANDOM_URL = 'https://api.urbandictionary.com/v0/random'


class UrbanDefinition(object):
	def __init__(self, word: str, definition: str, example: str, upvotes: int, downvotes: int, permalink: str):
		self.word = word
		self.definition = definition
		self.example = example
		self.upvotes = upvotes
		self.downvotes = downvotes
		self.permalink = permalink

	def __str__(self):
		return '%s: %s%s (%d, %d)' % (
			self.word,
			self.definition[:50],
			'...' if len(self.definition) > 50 else '',
			self.upvotes,
			self.downvotes
		)


def _get_urban_json(url: str):
	f = urlopen(url)
	data = json.loads(f.read().decode('utf-8'))
	f.close()
	return data


def _parse_urban_json(json_: dict, check_result: bool = True) -> list[UrbanDefinition]:
	result = []
	if json_ is None or any(e in json_ for e in ('error', 'errors')):
		raise ValueError('UD: Invalid input for Urban Dictionary API')
	if check_result and ('list' not in json_ or len(json_['list']) == 0):
		return result
	for definition in json_['list']:
		d = UrbanDefinition(
			definition['word'],
			definition['definition'],
			definition['example'],
			int(definition['thumbs_up']),
			int(definition['thumbs_down']),
			definition['permalink']
		)
		result.append(d)
	return result


def define(term: str) -> list[UrbanDefinition]:
	"""Search for term/phrase and return list of UrbanDefinition objects.

	Keyword arguments:
	term -- term or phrase to search for (str)
	"""
	json_ = _get_urban_json(UD_DEFINE_URL + urlquote(term))
	return _parse_urban_json(json_)
