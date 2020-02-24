module.exports = function(deployer) {
  deployer.deploy(PullPaymentBid);
  deployer.deploy(BadArrayUse);
  deployer.deploy(ProofOfExistence);
  deployer.deploy(Ownable);
  deployer.deploy(Claimable);
  deployer.deploy(LimitBalance);
  if(deployer.network == 'test'){
    deployer.deploy(SecureTargetBounty);
    deployer.deploy(InsecureTargetBounty);
  };
};
