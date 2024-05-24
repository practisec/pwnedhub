-- Attach to database
USE `pwnedhub`;

-- MySQL dump 10.13  Distrib 8.0.33, for Linux (x86_64)
--
-- Host: localhost    Database: pwnedhub
-- ------------------------------------------------------
-- Server version	8.0.33

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `mail`
--

DROP TABLE IF EXISTS `mail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mail` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  `subject` text NOT NULL,
  `content` text NOT NULL,
  `sender_id` int NOT NULL,
  `receiver_id` int NOT NULL,
  `read` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `sender_id` (`sender_id`),
  KEY `receiver_id` (`receiver_id`),
  CONSTRAINT `mail_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`),
  CONSTRAINT `mail_ibfk_2` FOREIGN KEY (`receiver_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mail`
--

LOCK TABLES `mail` WRITE;
/*!40000 ALTER TABLE `mail` DISABLE KEYS */;
INSERT INTO `mail` VALUES (1,'2019-02-14 14:12:17','2019-02-14 14:12:17','QA Results','Hey Cooper,\r\n\r\nI just finished checking out the latest push of PwnedHub. I encountered a couple of errors as I was testing and placed them in a paste for you to check out at https://pastebin.com/F2mzJJJ0.',5,2,1),(2,'2019-02-17 22:30:14','2019-02-17 22:30:14','Training','Hey Cooper,\r\n\r\nHave you heard about that PWAPT class by Tim Tomes? Sounds like some top notch stuff. We should get him in here to do some training.',4,2,1),(3,'2019-02-17 22:45:38','2019-02-17 22:45:38','RE: Training','Tanner,\r\n\r\nSounds good to me. I\'ll put a request in to Taylor.',2,4,1),(4,'2019-02-17 22:46:29','2019-02-17 22:46:29','PWAPT Training','Taylor,\r\n\r\nTanner and some of the folks have been asking about some training. Specifically, the PWAPT class by Tim Tomes. You ever heard of it?',2,3,1),(5,'2019-02-17 22:48:12','2019-02-17 22:48:12','RE: PWAPT Training','Cooper,\r\n\r\nYeah, I\'ve heard about that guy. He\'s a hack!',3,2,1);
/*!40000 ALTER TABLE `mail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `messages`
--

DROP TABLE IF EXISTS `messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  `comment` text NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `messages`
--

LOCK TABLES `messages` WRITE;
/*!40000 ALTER TABLE `messages` DISABLE KEYS */;
INSERT INTO `messages` VALUES (1,'2019-02-18 04:55:11','2019-02-18 04:55:11','Hey, did you guys hear that we\'re having a security assessment this week?',3),(2,'2019-02-18 04:55:19','2019-02-18 04:55:19','No.',4),(3,'2019-02-18 04:56:09','2019-02-18 04:56:09','First I\'m hearing of it. I hope they don\'t find any bugs. This is my \"get rich quick\" scheme.',2),(4,'2019-02-18 04:57:02','2019-02-18 04:57:02','Heh. Me too. So looking forward to afternoons on my yacht. :-)',3),(5,'2019-02-18 04:57:08','2019-02-18 04:57:08','Wait... didn\'t we go live this week?',4),(6,'2019-02-18 04:57:20','2019-02-18 04:57:20','Well, as the most interesting man in the world says, \"I don\'t always get apps tested, but when I do, I get it done in prod.\"',2),(7,'2019-02-18 04:57:32','2019-02-18 04:57:32','LOL! So, yeah, did any of you guys fix those things I found during QA testing? I sent Cooper a link to them in a private message.',5),(8,'2019-02-18 04:57:37','2019-02-18 04:57:37','No.',4),(9,'2019-02-18 04:57:41','2019-02-18 04:57:41','My bad.',2),(10,'2019-02-18 04:57:46','2019-02-18 04:57:46','Uh oh...',3),(11,'2019-02-18 04:59:31','2019-02-18 04:59:31','Wow. We\'re totally going to end up on https://haveibeenpwned.com/PwnedWebsites.',5);
/*!40000 ALTER TABLE `messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notes`
--

DROP TABLE IF EXISTS `notes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  `name` varchar(255) NOT NULL,
  `content` text,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `notes_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notes`
--

LOCK TABLES `notes` WRITE;
/*!40000 ALTER TABLE `notes` DISABLE KEYS */;
/*!40000 ALTER TABLE `notes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tokens`
--

DROP TABLE IF EXISTS `tokens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tokens` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  `value` varchar(255) NOT NULL,
  `ttl` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `tokens_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tokens`
--

LOCK TABLES `tokens` WRITE;
/*!40000 ALTER TABLE `tokens` DISABLE KEYS */;
/*!40000 ALTER TABLE `tokens` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tools`
--

DROP TABLE IF EXISTS `tools`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tools` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  `name` varchar(255) NOT NULL,
  `path` varchar(255) NOT NULL,
  `description` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  `username` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `avatar` text,
  `signature` text,
  `password_hash` varchar(255) DEFAULT NULL,
  `question` int NOT NULL,
  `answer` varchar(255) NOT NULL,
  `role` int NOT NULL,
  `status` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'2019-02-16 01:51:59','2019-02-16 01:51:59','admin','admin@pwnedhub.com','Administrator','/static/common/images/avatars/admin.png','All your base are belong to me.','QQsEEwIRJgAXUBY=',1,'Diego',0,1),(2,'2019-02-16 04:46:27','2019-02-16 04:46:27','Cooperman','cooper@pwnedhub.com','Cooper','/static/common/images/avatars/c-man.png','Gamer, hacker, and basketball player. Energy sword FTW!','cBdTBwdALwoLAlY=',3,'Augusta',1,1),(3,'2019-02-16 04:47:14','2019-02-16 04:47:14','Babygirl#1','taylor@pwnedhub.com','Taylor','/static/common/images/avatars/wolf.jpg','Wolf in a past life. Nerd in the current. Johnny 5 is indeed alive.','RwoRAAAXPw0WVhYG',2,'Rocket',1,1),(4,'2019-02-16 04:48:19','2019-02-16 04:48:19','Hack3rPrincess','tanner@pwnedhub.com','Tanner','/static/common/images/avatars/kitty.jpg','I might be small, cute, and cuddly, but remember... dynamite comes in small tightly wrapped packages that go boom.','RgQXBgAGMhYNRRUPFw==',0,'Drumstick',1,1),(5,'2019-02-16 04:49:34','2019-02-16 04:49:34','Baconator','emilee@pwnedhub.com','Emilee','/static/common/images/avatars/bacon.png','Late to the party, but still the life of the party.','XA4AFksXJAhWHVZVXQ==',4,'Chick-fil-a',1,1);
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

-- Dump completed on 2023-07-17  4:09:55
