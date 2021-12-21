import click
from ava.services.tech import Technical


class Context:
    def __init__(self, ticker):
        self.ticker = ticker
        self.compute = Technical()


@click.group()
@click.option('--ticker', type=str, default='AAPL', help="Yahoo Finance ticker")
@click.pass_context
def cli(ctx, ticker):
    """Technical Analysis"""
    ctx.obj = Context(ticker)


@cli.command()
@click.pass_context
def macd(ctx):
    """Moving Average Convergence Divergence"""
    click.echo(ctx.obj.ticker)


@cli.command()
@click.pass_context
def rsi(ctx):
    """Relative Strength Index"""
    click.echo(ctx.obj.ticker)


@cli.command()
@click.pass_context
def stoch(ctx):
    """Full Stochastic K and D"""
    click.echo(ctx.obj.ticker)
