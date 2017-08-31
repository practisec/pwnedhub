-- MySQL dump 10.13  Distrib 5.5.53, for debian-linux-gnu (i686)
--
-- Host: localhost    Database: pwnedhub
-- ------------------------------------------------------
-- Server version      5.5.53-0ubuntu0.14.04.1

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
-- Table structure for table `mail`
--

DROP TABLE IF EXISTS `mail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `subject` text,
  `content` text,
  `sender_id` int(11) NOT NULL,
  `receiver_id` int(11) NOT NULL,
  `read` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `sender_id` (`sender_id`),
  KEY `receiver_id` (`receiver_id`),
  CONSTRAINT `mail_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`),
  CONSTRAINT `mail_ibfk_2` FOREIGN KEY (`receiver_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mail`
--

LOCK TABLES `mail` WRITE;
/*!40000 ALTER TABLE `mail` DISABLE KEYS */;
INSERT INTO `mail` VALUES (1,'2016-10-07 22:30:14.509923','Training','Hey Cooper,\r\n\r\nHave you heard about that PWAPT class by Tim Tomes? Sounds like some top notch stuff. We should get him in here to do some training.',4,2,1),(2,'2016-10-07 22:45:38.620758','RE: Training','Tanner,\r\n\r\nSounds good to me. I\'ll put a request in to Taylor.',2,4,1),(3,'2016-10-07 22:46:29.639263','PWAPT Training','Taylor,\r\n\r\nTanner and some of the folks have been asking about some training. Specifically, the PWAPT class by Tim Tomes. You ever heard of it?',2,3,1),(4,'2016-10-07 22:48:12.456073','RE: PWAPT Training','Cooper,\r\n\r\nYeah, I\'ve heard about that guy. He\'s a hack!',3,2,1);
/*!40000 ALTER TABLE `mail` ENABLE KEYS */;
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
  `comment` text,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `messages`
--

LOCK TABLES `messages` WRITE;
/*!40000 ALTER TABLE `messages` DISABLE KEYS */;
INSERT INTO `messages` VALUES (1,'2015-10-28 04:55:11','Hey, did you guys hear that we\'re having a security assessment this week?',3),(2,'2015-10-28 04:55:19','No.',4),(3,'2015-10-28 04:56:09','First I\'m hearing of it. I hope they don\'t find any bugs. This is my \"get rich quick\" scheme.',2),(4,'2015-10-28 04:57:02','Heh. Me too. So looking forward to afternoons on my yacht. :-)',3),(5,'2015-10-28 04:57:32','So, yeah, did any of you guys fix those things I found during peer review?',3),(6,'2015-10-28 04:57:37','No.',4),(7,'2015-10-28 04:57:41','Nope.',2),(8,'2015-10-28 04:57:46','Uh oh...',3);
/*!40000 ALTER TABLE `messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `scores`
--

