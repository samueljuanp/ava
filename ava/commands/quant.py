import click
from ava.services.quant import Quantitative


class Context:
    def __init__(self, ticker, window):
        self.ticker = ticker
        self.window = window
        self.quant = Quantitative(ticker, window)


@click.group()
@click.option('--ticker', type=str, default='AAPL', help="Yahoo Finance ticker")
@click.option('--window', type=int, default=1095, help="Lookback period in days")
@click.pass_context
def cli(ctx, ticker, window):
    """Quantitative Analysis"""
    ctx.obj = Context(ticker, window)


@cli.command()
@click.pass_context
def beta(ctx):
    """Beta from CAPM with SPY ETF"""
    click.echo(ctx.obj.quant.get_capm_beta())


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
