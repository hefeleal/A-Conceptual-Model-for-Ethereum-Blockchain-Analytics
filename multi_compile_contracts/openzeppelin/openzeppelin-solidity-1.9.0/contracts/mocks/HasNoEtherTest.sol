pragma solidity ^0.4.21;

import "../../contracts/ownership/HasNoEther.sol";


contract HasNoEtherTest is HasNoEther {

  // Constructor with explicit payable — should still fail
  function HasNoEtherTest() public payable {
  }

}
