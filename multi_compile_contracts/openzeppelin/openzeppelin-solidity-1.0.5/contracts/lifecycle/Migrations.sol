pragma solidity ^0.4.8;


import '../ownership/Ownable.sol';


// This is a truffle contract, needed for truffle integration, not meant for use by Zeppelin users. 
contract Migrations is Ownable {
  uint public lastCompletedMigration;

  function setCompleted(uint completed) onlyOwner {
    lastCompletedMigration = completed;
  }

  function upgrade(address newAddress) onlyOwner {
    Migrations upgraded = Migrations(newAddress);
    upgraded.setCompleted(lastCompletedMigration);
  }
}
