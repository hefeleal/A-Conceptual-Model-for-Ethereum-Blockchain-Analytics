pragma solidity ^0.4.4;


import '../PullPayment.sol';


// mock class using PullPayment
contract PullPaymentMock is PullPayment {

  function PullPaymentMock() payable { }

  // test helper function to call asyncSend
  function callSend(address dest, uint amount) {
    asyncSend(dest, amount);
  }

}
