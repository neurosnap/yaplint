from importlib import import_module
import click

from yaplint_core import lint_runner


@click.command()
@click.argument("path")
@click.option("--rules")
@click.option("--reporter", default="basic_reporter")
def yaplint(path, rules, reporter):
    irules = []
    for rule in rules.split(","):
        mod = import_module("yaplint_{}".format(rule))
        irules = irules + [Rule() for Rule in mod.rules]

    reporter = import_module("yaplint_{}".format(reporter)).reporter
    results = lint_runner(path, irules)
    output = reporter(results)
    click.echo(output)


if __name__ == "__main__":
    yaplint()
