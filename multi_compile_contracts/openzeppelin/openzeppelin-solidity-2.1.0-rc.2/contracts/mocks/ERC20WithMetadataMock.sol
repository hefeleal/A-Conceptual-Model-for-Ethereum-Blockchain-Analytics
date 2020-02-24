pragma solidity ^0.5.0;

import "../token/ERC20/ERC20.sol";
import "../drafts/ERC1046/TokenMetadata.sol";

contract ERC20WithMetadataMock is ERC20, ERC20WithMetadata {
    constructor (string memory tokenURI) public ERC20WithMetadata(tokenURI) {}
}
