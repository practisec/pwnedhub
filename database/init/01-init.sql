-- Setup databases and users
CREATE DATABASE IF NOT EXISTS `pwnedhub`;
CREATE DATABASE IF NOT EXISTS `pwnedhub-test`;
CREATE DATABASE IF NOT EXISTS `pwnedhub-config`;
CREATE USER 'pwnedhub'@'%' IDENTIFIED BY 'dbconnectpass';
GRANT ALL PRIVILEGES ON `pwnedhub` . * TO 'pwnedhub'@'%';
GRANT ALL PRIVILEGES ON `pwnedhub-test` . * TO 'pwnedhub'@'%';
GRANT ALL PRIVILEGES ON `pwnedhub-config` . * TO 'pwnedhub'@'%';
