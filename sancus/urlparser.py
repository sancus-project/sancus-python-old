import re
import logging

logger = logging.getLogger('sancus.urlparser')

class TemplateCompiler(object):
    splitter1 = re.compile(r'([\[\]])')
    splitter2 = re.compile(r'({[^{}]+})')

    def __call__(self, template):
        if template[-1] == '$':
            has_end = True
            template1 = template[:-1]
        else:
            has_end = False
            template1 = template

        result = [ '^' ]

        for chunk in self.splitter1.split(template1):
            if len(chunk) > 1:
                s = self.step2(chunk)
                result.append(s)
            elif chunk == '[':
                result.append(r'(')
            elif chunk == ']':
                result.append(r')?')
            elif len(chunk) == 1:
                s = self.literal(chunk)
                result.append(s)

        if has_end:
            result.append('$')

        result = ''.join(result)
        logger.info("compile(%r): %s" % (template, result))
        return result

    def literal(self, template):
        return re.escape(template)

    def step2(self, template):
        result = []
        for chunk in self.splitter2.split(template):
            if len(chunk) > 2:
                if chunk[0] == '{' and chunk[-1] == '}':
                    s = self.step3(chunk[1:-1])
                else:
                    s = self.literal(chunk)
            elif len(chunk) == 0:
                continue
            else:
                s = self.literal(chunk)

            result.append(s)

        result = ''.join(result)
        logger.debug("step2(%r): %s" % (template, result))
        return result

    def step3(self, template):
        result = r'(?P<%s>[^/]+)' % template
        logger.debug("step3('{%s}'): %s" % (template, result))
        return result
