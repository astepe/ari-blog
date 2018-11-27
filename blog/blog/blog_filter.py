from collections import namedtuple
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
import re


class Filter():
    """
    used for tracking the open and closed state of tags
    while determining tag locations within input text
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
                    'escape': {
                        True: '',
                        False: '',
                    },
                }

    TAG = namedtuple('Tag', 'type index index_offset open')

    MARKUP_TAGS = {
                    '_': 'italic',
                    '>': 'quote',
                    '**': 'bold',
                    '`': 'code',
                    '\n': 'new_line',
                    '```': 'code_block',
                    }

    FORMAT_CHARS = {'_', '>', '*', '`', '\n'}

    def __init__(self, string):

        self.tags = []

        self.open_states = {
                            'italic': False,
                            'quote': False,
                            'bold': False,
                            'code': False,
                            'code_block': False,
                            'escape': False,
                            'ordered_list': False,
                            'unordered_list': False,
                            'list_item': False,
                            }

        self.star_count, self.tick_count = 0, 0

        self.text = string

        self.text_list = list(string)

        self.tags_slice_start = 0

        self.html_text = ''

    def inspect_char(self, format_char, index):

        within_code_block = self.open_states['code_block']
        within_code_inline = self.open_states['code']
        within_code = within_code_block or within_code_inline

        if format_char == '\n':

            if not within_code:

                self.check_list(index)

        elif format_char == '*':

            self.count_star()

            if not within_code:

                self.check_bold(index)

        elif format_char == '`':

            self.count_tick()

            if self.tick_count == 3:

                self.check_escape('```', index-2, index-3)

            elif not within_code_block:

                self.check_code(index)

        elif not within_code:

            self.check_escape(format_char, index, index-1)

    def check_bold(self, index):

        if self.star_count == 2:

            self.check_escape('**', index-1, index-2)

    def check_code(self, index):

        if self.tick_count == 1 and self.text_list[index+1] != '`':

            self.check_escape('`', index, index-1)

    def check_list(self, index):

        within_ol = self.open_states['ordered_list']
        within_ul = self.open_states['unordered_list']

        ol_start = re.compile(r'\n[0-9]*\. ')
        ul_start = re.compile(r'\n\* ')
        list_end = re.compile(r'\n\n')

        ol_start_match = ol_start.match(self.text[index:])
        ul_start_match = ul_start.match(self.text[index:])
        list_end_match = list_end.match(self.text[index:])

        if ol_start_match:

            index_offset = len(ol_start_match[0])

            if within_ol:
                self.make_tag('list_item', index, index_offset)
            else:
                self.make_tag('ordered_list', index, index_offset)

        elif ul_start_match:

            if within_ul:
                self.make_tag('list_item', index, 3)
            else:
                self.make_tag('unordered_list', index, 3)

        elif list_end_match:

            if within_ul:
                self.make_tag('unordered_list', index, 2)
            elif within_ol:
                self.make_tag('ordered_list', index, 2)

    def count_tick(self):

        self.tick_count += 1
        self.star_count = 0

    def count_star(self):

        self.star_count += 1
        self.tick_count = 0

    def check_escape(self, markup_tag, tag_index, escape_index):

        if self.text_list[escape_index] == '\\':
            self.make_tag('escape', escape_index, 1)
        else:
            tag_type = self.MARKUP_TAGS[markup_tag]
            self.make_tag(tag_type, tag_index, len(markup_tag))

    def reset_counts(self):

        self.star_count, self.tick_count = 0, 0

    def make_tag(self, tag_type, index, index_offset):

        self.flip_tag_open_state(tag_type)
        tag = self.TAG(tag_type, index, index_offset, self.open_states[tag_type])
        self.tags.append(tag)
        self.reset_counts()

    def insert_tags(self):

        previous_tag_index = 0

        for current_index, tag in enumerate(self.tags):

            if tag.type == 'code_block':

                self.preprocess_code_block(tag, previous_tag_index, current_index)

            else:

                if tag.type == 'ordered_list' and tag.open:
                    _num = self.text[tag.index+1:tag.index_offset-2]
                    self.HTML_TAGS['ordered_list'][True] = f'</p><ol start="{_num}"><li>'
                html_tag = self.HTML_TAGS[tag.type][tag.open]

                escape_in_code_block = tag.type == 'escape' and self.open_states['code_block']

                if not escape_in_code_block:
                    self.html_text += self.text[previous_tag_index:tag.index] + html_tag

            previous_tag_index = tag.index + tag.index_offset

        self.html_text += self.text[previous_tag_index:]

        return self.html_text

    def preprocess_code_block(self, tag, previous_tag_index, current_index):

        if tag.open:

            self.tags_slice_start = current_index

            self.html_text += self.text[previous_tag_index:tag.index]

        else:

            escaped_text = self.remove_code_block_escapes(current_index)

            self.html_text += '</p></div>' + \
                              highlight(escaped_text, PythonLexer(), HtmlFormatter()) + \
                              '<div><p>'

        self.flip_tag_open_state('code_block')

    def remove_code_block_escapes(self, current_index):

        escaped_text = ''

        tags_slice = self.tags[self.tags_slice_start:current_index+1]

        previous_index = tags_slice[0].index + 3

        for tag in tags_slice:

            if tag.type == 'escape':
                escaped_text += self.text[previous_index:tag.index]
                previous_index = tag.index + 1

        escaped_text += self.text[previous_index:tags_slice[-1].index]

        return escaped_text

    def flip_tag_open_state(self, type):

        self.open_states[type] = not self.open_states[type]

    def __repr__(self):

        return self.tags, self.text


def blog_filter(raw_text):

    filter = Filter(raw_text)

    for index, char in enumerate(filter.text_list):

        if char in filter.FORMAT_CHARS:
            filter.inspect_char(char, index)
        else:
            filter.reset_counts()

    html = filter.insert_tags()

    return html
