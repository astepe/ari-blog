from collections import namedtuple
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


class Filter():
    """
    used for tracking the open and closed state of tags
    while determining tag locations within input text
    """

    HTML_TAGS = {'italic': {True: '<span style="font-style: italic;">', False: '</span>'},
                 'quote': {True: '</p><blockquote><div class="quote-bar"></div>', False: '</blockquote><p>'},
                 'bold': {True: '<b>', False: '</b>'},
                 'code': {True: '<code>', False: '</code>'},
                 'escape': {True: '', False: ''}
                 }

    TAG = namedtuple('Tag', 'tag_type index open')

    FORMAT_CHARS = {'_': 'italic', '`': 'code', '>': 'quote', '*': 'bold'}

    def __init__(self, string):

        self.tags = []

        self.open_states = {'italic': False,
                            'code': False,
                            'quote': False,
                            'bold': False,
                            'code_block': False,
                            'escape': False}

        self.star_count, self.tick_count = 0, 0

        self.text = string

        self.text_list = list(string)

        self.tags_slice_start = 0

        self.html_text = ''

    def inspect_char(self, tag_type, index):

        within_code_block = self.open_states['code_block']
        within_code_inline = self.open_states['code']
        within_code = within_code_block or within_code_inline

        if tag_type == 'bold':

            self.count_bold()

            if not within_code:

                self.check_bold(index)

        elif tag_type == 'code':

            self.count_code()

            if self.tick_count == 3:

                self.check_escape('code_block', index-2, index-3)

            elif not within_code_block:

                self.check_code(index)

        elif not within_code:

            self.check_escape(tag_type, index, index-1)

    def count_bold(self):

        self.star_count += 1
        self.tick_count = 0

    def check_bold(self, index):

        if self.star_count == 2:

            self.check_escape('bold', index-1, index-2)

    def count_code(self):

        self.tick_count += 1
        self.star_count = 0

    def check_escape(self, tag_type, tag_index, escape_index):

        if self.text_list[escape_index] == '\\':
            self.make_tag('escape', escape_index)
        else:
            self.make_tag(tag_type, tag_index)

    def check_code(self, index):

        if self.tick_count == 1 and self.text_list[index+1] != '`':

            self.check_escape('code', index, index-1)

    def reset_counts(self):

        self.star_count, self.tick_count = 0, 0

    def make_tag(self, tag_type, index):

        self.flip_state(tag_type)
        tag = self.TAG(tag_type, index, self.open_states[tag_type])
        self.tags.append(tag)
        self.reset_counts()

    def insert_tags(self):

        previous_tag_index = 0

        for current_index, tag in enumerate(self.tags):

            if tag.tag_type == 'code_block':

                self.preprocess_code_block(tag, previous_tag_index, current_index)

            else:

                html_tag = self.HTML_TAGS[tag.tag_type][tag.open]

                escape_in_code_block = tag.tag_type == 'escape' and self.open_states['code_block']

                if not escape_in_code_block:
                    self.html_text += self.text[previous_tag_index:tag.index] + html_tag

            previous_tag_index = tag.index + self.get_offset(tag.tag_type)

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

        self.flip_state('code_block')

    def remove_code_block_escapes(self, current_index):

        escaped_text = ''

        tags_slice = self.tags[self.tags_slice_start:current_index+1]

        previous_index = tags_slice[0].index + 3

        for tag in tags_slice:

            if tag.tag_type == 'escape':
                escaped_text += self.text[previous_index:tag.index]
                previous_index = tag.index + 1

        escaped_text += self.text[previous_index:tags_slice[-1].index]

        return escaped_text

    def flip_state(self, tag_type):

        self.open_states[tag_type] = not self.open_states[tag_type]

    def get_offset(self, tag_type):

        if tag_type == 'code_block':
            return 3
        elif tag_type == 'bold':
            return 2
        else:
            return 1

    def __repr__(self):

        return self.tags, self.text


def blog_filter(raw_text):

    filter = Filter(raw_text)

    for index, char in enumerate(filter.text_list):

        if char in filter.FORMAT_CHARS:
            tag_type = filter.FORMAT_CHARS[char]
            filter.inspect_char(tag_type, index)
        else:
            filter.reset_counts()

    html = filter.insert_tags()

    return html
