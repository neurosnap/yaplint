from yaplint_core import LintRule


class MaxLength(LintRule):
    name = "max_length"

    def __init__(self, options=None):
        if options is None:
            options = {}
        self.code = options.get("code", 80)
        super().__init__(options)

    def match(self, node):
        return True

    def lint_src(self, src, filename, **kwargs):
        lines = src.splitlines(keepends=True)

        for i, line in enumerate(lines):
            line_len = len(line)
            print(line_len)
            if line_len > self.code:
                msg = "max line has been exceeded {} > {}" \
                     .format(line_len, self.code)
                return self.report(
                    None,
                    msg,
                    lineno=i + 1,
                    filename=filename,
                )
        print(lines)


rules = [MaxLength]
