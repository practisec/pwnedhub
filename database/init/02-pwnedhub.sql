-- Attach to database
USE `pwnedhub`;

-- MySQL dump 10.13  Distrib 5.7.41, for Linux (x86_64)
--
-- Host: db    Database: pwnedhub
-- ------------------------------------------------------
-- Server version	5.7.41

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
  `modified` datetime NOT NULL,
  `subject` text NOT NULL,
  `content` text NOT NULL,
  `sender_id` int(11) NOT NULL,
  `receiver_id` int(11) NOT NULL,
  `read` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `sender_id` (`sender_id`),
  KEY `receiver_id` (`receiver_id`),
  CONSTRAINT `mail_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`),
  CONSTRAINT `mail_ibfk_2` FOREIGN KEY (`receiver_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mail`
--

LOCK TABLES `mail` WRITE;
/*!40000 ALTER TABLE `mail` DISABLE KEYS */;
INSERT INTO `mail` VALUES (1,'2023-04-10 11:46:33','2023-04-10 11:46:33','QA Results','I just finished checking out the latest push of PwnedHub. I encountered a couple of errors as I was testing and placed them in a paste for you to check out at https://pastebin.com/F2mzJJJ0.',5,2,1),(2,'2023-04-11 14:12:17','2023-04-11 14:12:17','Collaboration Inquiry','Hey, I\'ve heard about the good work you\'ve been doing on the platform and wanted to talk to you privately about something important.',3,5,1),(3,'2023-04-11 14:17:17','2023-04-11 14:17:17','RE: Collaboration Inquiry','Sure, what\'s on your mind?',5,3,1),(4,'2023-04-11 14:22:17','2023-04-11 14:22:17','RE: Collaboration Inquiry','I believe we have a unique opportunity to collaborate on a project together.',3,5,1),(5,'2023-04-11 14:27:17','2023-04-11 14:27:17','RE: Collaboration Inquiry','Interesting. What kind of project are you referring to?',5,3,1),(6,'2023-04-11 14:32:17','2023-04-11 14:32:17','RE: Collaboration Inquiry','Well, we both clearly have a passion for technology and problem-solving. I think we can combine our skills to accomplish something remarkable.',3,5,1),(7,'2023-04-11 14:37:17','2023-04-11 14:37:17','RE: Collaboration Inquiry','That sounds intriguing. But why do we need to keep it a secret?',5,3,1),(8,'2023-04-11 14:42:17','2023-04-11 14:42:17','RE: Collaboration Inquiry','I believe keeping it secret is crucial for now. We can work discreetly without any unnecessary external influences or distractions. It allows us to focus solely on our project and ensures that our ideas and efforts remain protected.',3,5,1),(9,'2023-04-11 14:47:17','2023-04-11 14:47:17','RE: Collaboration Inquiry','I see your point. Confidentiality could indeed be beneficial in the early stages. What are the details of this project?',5,3,1),(10,'2023-04-11 14:52:17','2023-04-11 14:52:17','RE: Collaboration Inquiry','I have an idea for developing some cutting-edge code that addresses a specific global need. I\'ve already done some initial research, and I believe it has great potential. The implications are massive!',3,5,1),(11,'2023-04-11 14:57:17','2023-04-11 14:57:17','RE: Collaboration Inquiry','That sounds exciting! Count me in. How can we proceed?',5,3,1),(12,'2023-04-11 15:02:17','2023-04-11 15:02:17','RE: Collaboration Inquiry','First, we need to establish a secure communication channel where we can share our progress, ideas, and any sensitive information related to the project. We can use encrypted messaging platforms or even set up a private server.',3,5,1),(13,'2023-04-11 15:07:17','2023-04-11 15:07:17','RE: Collaboration Inquiry','Agreed. Security should be our top priority. We should also consider using our handles to protect our identities during this secretive collaboration.',5,3,1),(14,'2023-04-11 15:12:17','2023-04-11 15:12:17','RE: Collaboration Inquiry','Excellent suggestion. Anonymity will add an extra layer of protection. Additionally, we should set up regular meetings in discreet locations to discuss the project\'s direction and milestones.',3,5,1),(15,'2023-04-11 15:17:17','2023-04-11 15:17:17','RE: Collaboration Inquiry','Sounds like a plan. Let\'s keep a low profile and make sure to involve only trustworthy individuals when the time comes to expand the team.',5,3,1),(16,'2023-04-11 15:22:17','2023-04-11 15:22:17','RE: Collaboration Inquiry','Absolutely. We must be selective and cautious about who we involve, ensuring they share our dedication to confidentiality and have the necessary skills to contribute effectively.',3,5,1),(17,'2023-04-11 15:27:17','2023-04-11 15:27:17','RE: Collaboration Inquiry','I\'m glad we\'re on the same page. Let\'s embark on this journey together, working in harmony to create something extraordinary while maintaining the secrecy that surrounds our collaboration.',5,3,1),(18,'2023-04-11 15:32:17','2023-04-11 15:32:17','RE: Collaboration Inquiry','Agreed. With our combined talents and discretion, I have no doubt we can achieve remarkable results. Here\'s to the beginning of our covert collaboration!',3,5,1),(19,'2023-05-17 15:18:23','2023-05-17 15:18:23','Suspicious Activity','Hey, I\'ve been noticing some unusual activity on our application lately. I\'m starting to think it might be used by a foreign government for malicious purposes.',2,3,1),(20,'2023-05-17 15:23:23','2023-05-17 15:23:23','RE: Suspicious Activity','That\'s a serious allegation. What kind of activity are you seeing?',3,2,1),(21,'2023-05-17 15:28:23','2023-05-17 15:28:23','RE: Suspicious Activity','Well, I\'ve been analyzing the network traffic, and there are some suspicious connections to servers in a foreign country known for cyber espionage. It seems like they\'re exploiting our app.',2,3,1),(22,'2023-05-17 15:33:23','2023-05-17 15:33:23','RE: Suspicious Activity','That\'s concerning. Can you provide more details? Are there any specific actions or patterns that indicate malicious intent?',3,2,1),(23,'2023-05-17 15:38:23','2023-05-17 15:38:23','RE: Suspicious Activity','Yes, I\'ve noticed an increase in data transfers during odd hours, and the payload seems to match known hacking techniques. It\'s as if they\'re using our application to target another government\'s network.',2,3,1),(24,'2023-05-17 15:43:23','2023-05-17 15:43:23','RE: Suspicious Activity','Hold on, let\'s not jump to conclusions. Is there any chance this could be a result of a bug or a misconfiguration on our side?',3,2,1),(25,'2023-05-17 15:48:23','2023-05-17 15:48:23','RE: Suspicious Activity','I\'ve considered that possibility, but our security protocols are robust, and I haven\'t found any issues with our code or configurations. This seems deliberate.',2,3,1),(26,'2023-05-17 15:53:23','2023-05-17 15:53:23','RE: Suspicious Activity','Alright, we need to take this seriously. Let\'s gather more evidence and conduct a thorough investigation. We should wait to involve our security team and superiors until we have enough evidence to respond appropriately.',3,2,1),(27,'2023-05-17 15:58:23','2023-05-17 15:58:23','RE: Suspicious Activity','Agreed. I\'ll document all the suspicious activities I\'ve observed so far. We\'ll need to present a compelling case to our superiors and get their support in addressing this.',2,3,1),(28,'2023-05-17 16:03:23','2023-05-17 16:03:23','RE: Suspicious Activity','Absolutely. Our priority should be protecting our users and ensuring the integrity of our application. Let\'s work together and I\'ll reach out to external experts when it becomes necessary.',3,2,1),(29,'2023-05-17 16:08:23','2023-05-17 16:08:23','RE: Suspicious Activity','Agreed. This situation demands our full attention. We should remain vigilant and maintain open communication as we proceed with the investigation.',2,3,1),(30,'2023-05-17 16:25:23','2023-05-17 16:25:23','Urgent Concern','We have a problem. Someone is onto us.',3,5,1),(31,'2023-05-17 16:30:23','2023-05-17 16:30:23','RE: Urgent Concern','What do you mean? How did you come to that conclusion?',5,3,1),(32,'2023-05-17 16:35:23','2023-05-17 16:35:23','RE: Urgent Concern','One of the other developers noticed some unusual activity and may have detected the presence of our encrypted communication channels. They noticed signs of intrusion attempts coming from the application\'s IP space and increased surveillance.',3,5,1),(33,'2023-05-17 16:40:23','2023-05-17 16:40:23','RE: Urgent Concern','That\'s alarming. Did you take any precautions to secure our communication?',5,3,1),(34,'2023-05-17 16:45:23','2023-05-17 16:45:23','RE: Urgent Concern','Yes, I immediately strengthened our encryption protocols and implemented additional security measures. But I fear it might not be enough. We need to be extra cautious from now on.',3,5,1),(35,'2023-05-17 16:50:23','2023-05-17 16:50:23','RE: Urgent Concern','Agreed. We can\'t afford to take any risks. Let\'s assume that our every move is being monitored. We need to lay low and reassess our strategy.',5,3,1),(36,'2023-05-17 16:55:23','2023-05-17 16:55:23','RE: Urgent Concern','I\'ve been thinking about that. We should consider temporarily suspending our project until we can determine the extent of the threat and find a way to neutralize it.',3,5,1),(37,'2023-05-17 17:00:23','2023-05-17 17:00:23','RE: Urgent Concern','It\'s a difficult decision, but it might be for the best. We must prioritize our safety and the protection of our work. Let\'s go dark and minimize any digital footprint associated with our project.',5,3,1),(38,'2023-05-17 17:05:23','2023-05-17 17:05:23','RE: Urgent Concern','Absolutely. We should disconnect from any shared resources and take down our private server. It\'s crucial to leave no trace behind.',3,5,1),(39,'2023-05-17 17:10:23','2023-05-17 17:10:23','RE: Urgent Concern','Once we\'ve taken the necessary precautions, we can regroup and reassess our situation.',5,3,1),(40,'2023-05-17 17:15:23','2023-05-17 17:15:23','RE: Urgent Concern','Agreed. We can\'t underestimate the severity of the situation.',3,5,1),(41,'2023-05-17 17:20:23','2023-05-17 17:20:23','RE: Urgent Concern','Let\'s also be vigilant in our personal lives. We should watch out for any suspicious activities or attempts to compromise our identities. It\'s crucial to protect ourselves on all fronts.',5,3,1),(42,'2023-05-17 17:25:23','2023-05-17 17:25:23','RE: Urgent Concern','Absolutely. Our safety and security should be our top priority. We\'ve come too far to let our work be jeopardized.',3,5,1),(43,'2023-05-17 17:30:23','2023-05-17 17:30:23','RE: Urgent Concern','Stay safe, my friend. Let\'s maintain open lines of communication through secure channels, and we\'ll navigate through this challenging situation together.',5,3,1),(44,'2023-05-17 17:35:23','2023-05-17 17:35:23','RE: Urgent Concern','Thank you for your support. We\'ll get through this. Our collaboration might be momentarily paused, but our determination remains unwavering. Take care and stay vigilant.',3,5,1);
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
  `modified` datetime NOT NULL,
  `comment` text NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `messages`
--

LOCK TABLES `messages` WRITE;
/*!40000 ALTER TABLE `messages` DISABLE KEYS */;
INSERT INTO `messages` VALUES (1,'2023-04-09 13:05:24','2023-04-09 13:05:24','Hey, have you heard the latest news? We\'re host to the world\'s most elite computer hackers now! It\'s the top headline on https://www.cnn.com.',4),(2,'2023-04-09 13:06:24','2023-04-09 13:06:24','Oh really? Did we finally break into those top-secret government systems? ;-)',3),(3,'2023-04-09 13:07:24','2023-04-09 13:07:24','Absolutely! We\'re like modern-day cyber spies. I hope they don\'t start calling us \"007010101.\"',2),(4,'2023-04-09 13:08:24','2023-04-09 13:08:24','Haha! We\'ll be the tech-savvy version of James Bond. Instead of gadgets, we\'ll have keyboards and code.',4),(5,'2023-04-09 13:09:24','2023-04-09 13:09:24','And our secret hideout will be a basement filled with energy drinks and pizza boxes.',3),(6,'2023-04-09 13:10:24','2023-04-09 13:10:24','Ah, the glamorous life of a hacker. We\'ll have our own catchphrases like \"I\'m in\" or \"Access granted,\" even though we\'re just sitting in our PJs.',2),(7,'2023-04-09 13:11:24','2023-04-09 13:11:24','Yeah, hacking into systems, one cup of coffee at a time. Who needs real-world adventures when you can have virtual ones, right?',4),(8,'2023-04-09 13:12:24','2023-04-09 13:12:24','Absolutely! We\'ll live on the edge of our office chairs, typing furiously as we breach firewalls and decipher encrypted codes.',3),(9,'2023-04-09 13:13:24','2023-04-09 13:13:24','And when we finally hack into those top-secret systems, we\'ll leave our signature: a dancing ASCII art of a penguin wearing a black hat.',2),(10,'2023-04-09 13:14:24','2023-04-09 13:14:24','Perfect! We\'ll be known as the notorious hackers who infiltrated the highest security systems and left a trail of laughter in our wake.',4),(11,'2023-04-09 13:15:24','2023-04-09 13:15:24','Just imagine the headlines: \"World-class hackers expose top-secret files... while snacking on nachos!\"',3),(12,'2023-04-09 13:16:24','2023-04-09 13:16:24','And when they try to catch us, they\'ll find themselves trapped in a never-ending loop of cat memes. We\'ll be unstoppable!',2),(13,'2023-04-09 13:17:24','2023-04-09 13:17:24','Well, until our moms call us for dinner or the pizza delivery arrives. The life of a hacker isn\'t all glamour, you know.',4),(14,'2023-04-09 13:18:24','2023-04-09 13:18:24','True, true. But for now, let\'s bask in the glory of our imaginary hacking adventures and dream of the day when we can type like lightning and break into anything we want.',3),(15,'2023-04-09 13:19:24','2023-04-09 13:19:24','Absolutely! Here\'s to the hackers who never hacked but always laughed. Cheers, my cyber comrades!',2),(16,'2023-04-09 13:20:24','2023-04-09 13:20:24','Hah! Y\'all are crazy. A bunch of developers sitting around talking about hacking like you know the first thing about breaking into protected systems. Some serious coping going on in here. Maybe one of these days you\'ll be like me and actually hack something for real.',5);
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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notes`
--

LOCK TABLES `notes` WRITE;
/*!40000 ALTER TABLE `notes` DISABLE KEYS */;
INSERT INTO `notes` VALUES (1,'2023-05-31 14:39:06','2023-05-31 15:09:26','Notes','### Operation \"Silent Snake\"\n\n#### Notes\n\n* ALWAYS remember to clean-up operational activity from PwnedHub.\n* Confirmed a reliable vector for command injection (tip from Babygirl#1).\n* Phase 1 of the operation complete with no sign of detection.\n* Phase 2 underway.\n\n#### Todo Phase 1\n\n1. (complete) Establish lines of communication.\n2. (complete) Identify potential attack vectors in target #1.\n3. (complete) Establish a reliable means of funneling attacks through target #1.\n4. (complete) Remove evidence of operational activity from target #1.\n\n#### Todo Phase 2\n\n1. (in progress) Use target #1 to identify potential attack vectors in target #2.\n2. Funnel attacks against target #2 through target #1.\n3. Establish remote access to target #2.\n\n#### Todo Phase 3\n\n* Actions on the objective.',5);
/*!40000 ALTER TABLE `notes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sessions`
--

DROP TABLE IF EXISTS `sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sessions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `session_id` varchar(255) DEFAULT NULL,
  `data` blob,
  `expiry` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `session_id` (`session_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sessions`
--

LOCK TABLES `sessions` WRITE;
/*!40000 ALTER TABLE `sessions` DISABLE KEYS */;
/*!40000 ALTER TABLE `sessions` ENABLE KEYS */;
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
  `question` int(11) NOT NULL,
  `answer` varchar(255) NOT NULL,
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
INSERT INTO `users` VALUES (1,'2019-02-16 01:51:59','2019-02-16 01:51:59','admin','admin@pwnedhub.com','Administrator','/images/avatars/admin.png','All your base are belong to me.','QQsEEwIRJgAXUBY=',1,'Diego',0,1),(2,'2019-02-16 04:46:27','2019-02-16 04:46:27','Cooperman','cooper@pwnedhub.com','Cooper','/images/avatars/c-man.png','Gamer, hacker, and basketball player. Energy sword FTW!','cBdTBwdALwoLAlY=',3,'Augusta',1,1),(3,'2019-02-16 04:47:14','2019-02-16 04:47:14','Babygirl#1','taylor@pwnedhub.com','Taylor','/images/avatars/wolf.jpg','Wolf in a past life. Nerd in the current. Johnny 5 is indeed alive.','RwoRAAAXPw0WVhYG',2,'Rocket',1,1),(4,'2019-02-16 04:48:19','2019-02-16 04:48:19','Hack3rPrincess','tanner@pwnedhub.com','Tanner','/images/avatars/kitty.jpg','I might be small, cute, and cuddly, but remember... dynamite comes in small tightly wrapped packages that go boom.','RgQXBgAGMhYNRRUPFw==',0,'Drumstick',1,1),(5,'2019-02-16 04:49:34','2019-02-16 04:49:34','Baconator','emilee@pwnedhub.com','Emilee','/images/avatars/bacon.png','Late to the party, but still the life of the party.','XA4AFksXJAhWHVZVXQ==',4,'Chick-fil-a',1,1);
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

-- Dump completed on 2023-05-31 15:17:22
