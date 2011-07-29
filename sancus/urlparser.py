import re
import logging

logger = logging.getLogger(__name__)

class TemplateCompiler(object):
    option_split = re.compile(r'([\[\]\$])')
    lookup_split = re.compile(r'({[^{}]+})')
    lookup_key_values = re.compile(r'([^:]+)(?::(.+))?$')
    escape_re = re.compile(r'([\.\?\+\&])')

    def escape(self, literal):
        return self.escape_re.sub(r'\\\1', literal)

    def __call__(self, template):
        result = [ '^' ]

        for chunk in self.option_split.split(template):
            if len(chunk) > 1:
                s = self.step2(chunk)
                result.append(s)
            elif chunk == '[':
                result.append(r'(')
            elif chunk == ']':
                result.append(r')?')
            elif chunk == '$':
                result.append(r'$')
            elif len(chunk) == 1:
                result.append(self.escape(chunk))

        result = ''.join(result)
        logger.debug("compile(%r): %s" % (template, result))
        return result

    def step2(self, template):
        result = []
        for chunk in self.lookup_split.split(template):
            if len(chunk) > 2:
                if chunk[0] == '{' and chunk[-1] == '}':
                    s = self.step3(chunk[1:-1])
                else:
                    s = self.escape(chunk)
            elif len(chunk) == 0:
                continue
            else:
                s = self.escape(chunk)

            result.append(s)

        result = ''.join(result)
        logger.debug("step2(%r): %s" % (template, result))
        return result

    def step3(self, template):
        m = self.lookup_key_values.match(template)
        assert m, "{%s} bad formed" % template
        m = m.groups()

        name = m[0]
        if m[1] == None:
            s = '[^/]+'
        else:
            s = m[1].split('|')
            for i in range(len(s)):
                s[i] = self.escape(s[i])

            if len(s) > 1:
                s = '(%s)' % '|'.join(s)
            else:
                s = s[0]

        result = r'(?P<%s>%s)' % (name, s)
        logger.debug("step3('{%s}'): %s" % (template, result))
        return result

    def match(self, regex, s):
        m = regex.match(s)
        if not m:
            return False, None, None, None, None

        return True, (), m.groupdict(), s[:m.end()], s[m.end():]