DROP TABLE IF EXISTS `scores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `scores` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `player` varchar(255) NOT NULL,
  `score` int(11) NOT NULL,
  `recid` int(11) DEFAULT NULL,
  `recording` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `scores`
--

LOCK TABLES `scores` WRITE;
/*!40000 ALTER TABLE `scores` DISABLE KEYS */;
INSERT INTO `scores` VALUES (1,'2015-10-28 03:07:00','Babygirl#1',50,8,'recTurn=230103230121030323012103210&recFrame=+r+b+4+3+4+7+i+f+9+3+8+5+7+i+b+j+1+g+1+g+g11+3+p+d+2+7&recFood=+n211k+lo+3q+ya+gc'),(2,'2015-10-28 05:31:19','Cooperman',140,3,'recTurn=032101230123032101230121230103230321030321030123012321230301230&recFrame=+i+5+h+9+d+j+6+b+2+d+6+8+7+9+h+b+4+d+6+h+1+h+7+s+9+4+m+3+l+7+b+3+9+i+1+x+7+k+2+a+8+q+i+s+i+4+o+9+p+b+m+a+g+a+l+g+a+1+e+q+k+r+k&recFood=+hq+me+8a+3j+vb+qo15p+mj10s+9t+om13h+dn+v6+0c'),(3,'2015-10-28 05:32:13','Hack3rPrincess',200,2,'recTurn=012323232103212301232103012321032301230103212103212321230301010323012303&recFrame=+f+j+5+3+c+a+1+9+1+b+h+o+f+1+f+h+4+i+5+m+e+9+f+c+q+p+7+c+1+g+m+5+a+2+8+o+710+c+9+1+t+5+a+1+o+m+r+m+6+e+8+9+9+f+6+g+3+6+k+9+1+j+3+c+1+a+9+j+3+e+1&recFood=+5d+ym+l5+d8+c8+y5174+lt+in+yb+uc+wn+vr+u5+c9+ie+zl14n+hb+fe+7k'),(4,'2015-10-28 05:32:37','Babygirl#1',70,5,'recTurn=23230123230123012323010103212&recFrame=+h+6+c+7+6+v+p+e+2+h+8+f+a+7+f+e+e+r+a+1+a+7+5+1+f+1+n+3+e&recFood=+sk+9t+v6+kd+q515j+wk10f'),(5,'2015-10-28 05:37:26','Babygirl#1',90,4,'recTurn=012301010303232301230123030121030&recFrame=+g+m+612+k+6+l+8+1+d+9+7+b+e+2+g+2+g+l+6+i+b+o+m+5+h+j+f+2+d+l+f+a&recFood=+1c12l+f4+4m+ir+np+s1+ii+fn+f3'),(6,'2015-10-28 05:34:21','Cooperman',270,0,'recTurn=230103230123230123212103230103012301012121032123012323012323012301030123010301012321230301230121&recFrame=+m+g+e+1+e+i+6+n+a+u+h+8+2+k+e10+g+1+d+a+e+o+2+v+1+w+a+b+3+d+9+f+f13+m+a+5+n+f+c+4+f+1+t+j+1+f11+i10+h+c+1+m+j12+p10+g+2+a+z+q+y+p+l+a+2+a+9+j+x+i+a+g+g+h+d+c+1+b+9+b+1+a+x+k+e+5+s+r13+j+3+8+1&recFood=117+t616c+cf147+bl+5i+o4+q3+tc+fj+1c14n+86+j1125+in+s7+3214j+jh+v7+g9+19+bd18b11o147'),(7,'2015-10-28 05:34:34','Hack3rPrincess',30,9,'recTurn=0321012323&recFrame=+h+3+g+8+5+q+8+2+d11&recFood=+kr+1l+rr+ft'),(8,'2015-10-28 05:34:56','Cooperman',70,6,'recTurn=230301230323010101232123&recFrame=+n+b+6+o+e+1+j+9+2+c+f+t+3+9+1+6+1+b+5+e+6+f+h+2&recFood=+r5+fb+8a+68+ln+co11o10t'),(9,'2015-10-28 05:36:34','Hack3rPrincess',260,1,'recTurn=03230301230123012321212301230103212123012321012303232301230321012303030123032301230101032301210123012321230323032121010321230&recFrame=+r+c+g+h+7+c+2+c+1+u+3+m+m+g+g+m+k+8+a+3+9+7+2+9+o+1+o+b+i+8+h+v+7+a+5+a+2+i+o11+6+c+1+a+5+l+f+r+3+8+8+1+b+b+1+z+m+m+4+k+n+p+p+p+113+7+b+1+5+1+n+8+v+1+r+1+v+c+y+e11+j+5+3+4+a+7+6+4+6+m+1+l+2+d+g+o+n11+l+1+g+1+h+a+8+3+6+h+1+j+1+m+e+c+1+k+4+j+n+u+e+6+e&recFood=+a2+gh+ep+is+r7+bm+d3+v2+f2155+hq+il+ph+18+dt+a4+jc+75+ei+sl13k+3k+cj+y5+ko+yb12g'),(10,'2015-10-28 05:36:53','Cooperman',60,7,'recTurn=23012301210123010121230&recFrame=+l+9+5+7+6+a+m+h+2+i+p+k+1+g+h+9+2+g+1+r+7+6+7&recFood=+t6+v6+xs+qq+p0+ke+zb');
/*!40000 ALTER TABLE `scores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sessions`
--

DROP TABLE IF EXISTS `sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sessions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `session_id` varchar(256) DEFAULT NULL,
  `data` text,
  `expiry` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `session_id` (`session_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tools`
--

DROP TABLE IF EXISTS `tools`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tools` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text NOT NULL,
  `path` text NOT NULL,
  `description` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tools`
--

LOCK TABLES `tools` WRITE;
/*!40000 ALTER TABLE `tools` DISABLE KEYS */;
INSERT INTO `tools` VALUES (1,'Dig','/usr/bin/dig','(Domain Internet Groper) Network administration tool for Domain Name System (DNS) name server interrogation.'),(2,'Nmap','/usr/bin/nmap','(Network Mapper) Utility for network discovery and security auditing.'),(3,'Nikto','/usr/bin/nikto','Signature-based web server scanner.'),(4,'SSLyze','/usr/bin/sslyze','Fast and powerful SSL/TLS server scanning library.'),(5,'SQLmap','/usr/bin/sqlmap --batch','Penetration testing tool that automates the process of detecting and exploiting SQL injection flaws.');
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
  `username` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `question` int(11) NOT NULL,
  `answer` varchar(255) NOT NULL,
  `notes` text,
  `role` int(11) NOT NULL,
  `status` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'2015-10-28 01:51:59','admin','Administrator','FgsMEw4RHgAFBho=',1,'Ralf',NULL,0,1),(2,'2015-10-28 04:46:27','Cooperman','Cooper','WQ1cIlpBBTwmC01QHRUGJxMQGQQcAgslJQ==',3,'Augusta',NULL,1,1),(3,'2015-10-28 04:47:14','Babygirl#1','Taylor','EFFBIk0nSwEsMTM1FQIxSycWKwEPVC80Ug==',2,'Rocket',NULL,1,1),(4,'2015-10-28 04:48:19','Hack3rPrincess','Tanner','V1ddUwhNMxYBUSEeKg1fCBgZBTBOGVAtBA==',0,'Drumstick',NULL,1,1);
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

-- Dump completed on 2017-01-09 22:50:38
