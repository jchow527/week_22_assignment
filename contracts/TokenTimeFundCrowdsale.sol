pragma solidity ^0.5.5;

import "./TokenTimeFund.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/crowdsale/Crowdsale.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/crowdsale/emission/MintedCrowdsale.sol";


contract TokenTimeFundCrowdsale is Crowdsale, MintedCrowdsale { // UPDATE THE CONTRACT SIGNATURE TO ADD INHERITANCE
    
    // Provide parameters for all of the features of your crowdsale, such as the `rate`, `wallet` for fundraising, and `token`.
    constructor(
        uint256 rate, // rate in TKNbits
        address payable wallet, // sale beneficiary
        TokenTimeFund token // The coin that will be used for the ICO.
        ) 
        public Crowdsale(rate, wallet, token)
    {
        // constructor can stay empty
    }
}

contract TokenTimeFundCrowdsaleDeployer {
    // Create an `address public` variable called `tokentime_token_address`.
    address public token_time_address;
    // Create an `address public` variable called `tokentime_crowdsale_address`.
    address public token_time_crowdsale_address;
    // Add the constructor.
    constructor(
        string memory name,
        string memory symbol,
        address payable wallet
    ) 
        public 
    {  
        // Create a new instance of the TokenTimeFund contract.
        TokenTimeFund token = new TokenTimeFund(name, symbol, 0);
        
        // Assign the token contract’s address to the `tokentime_token_address` variable.
        token_time_address = address(token);
        // Create a new instance of the `TokenTimeFund` contract
        TokenTimeFundCrowdsale tokentime_crowdsale = new TokenTimeFundCrowdsale (1, wallet, token);
        // Aassign the `TokenTimeFundCrowdsale` contract’s address to the `tokentime_crowdsale_address` variable.
        token_time_crowdsale_address = address(tokentime_crowdsale);
        // Set the `TokenTimeFundCrowdsale` contract as a minter
        token.addMinter(token_time_crowdsale_address);
        // Have the `TokenTimeFundCrowdsaleDeployer` renounce its minter role.
        token.renounceMinter();
    }
}