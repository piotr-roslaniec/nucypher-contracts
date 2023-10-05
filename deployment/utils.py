import os
from pathlib import Path
from typing import List

from ape import networks
from ape.contracts import ContractInstance
from ape_etherscan.utils import API_KEY_ENV_KEY_MAP

from deployment.constants import (
    CURRENT_NETWORK,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS
)


def check_registry_filepath(registry_filepath: Path) -> None:
    """
    Checks that the registry_filepath does not exist,
    and that its parent directory does exist.
    """
    if registry_filepath.exists():
        raise FileExistsError(f"Registry file already exists at {registry_filepath}")
    if not registry_filepath.parent.exists():
        raise FileNotFoundError(f"Parent directory of {registry_filepath} does not exist.")


def check_etherscan_plugin() -> None:
    """
    Checks that the ape-etherscan plugin is installed and that
    the appropriate API key environment variable is set.
    """
    if CURRENT_NETWORK in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        # unnecessary for local deployment
        return
    try:
        import ape_etherscan  # noqa: F401
    except ImportError:
        raise ImportError("Please install the ape-etherscan plugin to use this script.")
    ecosystem_name = networks.provider.network.ecosystem.name
    explorer_envvar = API_KEY_ENV_KEY_MAP.get(ecosystem_name)
    api_key = os.environ.get(explorer_envvar)
    if not api_key:
        raise ValueError(f"{explorer_envvar} is not set.")


def check_infura_plugin() -> None:
    """Checks that the ape-infura plugin is installed."""
    if CURRENT_NETWORK in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return  # unnecessary for local deployment
    try:
        import ape_infura  # noqa: F401
        from ape_infura.provider import _ENVIRONMENT_VARIABLE_NAMES  # noqa: F401
    except ImportError:
        raise ImportError("Please install the ape-infura plugin to use this script.")
    for envvar in _ENVIRONMENT_VARIABLE_NAMES:
        api_key = os.environ.get(envvar)
        if api_key:
            break
    else:
        raise ValueError(
            f"No Infura API key found in "
            f"environment variables: {', '.join(_ENVIRONMENT_VARIABLE_NAMES)}"
        )


def verify_contracts(contracts: List[ContractInstance]) -> None:
    explorer = networks.provider.network.explorer
    for instance in contracts:
        print(f"(i) Verifying {instance.contract_type.name}...")
        explorer.publish_contract(instance.address)


def check_plugins() -> None:
    check_etherscan_plugin()
    check_infura_plugin()


def check_deployment_ready(registry_filepath: Path) -> None:
    check_plugins()
    check_registry_filepath(registry_filepath=registry_filepath)