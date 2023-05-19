-- Attach to database
USE `pwnedhub-test`;

-- MySQL dump 10.13  Distrib 5.7.29, for Linux (x86_64)

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `memberships`
--

DROP TABLE IF EXISTS `memberships`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `memberships` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `room_id` int(11) DEFAULT NULL,
  `level` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `membership_id` (`user_id`,`room_id`),
  KEY `room_id` (`room_id`),
  CONSTRAINT `memberships_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `memberships_ibfk_2` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `memberships`
--

LOCK TABLES `memberships` WRITE;
/*!40000 ALTER TABLE `memberships` DISABLE KEYS */;
INSERT INTO `memberships` VALUES (1,'2019-02-16 01:51:59','2019-02-16 01:51:59',1,1,0),(2,'2019-02-16 04:46:27','2019-02-16 04:46:27',2,1,1),(3,'2019-02-16 04:47:14','2019-02-16 04:47:14',3,1,1),(4,'2019-02-16 04:48:19','2019-02-16 04:48:19',4,1,1),(5,'2019-02-16 04:49:34','2019-02-16 04:49:34',5,1,1);
/*!40000 ALTER TABLE `memberships` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `messages`
--

DROP TABLE IF EXISTS `messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `messages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  `comment` text NOT NULL,
  `user_id` int(11) NOT NULL,
  `room_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `room_id` (`room_id`),
  CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `messages`
--

LOCK TABLES `messages` WRITE;
/*!40000 ALTER TABLE `messages` DISABLE KEYS */;
INSERT INTO `messages` VALUES (1,'2019-02-18 04:55:11','2019-02-18 04:55:11','Hey, did you guys hear that we\'re having a security assessment this week?',3,1),(2,'2019-02-18 04:55:19','2019-02-18 04:55:19','No.',4,1),(3,'2019-02-18 04:56:09','2019-02-18 04:56:09','First I\'m hearing of it. I hope they don\'t find any bugs. This is my \"get rich quick\" scheme.',2,1),(4,'2019-02-18 04:57:02','2019-02-18 04:57:02','Heh. Me too. So looking forward to afternoons on my yacht. :-)',3,1),(5,'2019-02-18 04:57:08','2019-02-18 04:57:08','Wait... didn\'t we go live this week?',4,1),(6,'2019-02-18 04:57:20','2019-02-18 04:57:20','Well, as the most interesting man in the world says, "I don\'t always get apps tested, but when I do, I get it done in prod."',2,1),(7,'2019-02-18 04:57:32','2019-02-18 04:57:32','LOL! So, yeah, did any of you guys fix those things I found during QA testing? I sent Cooper a link to them in a private message.',5,1),(8,'2019-02-18 04:57:37','2019-02-18 04:57:37','No.',4,1),(9,'2019-02-18 04:57:41','2019-02-18 04:57:41','My bad.',2,1),(10,'2019-02-18 04:57:46','2019-02-18 04:57:46','Uh oh...',3,1),(11,'2019-02-18 04:59:31','2019-02-18 04:59:31','Wow. We\'re totally going to end up on https://haveibeenpwned.com/PwnedWebsites.',5,1);
/*!40000 ALTER TABLE `messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notes`
--

DROP TABLE IF EXISTS `notes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  `name` varchar(255) NOT NULL,
  `content` text,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `notes_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notes`
--

LOCK TABLES `notes` WRITE;
/*!40000 ALTER TABLE `notes` DISABLE KEYS */;
/*!40000 ALTER TABLE `notes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rooms`
--

DROP TABLE IF EXISTS `rooms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rooms` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  `name` varchar(255) NOT NULL,
  `private` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rooms`
--

LOCK TABLES `rooms` WRITE;
/*!40000 ALTER TABLE `rooms` DISABLE KEYS */;
INSERT INTO `rooms` VALUES (1,'2019-02-16 01:51:59','2019-02-16 01:51:59','general',0);
/*!40000 ALTER TABLE `rooms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `scans`
--

DROP TABLE IF EXISTS `scans`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `scans` (
  `id` varchar(36) NOT NULL,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  `command` varchar(255) NOT NULL,
  `results` text,
  `complete` tinyint(1) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `scans_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `scans`
--

LOCK TABLES `scans` WRITE;
/*!40000 ALTER TABLE `scans` DISABLE KEYS */;
/*!40000 ALTER TABLE `scans` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tools`
--

DROP TABLE IF EXISTS `tools`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tools` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  `name` varchar(255) NOT NULL,
  `path` varchar(255) NOT NULL,
  `description` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tools`
--

LOCK TABLES `tools` WRITE;
/*!40000 ALTER TABLE `tools` DISABLE KEYS */;
INSERT INTO `tools` VALUES (1,'2019-02-16 02:09:59','2019-02-16 02:09:59','Dig','dig','(Domain Internet Groper) Network administration tool for Domain Name System (DNS) name server interrogation.'),(2,'2019-02-16 02:10:29','2019-02-16 02:10:29','Nmap','nmap','(Network Mapper) Utility for network discovery and security auditing.'),(3,'2019-02-16 02:10:59','2019-02-16 02:10:59','Nikto','nikto','Signature-based web server scanner.'),(4,'2019-02-16 02:11:29','2019-02-16 02:11:29','SSLyze','sslyze','Fast and powerful SSL/TLS server scanning library.'),(5,'2019-02-16 02:11:59','2019-02-16 02:11:59','SQLmap','sqlmap --batch','Penetration testing tool that automates the process of detecting and exploiting SQL injection flaws.');
/*!40000 ALTER TABLE `tools` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  `username` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `avatar` text,
  `signature` text,
  `password_hash` varchar(255) DEFAULT NULL,
  `role` int(11) NOT NULL,
  `status` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'2019-02-16 01:51:59','2019-02-16 01:51:59','admin','admin@pwnedhub.com','Administrator','/images/avatars/admin.png','All your base are belong to me.','diMyVFRBOBQbXFIkMRRQeAguTEEhCBAmHw==',0,1),(2,'2019-02-16 04:46:27','2019-02-16 04:46:27','Cooperman','cooper@pwnedhub.com','Cooper','/images/avatars/c-man.png','Gamer, hacker, and basketball player. Energy sword FTW!','cBdTBwdALwoLAlY=',1,1),(3,'2019-02-16 04:47:14','2019-02-16 04:47:14','Babygirl#1','taylor@pwnedhub.com','Taylor','/images/avatars/wolf.jpg','Wolf in a past life. Nerd in the current. Johnny 5 is indeed alive.','RwoRAAAXPw0WVhYG',1,1),(4,'2019-02-16 04:48:19','2019-02-16 04:48:19','Hack3rPrincess','tanner@pwnedhub.com','Tanner','/images/avatars/kitty.jpg','I might be small, cute, and cuddly, but remember... dynamite comes in small tightly wrapped packages that go boom.','RgQXBgAGMhYNRRUPFw==',1,1),(5,'2019-02-16 04:49:34','2019-02-16 04:49:34','Baconator','emilee@pwnedhub.com','Emilee','/images/avatars/bacon.png','Late to the party, but still the life of the party.','XA4AFksXJAhWHVZVXQ==',1,1);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-07-14  2:13:08
