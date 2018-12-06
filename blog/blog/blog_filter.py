from collections import namedtuple
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
import re


class Filter():
    """
    markdown to html interpreter
    """

    HTML_TAGS = {
                    'italic': {
                        True: '<span style="font-style: italic;">',
                        False: '</span>',
                    },
                    'quote': {
                        True: '</p><blockquote><div class="quote-bar"></div>',
                        False: '</blockquote><p>',
                    },
                    'bold': {
                        True: '<b>',
                        False: '</b>',
                    },
                    'code': {
                        True: '<code>',
                        False: '</code>'
                    },
                    'ordered_list': {
                        True: '</p><ol><li>',
                        False: '</li></ol><p>',
                    },
                    'unordered_list': {
                        True: '</p><ul type="square"><li>',
                        False: '</li></ul><p>'
                    },
                    'list_item': {
                        True: '</li><li>',
                        False: '</li><li>',
                    },
                    'heading1': {
                        True: '</p><h1>',
                        False: '</h1><p>',
                    },
                    'heading2': {
                        True: '</p><h2>',
                        False: '</h2><p>',
                    },
                    'heading3': {
                        True: '</p><h3>',
                        False: '</h3><p>',
                    },
                    'heading4': {
                        True: '</p><h4>',
                        False: '</h4><p>',
                    },
                    'heading5': {
                        True: '</p><h5>',
                        False: '</h5><p>',
                    },
                    'heading6': {
                        True: '</p><h6>',
                        False: '</h6><p>',
                    },
                    'horizontal_rule': {
                        True: '</p><hr /><p>',
                        False: '</p><hr /><p>',
                    },
                    'line_break': {
                        True: '</p><br /><p>',
                        False: '</p><br /><p>',
                    },
                    'escape': {
                        True: '',
                        False: '',
                    },
                }

    TAG = namedtuple('Tag', 'name start end open')

    TAG_NAMES = {
                '_': 'italic',
                '>': 'quote',
                '**': 'bold',
                '`': 'code',
                '\n': 'new_line',
                '\n\n': 'line_break',
                '```': 'code_block',
                '\n# ': 'heading1',
                '\n## ': 'heading2',
                '\n### ': 'heading3',
                '\n#### ': 'heading4',
                '\n##### ': 'heading5',
                '\n###### ': 'heading6',
                '\n---': 'horizontal_rule',
                '\n* ': 'unordered_list',
                }

    FORMAT_CHARS = {'_', '>', '*', '`', '\n', }

    def __init__(self, string):

        self.tags = []

        self.open_states = {name: False for name, _ in self.HTML_TAGS.items()}

        self.open_states['code_block'] = False

        self.char_counts = {
                            '*': 0,
                            '`': 0,
                            }

        self.text = string

        self.text_start = 0

        self.text_list = list(string)

        self.tags_slice_start = 0

        self.html_text = ''

        self.new_line_matches = {
                        'ordered_list': re.compile(r'\n[0-9]*\. '),
                        'unordered_list': re.compile(r'\n\* '),
                        'line_break': re.compile(r'\n\n'),
                        'heading1': re.compile(r'\n# '),
                        'heading2': re.compile(r'\n#{2} '),
                        'heading3': re.compile(r'\n#{3} '),
                        'heading4': re.compile(r'\n#{4} '),
                        'heading5': re.compile(r'\n#{5} '),
                        'heading6': re.compile(r'\n#{6} '),
                        'horizontal_rule': re.compile(r'\n---'),
                        }

    def filter_text(self):

        for index, char in enumerate(self.text_list):

            if char in self.FORMAT_CHARS:
                self.identify_markdown(char, index)
            else:
                self.reset_counts()

        return self.scan_tags()

    def identify_markdown(self, format_char, index):

        within_code_block = self.open_states['code_block']
        within_code_inline = self.open_states['code']
        within_code = within_code_block or within_code_inline

        counted_char_checks = []

        tag_parameters = None

        if not within_code:

            if format_char == '\n':

                new_line_tag = self.check_new_line(index)

                if new_line_tag:

                    tag_name, markdown_tag = new_line_tag[0], new_line_tag[1]

                    _ = self.check_new_line_states(tag_name, index)
                    if _:
                        tag_name = _

                    tag_parameters = self.generate_tag_parameters(markdown_tag,
                                                                  index + len(markdown_tag) - 1,
                                                                  tag_name=tag_name)

            elif format_char == '*':

                counted_char_checks = ['bold']

            elif format_char == '`':

                counted_char_checks = ['code', 'code_block']

            else:
                tag_parameters = self.generate_tag_parameters(format_char, index)

        elif within_code_block:

            if format_char == '`':

                counted_char_checks = ['code_block']

        elif within_code_inline:

            if format_char == '`':

                counted_char_checks = ['code']

        if counted_char_checks:

            self.count_char(format_char)
            counted_char_tag = self.check_counted_char(index,
                                                       checks=counted_char_checks)
            if counted_char_tag:
                tag_parameters = self.generate_tag_parameters(counted_char_tag,
                                                              index)

        if tag_parameters:

            self.make_tag(*tag_parameters)
            self.reset_counts()

    def check_counted_char(self, index, checks=[]):

        if 'bold' in checks:
            if self.char_counts['*'] == 2:
                return '**'
        if 'code' in checks:
            if self.char_counts['`'] == 1 and self.text_list[index+1] != '`':
                return '`'
        if 'code_block' in checks:
            if self.char_counts['`'] == 3:
                return '```'

    def count_char(self, input_char):

        for char, _ in self.char_counts.items():
            if char == input_char:
                self.char_counts[char] += 1
            else:
                self.char_counts[char] = 0

    def generate_tag_parameters(self, markdown_tag, index, tag_name=None):

        if tag_name is None:
            tag_name = self.TAG_NAMES[markdown_tag]

        tag_length = len(markdown_tag)
        tag_escaped = self.text_list[index-tag_length] == '\\'

        if not tag_escaped:
            return (tag_name, index-tag_length+1, index+1)
        else:
            return ('escape', index-tag_length, index-tag_length+1)

    def check_new_line(self, tag_start):

        slice = self.text[tag_start:]

        found_match = None

        for name, regex in self.new_line_matches.items():
            match = regex.match(slice)
            if match:
                return name, match[0]

    def check_new_line_states(self, tag_name, tag_start):

        if tag_name == 'ordered_list':
            if self.open_states['ordered_list']:
                return 'list_item'

        elif tag_name == 'unordered_list':
            if self.open_states['unordered_list']:
                return 'list_item'

        if tag_name == 'line_break':
            if self.open_states['ordered_list']:
                return 'ordered_list'
            elif self.open_states['unordered_list']:
                return 'unordered_list'
            elif self.text_list[tag_start-1] != '\n':
                return 'line_break'
            for name, open in self.open_states.items():
                if name.startswith('heading') and open:
                    return name

    def reset_counts(self):

        for char, _ in self.char_counts.items():
            self.char_counts[char] = 0

    def make_tag(self, name, start, end):

        self.flip_tag_open_state(name)
        tag = self.TAG(name, start, end, self.open_states[name])
        self.tags.append(tag)

    def flip_tag_open_state(self, name):

        self.open_states[name] = not self.open_states[name]

    def scan_tags(self):

        for tag_list_index, tag in enumerate(self.tags):

            if tag.name == 'code_block':

                self.preprocess_code_block(tag, tag_list_index)

            else:

                self.insert_tag(tag)

            self.text_start = tag.end

        self.html_text += self.text[self.text_start:]

        return self.html_text

    def insert_tag(self, tag):

        if tag.name == 'ordered_list' and tag.open:
            self.set_list_start_num(tag)

        html_tag = self.HTML_TAGS[tag.name][tag.open]

        escape_in_code_block = tag.name == 'escape' and self.open_states['code_block']

        if not escape_in_code_block:
            self.html_text += self.text[self.text_start:tag.start] + html_tag

    def set_list_start_num(self, tag):

        _num = self.text[tag.start+1:tag.end-2]
        self.HTML_TAGS['ordered_list'][True] = f'</p><ol start="{_num}"><li>'

    def preprocess_code_block(self, tag, tag_list_index):

        if tag.open:

            self.tags_slice_start = tag_list_index

            self.html_text += self.text[self.text_start:tag.start]

        else:

            escaped_text = self.remove_code_block_escapes(tag_list_index)

            self.html_text += '</p></div>' + \
                              highlight(escaped_text, PythonLexer(), HtmlFormatter()) + \
                              '<div><p>'

        self.flip_tag_open_state('code_block')

    def remove_code_block_escapes(self, tag_list_index):

        escaped_text = ''

        tags_slice = self.tags[self.tags_slice_start:tag_list_index+1]

        previous_index = tags_slice[0].start + 3

        for tag in tags_slice:

            if tag.name == 'escape':
                escaped_text += self.text[previous_index:tag.start]
                previous_index = tag.start + 1

        escaped_text += self.text[previous_index:tags_slice[-1].start]

        return escaped_text


    def __repr__(self):

        return self.tags, self.text


def blog_filter(raw_text):

    filter = Filter(raw_text)

    html = filter.filter_text()

    return html
