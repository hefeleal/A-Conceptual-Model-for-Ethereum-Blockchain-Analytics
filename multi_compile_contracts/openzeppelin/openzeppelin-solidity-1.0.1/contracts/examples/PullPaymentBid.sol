pragma solidity ^0.4.4;


import '../PullPayment.sol';


contract PullPaymentBid is PullPayment {
  address public highestBidder;
  uint public highestBid;
  
  function bid() external payable {
    if (msg.value <= highestBid) throw;
    
    if (highestBidder != 0) {
      asyncSend(highestBidder, highestBid);
    }
    highestBidder = msg.sender;
    highestBid = msg.value;
  }
}
