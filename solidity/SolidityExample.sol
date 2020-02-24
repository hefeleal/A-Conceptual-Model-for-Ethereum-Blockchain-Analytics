pragma solidity ^0.4.25;
contract SolidityExample {
  address owner;
  bool isRunning;
  uint256 highestBid;
  address highestBidder;
  mapping(address => uint256) oldBids;
  event NewHighestBid(address bidder, uint256 amount);

  modifier onlyBy(address who) {
    require(msg.sender == who, "not authorized");
    _;
  }
  constructor() public {
    owner = msg.sender;
    isRunning = true;
    highestBid = 0;
    highestBidder = 0;
  }
  function placeBid() public payable {
    require(isRunning, "auction has already ended");
    require(msg.value > highestBid, "bid is too low");

    if(highestBid > 0) {
      oldBids[highestBidder] += highestBid;
    }
    highestBid = msg.value;
    highestBidder = msg.sender;
    emit NewHighestBid(highestBidder, highestBid);
  }
  function withdraw() public {
    uint256 amount = oldBids[msg.sender];
    if(amount > 0) {
      msg.sender.transfer(amount);
      oldBids[msg.sender] = 0;
    }
  }
  function getOldBidFor(address bidder) public view returns (uint256) {
    return oldBids[bidder];
  }
  function endAuction() public onlyBy(owner) {
    if(isRunning) {
      isRunning = false;
      owner.transfer(highestBid);
    }
  }
  function() public { }
}
