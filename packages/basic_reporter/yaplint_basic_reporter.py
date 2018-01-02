def reporter(results):
    output = "\n"
    _fmt = "{name} {filename}:{lineno}: {msg} {type}\n"
    for issue in results["errors"]:
        output += _fmt.format(**issue, type="[error]")
    for issue in results["warnings"]:
        output += _fmt.format(**issue, type="[warning]")

    output += "-" * 8 + "\n"
    output += "yaplint found {} errors and {} warnings\n" \
        .format(len(results["errors"]), len(results["warnings"]))
    output += "-" * 8

    return output
