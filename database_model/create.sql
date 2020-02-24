CREATE USER IF NOT EXISTS 'ethuser'@'localhost' IDENTIFIED BY 'wEXaJV266kpCZm09EU8H';

CREATE DATABASE IF NOT EXISTS eth;


CREATE TABLE IF NOT EXISTS eth.block
(
  blockNumber INTEGER PRIMARY KEY,
  hash CHAR(66) NOT NULL UNIQUE,
  timestamp DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS eth.contractTransaction
(
  hash CHAR(66) PRIMARY KEY,
  txValue VARCHAR(30) NOT NULL,
  nonce INTEGER NOT NULL,
  input LONGTEXT,
  txIndex INTEGER NOT NULL,
  gas VARCHAR(30) NOT NULL,
  gasPrice VARCHAR(30) NOT NULL,
  blockNumber INTEGER NOT NULL REFERENCES eth.block(blockNumber),
  txFrom CHAR(42) NOT NULL,
  txTo CHAR(42)
);

CREATE INDEX ct_from_index
ON eth.contractTransaction (txFrom);

CREATE INDEX ct_blocknumber_index
ON eth.contractTransaction (blockNumber);

CREATE TABLE IF NOT EXISTS eth.contractCode
(
  hash CHAR(66) PRIMARY KEY,
  code LONGTEXT NOT NULL,
  hasCreateOpcode BOOLEAN NOT NULL,
  occurrences INTEGER NOT NULL,
  minCompilerVersion VARCHAR(64),
  maxCompilerVersion VARCHAR(64),
  minSafeMathVersion VARCHAR(64),
  maxSafeMathVersion VARCHAR(64),
  verifiedSourceCodeID INT(20),
  isUsingSafeMath BOOLEAN
);

CREATE TABLE IF NOT EXISTS eth.contract
(
  address CHAR(42) NOT NULL,
  contractHash CHAR(66) NOT NULL REFERENCES eth.contractCode(hash),
  transactionHash CHAR(66) REFERENCES eth.contractTransaction(hash),
  contractCreationCode LONGTEXT,
  constructorArguments LONGTEXT,
  selfdestructed BOOLEAN,
  origin INTEGER NOT NULL,
  PRIMARY KEY (address, origin)
);

CREATE INDEX contract_hash_index
ON eth.contract (contractHash);

CREATE TABLE IF NOT EXISTS eth.contractCreatedContract
(
  address CHAR(42),
  contractHash CHAR(66) NOT NULL REFERENCES eth.contractCode(hash),
  creatorAddress CHAR(42) NOT NULL,
  nonceUsed INTEGER NOT NULL,
  generation INTEGER NOT NULL,
  origin INTEGER NOT NULL,
  PRIMARY KEY (address, origin)
);

CREATE INDEX contract_created_contract_hash_index
ON eth.contractCreatedContract (contractHash);

CREATE TABLE IF NOT EXISTS eth.functions (
  id INT(9) NOT NULL,
  hash VARCHAR(10) NOT NULL,
  interface TEXT NOT NULL
);

-- releaseDate in UTC
CREATE TABLE IF NOT EXISTS eth.compiler (
  id INT(9) NOT NULL,
  version VARCHAR(64) NOT NULL,
  longVersion VARCHAR(64) NOT NULL,
  releaseDate DATETIME NOT NULL,
  PRIMARY KEY (id)
);

INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (0, "0.1.1", "soljson-v0.1.1+commit.6ff4cd6.js", "2015-08-04 09:12:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (1, "0.1.2", "soljson-v0.1.2+commit.d0d36e3.js", "2015-08-21 11:03:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (2, "0.1.3", "soljson-v0.1.3+commit.28f561.js", "2015-09-22 23:25:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (3, "0.1.4", "soljson-v0.1.4+commit.5f6c3cd.js", "2015-09-30 15:05:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (4, "0.1.5", "soljson-v0.1.5+commit.23865e3.js", "2015-10-07 16:45:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (5, "0.1.6", "soljson-v0.1.6+commit.d41f8b7.js", "2015-10-16 15:02:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (6, "0.1.7", "soljson-v0.1.7+commit.b4e666c.js", "2015-11-17 15:12:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (7, "0.2.0", "soljson-v0.2.0+commit.4dc2445.js", "2015-12-01 15:21:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (8, "0.2.1", "soljson-v0.2.1+commit.91a6b35.js", "2016-01-30 16:40:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (9, "0.2.2", "soljson-v0.2.2+commit.ef92f56.js", "2016-02-17 18:27:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (10, "0.3.0", "soljson-v0.3.0+commit.11d6736.js", "2016-03-11 16:58:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (11, "0.3.1", "soljson-v0.3.1+commit.c492d9b.js", "2016-03-31 16:49:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (12, "0.3.2", "soljson-v0.3.2+commit.81ae2a7.js", "2016-04-18 17:34:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (13, "0.3.3", "soljson-v0.3.3+commit.4dc1cb1.js", "2016-05-27 17:02:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (14, "0.3.4", "soljson-v0.3.4+commit.7dab890.js", "2016-05-31 21:23:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (15, "0.3.5", "soljson-v0.3.5+commit.5f97274.js", "2016-06-10 16:02:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (16, "0.3.6", "soljson-v0.3.6+commit.3fc68da.js", "2016-08-10 19:09:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (17, "0.4.0", "soljson-v0.4.0+commit.acd334c9.js", "2016-09-08 14:22:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (18, "0.4.1", "soljson-v0.4.1+commit.4fc6fc2c.js", "2016-09-09 10:38:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (19, "0.4.2", "soljson-v0.4.2+commit.af6afb04.js", "2016-09-17 13:36:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (20, "0.4.3", "soljson-v0.4.3+commit.2353da71.js", "2016-10-25 13:53:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (21, "0.4.4", "soljson-v0.4.4+commit.4633f3de.js", "2016-11-01 08:53:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (22, "0.4.5", "soljson-v0.4.5+commit.b318366e.js", "2016-11-21 11:26:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (23, "0.4.6", "soljson-v0.4.6+commit.2dabbdf0.js", "2016-11-22 14:35:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (24, "0.4.7", "soljson-v0.4.7+commit.822622cf.js", "2016-12-15 13:00:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (25, "0.4.8", "soljson-v0.4.8+commit.60cc1668.js", "2017-01-13 12:40:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (26, "0.4.9", "soljson-v0.4.9+commit.364da425.js", "2017-01-31 18:33:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (27, "0.4.10", "soljson-v0.4.10+commit.f0d539ae.js", "2017-03-15 17:22:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (28, "0.4.11", "soljson-v0.4.11+commit.68ef5810.js", "2017-05-03 12:59:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (29, "0.4.12", "soljson-v0.4.12+commit.194ff033.js", "2017-07-03 16:47:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (30, "0.4.13", "soljson-v0.4.13+commit.fb4cb1a.js", "2017-07-06 11:13:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (31, "0.4.14", "soljson-v0.4.14+commit.c2215d46.js", "2017-07-31 14:55:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (32, "0.4.15", "soljson-v0.4.15+commit.bbb8e64f.js", "2017-08-08 17:02:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (33, "0.4.16", "soljson-v0.4.16+commit.d7661dd9.js", "2017-08-24 20:31:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (34, "0.4.17", "soljson-v0.4.17+commit.bdeb9e52.js", "2017-09-21 15:40:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (35, "0.4.18", "soljson-v0.4.18+commit.9cf6e910.js", "2017-10-18 13:39:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (36, "0.4.19", "soljson-v0.4.19+commit.c4cbbb05.js", "2017-11-30 16:48:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (37, "0.4.20", "soljson-v0.4.20+commit.3155dd80.js", "2018-02-14 07:44:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (38, "0.4.21", "soljson-v0.4.21+commit.dfe3193c.js", "2018-03-08 06:45:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (39, "0.4.22", "soljson-v0.4.22+commit.4cb486ee.js", "2018-04-17 05:11:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (40, "0.4.23", "soljson-v0.4.23+commit.124ca40d.js", "2018-04-19 21:18:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (41, "0.4.24", "soljson-v0.4.24+commit.e67f0147.js", "2018-05-16 14:09:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (42, "0.4.25", "soljson-v0.4.25+commit.59dbf8f1.js", "2018-09-13 18:03:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (43, "0.5.0", "soljson-v0.5.0+commit.1d4f565a.js", "2018-11-13 19:36:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (44, "0.5.1", "soljson-v0.5.1+commit.c8a2cb62.js", "2018-12-03 15:32:00");
INSERT INTO eth.compiler (id, version, longVersion, releaseDate)
VALUES (45, "0.5.2", "soljson-v0.5.2+commit.1df8f40c.js", "2018-12-19 18:25:00");

-- releaseDate in UTC
CREATE TABLE IF NOT EXISTS eth.library (
  id INT(9) NOT NULL AUTO_INCREMENT,
  name VARCHAR(64) NOT NULL,
  version VARCHAR(64) NOT NULL,
  releaseDate DATETIME NOT NULL,
  functions VARCHAR(2048) NOT NULL,
  PRIMARY KEY (id)
);

INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "1.0.0", "2016-11-24 04:23:00", "mul,add,sub");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "1.0.1", "2017-01-05 18:39:00", "mul,add,sub");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "1.0.2", "2017-02-23 15:57:00", "mul,add,sub,div");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "1.0.3", "2017-03-06 14:15:00", "mul,add,sub,div");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "1.0.4", "2017-03-09 18:08:00", "mul,add,sub,div");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "1.0.5", "2017-05-09 19:16:00", "mul,add,sub,div");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "1.0.6", "2017-05-29 21:40:00", "mul,add,sub,div");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "1.0.7", "2017-06-09 22:31:00", "mul,add,sub,div");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "1.1.0", "2017-07-02 22:04:00", "mul,add,sub,div");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "1.2.0", "2017-07-18 18:20:00", "mul,add,sub,div");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "1.3.0", "2017-09-21 19:02:00", "mul,add,sub,div");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "1.4.0", "2017-11-23 20:12:00", "mul,add,sub,div");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "1.5.0", "2017-12-22 23:21:00", "mul,add,sub,div");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "1.6.0", "2018-01-23 21:04:00", "mul,add,sub,div");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "1.7.0", "2018-02-20 21:39:00", "mul,add,sub,div");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "1.8.0", "2018-03-23 18:27:00", "mul,add,sub,div");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "1.9.0", "2018-04-27 15:51:00", "mul,add,sub,div");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "1.10.0", "2018-06-05 21:29:00", "mul,add,sub,div");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "1.11.0.RC1", "2018-07-04 17:35:00", "mul,add,sub,div");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "1.11.0", "2018-07-13 23:19:00", "mul,add,sub,div");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "1.12.0.RC1", "2018-08-01 19:53:00", "mul,add,sub,div");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "1.12.0.RC2", "2018-08-11 20:26:00", "mul,add,sub,div");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "1.12.0", "2018-08-11 20:55:00", "mul,add,sub,div");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "2.0.0.RC1", "2018-09-07 18:00:00", "mul,add,sub,div,mod");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "2.0.0.RC2", "2018-09-18 22:49:00", "mul,add,sub,div,mod");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "2.0.0.RC3", "2018-10-04 14:31:00", "mul,add,sub,div,mod");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "2.0.0.RC4", "2018-10-21 00:48:00", "mul,add,sub,div,mod");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "2.0.0", "2018-10-21 16:05:00", "mul,add,sub,div,mod");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "2.1.0.RC1", "2018-12-18 20:35:00", "mul,add,sub,div,mod");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "2.1.0.RC2", "2018-12-27 19:32:00", "mul,add,sub,div,mod");
INSERT INTO eth.library (name, version, releaseDate, functions)
VALUES ("SafeMath", "2.1.1", "2019-01-04 21:34:00", "mul,add,sub,div,mod");

CREATE TABLE IF NOT EXISTS eth.libraryFunction (
  id INT(9) NOT NULL AUTO_INCREMENT,
  compilerVersion VARCHAR(64) NOT NULL,
  compilerOptimization BOOLEAN NOT NULL,
  library VARCHAR(64) NOT NULL,
  libraryVersion VARCHAR(64) NOT NULL,
  functionName VARCHAR(64) NOT NULL,
  bytecode LONGTEXT NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS eth.verifiedContracts (
  id int(20) NOT NULL,
  address varchar(50) NOT NULL,
  network int(5) NOT NULL,
  mainContract varchar(200) NOT NULL,
  dateVerified date NOT NULL,
  sourcecode longtext NOT NULL,
  abi longtext NOT NULL,
  contractCreationCode longtext NOT NULL,
  constructor longtext NOT NULL,
  library longtext NOT NULL,
  swarm varchar(500) NOT NULL,
  compiler varchar(200) NOT NULL,
  optimiser varchar(20) NOT NULL,
  optimiser_runs int(10) NOT NULL,
  comments int(10) NOT NULL,
  dateCrawled date NOT NULL
);

GRANT SELECT, INSERT, UPDATE ON TABLE eth.* TO 'ethuser'@'localhost';
