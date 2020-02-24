pragma solidity ^0.4.4;
import '../token/BasicToken.sol';

// mock class using BasicToken
contract BasicTokenMock is BasicToken {

  function BasicTokenMock(address initialAccount, uint initialBalance) {
    balances[initialAccount] = initialBalance;
    totalSupply = initialBalance;
  }

}
