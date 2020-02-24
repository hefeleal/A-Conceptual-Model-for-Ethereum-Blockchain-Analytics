pragma solidity ^0.4.8;


import '../../contracts/lifecycle/Pausable.sol';


// mock class using Pausable
contract PausableMock is Pausable {
  bool public drasticMeasureTaken;
  uint public count;

  function PausableMock() {
    drasticMeasureTaken = false;
    count = 0;
  }

  function normalProcess() external stopInEmergency {
    count++;
  }

  function drasticMeasure() external onlyInEmergency {
    drasticMeasureTaken = true;
  }

}
