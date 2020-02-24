pragma solidity ^0.4.4;


import {Bounty, Target} from "../Bounty.sol";


contract InsecureTargetMock is Target {
  function checkInvariant() returns(bool){
    return false;
  }
}

contract InsecureTargetBounty is Bounty {
  function deployContract() internal returns (address) {
    return new InsecureTargetMock();
  }
}
