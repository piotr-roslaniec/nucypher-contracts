// SPDX-License-Identifier: GPL-3.0-or-later

pragma solidity ^0.8.0;

import "../contracts/coordination/ITACoChildToRoot.sol";

interface ITACoChildApplication is ITACoChildToRoot {
    function stakingProviderFromOperator(address _operator) external view returns (address);

    function authorizedStake(address _stakingProvider) external view returns (uint96);

    //TODO: Function to get locked stake duration?
}