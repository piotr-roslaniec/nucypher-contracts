#!/usr/bin/python3

import os

import click
from ape import config, networks, project
from ape.cli import NetworkBoundCommand, account_option, network_option
from ape.utils import ZERO_ADDRESS
from ape_etherscan.utils import API_KEY_ENV_KEY_MAP


@click.command(cls=NetworkBoundCommand)
@network_option()
@account_option()
@click.option("--currency", default=ZERO_ADDRESS)
@click.option("--rate", default=None)
@click.option("--timeout", default=None)
@click.option("--admin", default=None)
@click.option("--max_size", default=None)
@click.option("--verify/--no-verify", default=True)
def cli(network, account, currency, rate, timeout, admin, max_size, verify):

    deployer = account
    click.echo(f"Deployer: {deployer}")

    if rate and currency == ZERO_ADDRESS:
        raise ValueError("ERC20 contract address needed for currency")

    # Network
    ecosystem_name = networks.provider.network.ecosystem.name
    network_name = networks.provider.network.name
    provider_name = networks.provider.name
    click.echo(f"You are connected to network '{ecosystem_name}:{network_name}:{provider_name}'.")

    # TODO: Move this to a common deployment utilities module
    # Validate Etherscan verification parameters.
    # This import fails if called before the click network options are evaluated
    from scripts.utils import LOCAL_BLOCKCHAIN_ENVIRONMENTS

    is_public_deployment = network_name not in LOCAL_BLOCKCHAIN_ENVIRONMENTS
    if not is_public_deployment:
        verify = False
    elif verify:
        env_var_key = API_KEY_ENV_KEY_MAP.get(ecosystem_name)
        api_key = os.environ.get(env_var_key)
        print(api_key)
        if not api_key:
            raise ValueError(f"{env_var_key} is not set")

    # Use deployment information for currency, if possible
    try:
        deployments = config.deployments[ecosystem_name][network_name]
    except KeyError:
        pass  # TODO: Further validate currency address?
    else:
        print(deployments)
        try:
            currency = next(d for d in deployments if d["contract_type"] == currency)["address"]
        except StopIteration:
            pass

        try:
            stakes = next(d for d in deployments if d["contract_type"] == "TACoChildApplication")[
                "address"
            ]
        except StopIteration:
            raise ValueError("TACoChildApplication deployment needed")

    # Parameter defaults
    admin = admin or deployer
    rate = rate or 1
    timeout = timeout or 60 * 60
    max_size = max_size or 64

    params = (stakes, timeout, max_size, admin, currency, rate)
    print("Deployment parameters:", params)
    return project.Coordinator.deploy(*params, sender=deployer, publish=verify)