import click
from ava.services.quant import Quantitative


class Context:
    def __init__(self, ticker, window):
        self.ticker = ticker
        self.window = window
        self.quant = Quantitative(ticker, window)


@click.group()
@click.option('--ticker', type=str, default='SPY', help="Yahoo Finance ticker")
@click.option('--window', type=int, default=3650, help="Lookback period in days")
@click.pass_context
def cli(ctx, ticker, window):
    """Quantitative Analysis"""
    ctx.obj = Context(ticker, window)


@cli.command()
@click.pass_context
def alpha(ctx):
    """Alpha from Carhart 4-Factor Model"""
    click.echo(ctx.obj.quant.get_alpha())


@cli.command()
@click.pass_context
def beta(ctx):
    """Beta from Carhart 4-Factor Model"""
    click.echo(ctx.obj.quant.get_beta())


@cli.command()
@click.pass_context
def regress(ctx):
    """Regression Summary Table"""
    click.echo(ctx.obj.quant.get_regression_summary())


@cli.command()
@click.pass_context
def profile(ctx):
    """Risk-Adjusted Return Profile"""
    click.echo(ctx.obj.quant.get_risk_return_profile())
