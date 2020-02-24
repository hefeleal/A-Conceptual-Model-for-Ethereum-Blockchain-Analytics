pragma solidity ^0.4.4;


import '../PullPayment.sol';
import '../Stoppable.sol';


contract StoppableBid is Stoppable, PullPayment {
  address public highestBidder;
  uint public highestBid;

  function bid() external payable stopInEmergency {
    if (msg.value <= highestBid) throw;
    
    if (highestBidder != 0) {
      asyncSend(highestBidder, highestBid);
    }
    highestBidder = msg.sender;
    highestBid = msg.value;
  }

  function withdraw() onlyInEmergency {
    selfdestruct(owner);
  }

}
