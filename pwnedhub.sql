-- MySQL dump 10.13  Distrib 5.7.25, for Linux (x86_64)
--
-- Host: localhost    Database: pwnedhub
-- ------------------------------------------------------
-- Server version	5.7.25-0ubuntu0.16.04.2

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
-- Table structure for table `bugs`
--

DROP TABLE IF EXISTS `bugs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bugs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `modified` datetime NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `vuln_id` int(11) NOT NULL,
  `severity` int(11) NOT NULL,
  `description` text NOT NULL,
  `impact` text NOT NULL,
  `status` int(11) NOT NULL,
  `submitter_id` int(11) NOT NULL,
  `reviewer_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `submitter_id` (`submitter_id`),
  KEY `reviewer_id` (`reviewer_id`),
  CONSTRAINT `bugs_ibfk_1` FOREIGN KEY (`submitter_id`) REFERENCES `users` (`id`),
  CONSTRAINT `bugs_ibfk_2` FOREIGN KEY (`reviewer_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bugs`
--

LOCK TABLES `bugs` WRITE;
/*!40000 ALTER TABLE `bugs` DISABLE KEYS */;
INSERT INTO `bugs` VALUES (1,'2019-02-02 10:52:51','2019-02-02 11:38:38','Form Replay in customer information form',3,2,'The server at `https://billingsupport.chaturbate.com/customer_support/information_form/` replays some form field data back in the response when there are form validation errors. This can be cached or viewed by someone with physical access to the same device used to complete the form.','Disclosure of sensitive customer information to arbitrary viewers.',2,2,4),(2,'2019-02-05 14:08:18','2019-02-08 15:39:03','Reflected XSS in lert.uber.com',4,2,'Due to a lack of input validation from the search field on `lert.uber.com`, it is possible to obtain a Reflected XSS from the URL path, e.g. `https://lert.uber.com/s/search/All/Home\">PAYLOAD`.','Standard XSS risk. Session hijacking, browser hijacking, etc.',2,2,4),(3,'2019-02-05 13:12:02','2019-02-07 21:37:10','Stored XSS on any page in most Uber domains',4,3,'Due to two IDOR vulnerabilities in Tealium, it is possible to compromise an administrator’s account and inject arbitrary JavaScript into `https://tags.tiqcdn.com/utag/uber/*`, which an attacker could leverage for a stored XSS attack on several Uber domains.\r\n\r\nAdditionally, a Tealium user’s password and MFA are resettable by any user, allowing an attacker to take over the account and modify code on their behalf.','Standard XSS stuff. Session hijacking, browser hijacking, etc. Although Uber does not own Tealium, they widely implement this on many different `uber.com` domains, making the impact far reaching.',1,2,3),(4,'2019-02-06 16:21:01','2019-02-08 10:37:37','Hacker can bypass 2FA requirement and reporter blacklist through embedded submission form',5,2,'A program owner can enforce the hackers to setup the two-factor authentication before submitting new reports to their program here: `https://hackerone.com/parrot_sec/submission_requirements` The Parrot Sec program has this feature enabled to enforce the hackers to setup 2FA before submitting reports. I removed my 2FA to test and i was blocked from submitting new reports as expected. However, i was able to bypass this 2FA setup requirements by using the Parrot Sec program Embedded Submission Form.\r\n\r\nSteps to reproduce:\r\n\r\n1. Login to your account and remove your 2FA on your account (if you already set it up).\r\n2. Now go to `https://hackerone.com/parrot_sec` and hit Submit Report button. Observe that you cannot submit report unless you will enable your 2FA.\r\n3. BYPASS: Get the Embedded Submission URL on their policy page: i got this ->> `https://hackerone.com/0a1e1f11-257e-4b46-b949-c7151212ffbb/embedded_submissions/new`\r\n4. Submit report using that embedded submission form and you can submit reports without setting-up your 2FA, despite the programs attempt to force the user to setup 2FA before submitting new reports.','Bypassing the enabled protection/feature of the program.',2,4,3),(5,'2019-02-08 09:37:11','2019-02-10 13:41:23','CORS Misconfiguration, could lead to disclosure of sensitive information',0,2,'An HTML5 cross-origin resource sharing (CORS) policy controls whether and how content running on other domains can perform two-way interaction with the domain that publishes the policy. The policy is fine-grained and can apply access controls per-request based on the URL and other features of the request.\r\n\r\nTrusting arbitrary origins effectively disables the same-origin policy, allowing two-way interaction by third-party web sites. Unless the response consists only of unprotected public content, this policy is likely to present a security risk. If the site specifies the `Access-Control-Allow-Credentials: true` header, third-party sites may be able to carry out privileged actions and retrieve sensitive information. Even if it does not, attackers may be able to bypass any IP-based access controls by proxying through users\' browsers.\r\n\r\nBelow is a proof-of-concept demonstrating this vulnerability in `www.zomato.com`. Notice the arbitrary origin reflected in the response:\r\n\r\nRequest:\r\n\r\n```\r\nGET /abudhabi HTTP/1.1\r\nHost: www.zomato.com\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:62.0) Gecko/20100101 Firefox/62.0\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8\r\nAccept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate\r\nReferer: https://www.zomato.com/\r\nCookie: zl=en; fbtrack=0c8f198276217196ed64230da7ec8506; _ga=GA1.2.1887254439.1538912146; _gcl_au=1.1.2098169460.1538912146; dpr=1; __utmx=141625785.FQnzc5UZQdSMS6ggKyLrqQ$0:NaN; __utmxx=141625785.FQnzc5UZQdSMS6ggKyLrqQ$0:1540032478:8035200; G_ENABLED_IDPS=google; cto_lwid=8a9f6540-307d-4333-bd04-96eebdec23b1; SL_C_23361dd035530_KEY=05a4e27ac591b9ca633a4fe9b5fdc3875e22560f; fbcity=57; zhli=1; al=0; _gid=GA1.2.1724569398.1539946684; session_id=c541029346655-a68e-4a04-b2f8-ef1992b2e230; AMP_TOKEN=%24NOT_FOUND; csrf=a84df4c9f61aadf31a4f1dd4ca48be6e; ak_bmsc=2C67C71C92EB260D24B70A22BB690F2C4F8C5EB21A5B00008607CB5B69982B47~plvdYiMgFHceTWhzyAX5U631p9L1788qeXL/lAyNPHymsMAnv6mHZSJNA05zvLH2oIoYhZh2IVuMrSYmbcah8ADEJOyyFO27PZ5N/H1Cdvks7MZe3E9Y91EtRL8tbHwWka49I9RjDSrHVcgq5z4OIk8dfQd05szzsPKkleP3Jp9MJD1rVdLEcg2cCHoQYw5ciHDvhZtMWN6RD0DxZBoe3LPsfb37q5xqHTQ8h9XpyqUzc=; _gat_city=1; _gat_country=1; _gat_global=1; _gat_globalV3=1; bm_sv=EDBA03CA40AC8D77509922CAA98130B4~OXaAg7LsgySzeWnqd9TzoaW6pGtPv7Ut2dYfUp7otuPnD1uJi3BUwSCYQiDP4q92NaiK6GLXT8xxPmWSgspcRyYjatr3Zc5lDyt8+MMSsDmykSMruOC6+5BPCXCEX+HulBpygHFzTAQJSoPSYxgsSjsbymzdQq/Q90b/MvSGLbo=\r\nConnection: close\r\nUpgrade-Insecure-Requests: 1\r\nOrigin: thisisanarbitraryorigin.com\r\n```\r\n\r\nResponse:\r\n\r\n```\r\nHTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length: 127168\r\nX-Content-Type-Options: nosniff\r\nX-XSS-Protection: 1; mode=block; report=https://www.zomato.com/cspreport.php\r\nContent-Security-Policy: frame-ancestors https://.nearbuystag.in https://.nearbuy.com \'self\'; default-src *; font-src * data:; img-src * data:; media-src * blob:; script-src \'self\' \'unsafe-inline\' \'unsafe-eval\' *.jwpcdn.com *.cloudflare.com *.twitter.com *.recruiterbox.com *.zdev.net *.zdev.net:8080 *.zomato.com *.tinymce.com *.gstatic.com *.googleapis.com *.google.com *.facebook.com sdk.accountkit.com *.doubleclick.net *.googlesyndication.com *.nr-data.net *.newrelic.com *.google-analytics.com *.akamaihd.net *.zmtcdn.com *.googletagmanager.com *.facebook.net *.googleadservices.com *.cdninstagram.com *.googlesyndication.com *.inspectlet.com *.spreedly.com *.instagram.com *.twimg.com *.mouseflow.com *.usersnap.com d3mvnvhjmkxpjz.cloudfront.net *.serving-sys.com *.sushissl.com *.pubnub.com tsgw.tataelxsi.co.in *.branch.io app.link cdn.poll-maker.com *.ampproject.org *.smartlook.com *.hotjar.com dashboard.hypertrack.io zba.se *.googletagmanager.com *.eff.org cdn.plot.ly *.zedo.com *.bing.com *.criteo.net *.criteo.com mddigital.in; style-src * \'unsafe-inline\';\r\nAccess-Control-Allow-Origin: thisisanarbitraryorigin.com\r\nAccess-Control-Allow-Credentials: true\r\nAccess-Control-Allow-Methods: GET, POST\r\nAccess-Control-Allow-Headers: Content-Type, X-ZOMATO-CSRFT, *\r\nServer: Zomato\r\nStrict-Transport-Security: max-age=31536000\r\nExpires: Sat, 20 Oct 2018 12:29:00 GMT\r\nPragma: no-cache\r\nDate: Sat, 20 Oct 2018 12:29:00 GMT\r\nConnection: close\r\nSet-Cookie: LEL_JS=true; expires=Sat, 20-Oct-2018 12:59:00 GMT; Max-Age=1800\r\nCache-Control: max-age=0, no-cache, no-store, no-transform\r\nVary: Accept-Encoding, User-Agent\r\nStrict-Transport-Security: max-age=31536000\r\nSet-Cookie: bm_sv=EDBA03CA40AC8D77509922CAA98130B4~OXaAg7LsgySzeWnqd9TzoaW6pGtPv7Ut2dYfUp7otuPnD1uJi3BUwSCYQiDP4q92NaiK6GLXT8xxPmWSgspcRyYjatr3Zc5lDyt8+MMSsDnq267a1bOhniBmABAbrga8gmdQdjDNE5GsLvrlCcm07Q3hffJKqLj7hIkMIJhtw4g=; Domain=.zomato.com; Path=/; Max-Age=1053; HttpOnly\r\n```','An attacker can lure victims to run arbitrary client-side code, and if a victim is logged in, then their personal information could be harvested and delivered to the attacker, bypassing same-origin policy.',2,2,3),(6,'2019-02-08 11:46:42','2019-02-08 11:46:42','Github Token Leaked publicly for https://github.sc-corp.net',12,4,'GitHub is a truly awesome service but it is unwise to put any sensitive data in code that is hosted on GitHub and similar services as i was able to find a Github token for a Software Engineer at Snap Inc. You can find the leak at `https://github.com/%E2%96%88%E2%96%88%E2%96%88%E2%96%88%E2%96%88/leetcode/blob/0eec6434940a01e490d5eecea9baf4778836c54e/TopicMatch.py`\r\n\r\n```\r\nimport os\r\nimport requests\r\nimport sys\r\npull_number = 76793\r\npull_url = \"https://github.sc-corp.net/api/v3/repos/Snapchat/android/pulls/\" + str(pull_number)\r\npayload = {}\r\npayload[\"Authorization\"] = \"token \" + \"9db9ca3440e535d90408a32a9c03d415979da910\"\r\nprint payload\r\nr = requests.get(pull_url,\r\n```','I didn\'t try anything with the token, so I don\'t know what access it has. I know that in order to login to `https://github.sc-corp.net` you need to have an email @snap, but I still thought it would be a good idea to share this finding with you in case it can be used in a way that i don\'t know.',0,4,2),(7,'2019-02-09 14:53:21','2019-02-16 09:42:07','Race condition in performing retest allows duplicated payments',16,4,'There exists a race condition in performing retests. By executing multiple requests to confirm a retest at the same time, a malicious user is paid multiple times for the retest. This allows for stealing money from HackerOne, which could go unnoticed by both HackerOne and the attacker (me).\r\n\r\nSteps to Reproduce:\r\n\r\n1. Receive a retest request email from HackerOne.\r\n2. Intercept the request to retest the email. Right click the request in Burp Suite and select Copy as curl command.\r\n3. Execute the request on the command line in the form (request) & (request) & .... In testing, I executed the command 5 times.\r\n4. Scroll to the bottom of `https://hackerone.com/settings/bounties`. The payment will appear under the Retest payments sections and may be repeated.\r\n5. Wait a few weeks. If successful, a callback from HackerOne will be received.\r\n6. Check your bank account statements. Observe that a $500 payment was sent from HackerOne, demonstrating that the race condition was successful.','This allows an attacker to exploit the retesting feature to steal many times more money. Given that this went unnoticed by both the attacker and HackerOne for over 2 weeks, this has the potential to be exploited multiple times to steal money from HackerOne.',2,2,3),(8,'2019-02-12 00:58:10','2019-02-12 00:58:10','XXE on https://duckduckgo.com',1,3,'The `x.js` endpoint on `https://duckduckgo.com` was vulnerable to XML External Entity (XXE) injection via the `u` parameter. This was due to improper sanitation of external XML entities. The results was a leak of certain world readable files on the system.','Arbitrary file read access on the file system which could disclose source code, config files, system information, etc.',0,4,2),(9,'2019-02-16 15:02:34','2019-02-17 14:42:48','Confidential data of users and limited metadata of programs and reports accessible via GraphQL',3,4,'Any attacker can get personally identifiable information of users of Hackerone such as email address, backup hash codes, facebook_user_id, account_recovery_phone_number_verified_at, totp_enabled, etc. These are just some examples of fields which are getting leaked directly from GraphQL. The following request sent to GraphQL causes the disclosure:\r\n\r\n```\r\n{\r\n  id\r\n  users()\r\n  {\r\n    total_count \r\n    nodes\r\n    {\r\n      _id\r\n      name\r\n      username\r\n      email\r\n      account_recovery_phone_number\r\n      account_recovery_unverified_phone_number\r\n      bounties\r\n      {\r\n        total_amount\r\n      }\r\n      otp_backup_codes\r\n      i_can_update_username\r\n      location\r\n      year_in_review_published_at\r\n      anc_triager\r\n      blacklisted_from_hacker_publish\r\n      calendar_token\r\n      vpn_credentials\r\n      {\r\n        name\r\n      }\r\n      account_recovery_phone_number_sent_at\r\n      account_recovery_phone_number_verified_at\r\n      swag\r\n      {\r\n        total_count\r\n      }\r\n      totp_enabled\r\n      subscribed_for_team_messages\r\n      subscribed_for_monthly_digest\r\n      sessions\r\n      {\r\n        total_count\r\n      }\r\n      facebook_user_id\r\n      unconfirmed_email\r\n    }\r\n  }\r\n```','This could potentially leak many users\' info.',2,2,4),(10,'2019-02-18 10:08:22','2019-02-18 10:08:22','Credientals Over GET method in plain Text',12,2,'While I was testing the application I found this bug where the application is sending the credentials over plain text in the URL of a GET request: `https://auth.ratelimited.me/login?username=testqaz%40grr.la&password=D33vanh%40h%40h%40`','If the application is sending the credentials over GET request it will be saved in the history of the Browser.',0,3,2);
/*!40000 ALTER TABLE `bugs` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mail`
--

LOCK TABLES `mail` WRITE;
/*!40000 ALTER TABLE `mail` DISABLE KEYS */;
INSERT INTO `mail` VALUES (1,'2016-10-07 22:30:14','2016-10-07 22:30:14','Training','Hey Cooper,\r\n\r\nHave you heard about that PWAPT class by Tim Tomes? Sounds like some top notch stuff. We should get him in here to do some training.',4,2,1),(2,'2016-10-07 22:45:38','2016-10-07 22:45:38','RE: Training','Tanner,\r\n\r\nSounds good to me. I\'ll put a request in to Taylor.',2,4,1),(3,'2016-10-07 22:46:29','2016-10-07 22:46:29','PWAPT Training','Taylor,\r\n\r\nTanner and some of the folks have been asking about some training. Specifically, the PWAPT class by Tim Tomes. You ever heard of it?',2,3,1),(4,'2016-10-07 22:48:12','2016-10-07 22:48:12','RE: PWAPT Training','Cooper,\r\n\r\nYeah, I\'ve heard about that guy. He\'s a hack!',3,2,1),(5,'2019-02-18 13:52:51','2019-02-18 15:38:15','New Submission for Review','You\'ve been randomly selected to review a bug bounty submission. That means that you are eligible to receive 25% of the bounty allotted for an accepted review of this bug! Please visit the submission page for <a href=\'http://pwnedhub.com/submissions/view/1\'>bug ID #00001</a> to review the submission and accept/reject accordingly. Thank you for being a valuable member of the PwnedHub community!',1,4,1),(6,'2019-02-18 13:53:32','2019-02-18 15:43:03','Submission Updated','A submission for which you are the reviewer has been updated. Please visit the submission page for <a href=\'http://pwnedhub.com/submissions/view/1\'>bug ID #00001</a> to review the updated submission and accept/reject accordingly. Thank you for being a valuable member of the PwnedHub community!',1,4,1),(7,'2019-02-18 14:08:18','2019-02-18 15:38:47','New Submission for Review','You\'ve been randomly selected to review a bug bounty submission. That means that you are eligible to receive 25% of the bounty allotted for an accepted review of this bug! Please visit the submission page for <a href=\'http://pwnedhub.com/submissions/view/2\'>bug ID #00002</a> to review the submission and accept/reject accordingly. Thank you for being a valuable member of the PwnedHub community!',1,4,1),(8,'2019-02-18 14:12:02','2019-02-18 15:35:59','New Submission for Review','You\'ve been randomly selected to review a bug bounty submission. That means that you are eligible to receive 25% of the bounty allotted for an accepted review of this bug! Please visit the submission page for <a href=\'http://pwnedhub.com/submissions/view/3\'>bug ID #00003</a> to review the submission and accept/reject accordingly. Thank you for being a valuable member of the PwnedHub community!',1,3,1),(9,'2019-02-18 14:12:57','2019-02-18 15:37:15','Submission Updated','A submission for which you are the reviewer has been updated. Please visit the submission page for <a href=\'http://pwnedhub.com/submissions/view/3\'>bug ID #00003</a> to review the updated submission and accept/reject accordingly. Thank you for being a valuable member of the PwnedHub community!',1,3,1),(10,'2019-02-18 14:21:01','2019-02-18 15:37:23','New Submission for Review','You\'ve been randomly selected to review a bug bounty submission. That means that you are eligible to receive 25% of the bounty allotted for an accepted review of this bug! Please visit the submission page for <a href=\'http://pwnedhub.com/submissions/view/4\'>bug ID #00004</a> to review the submission and accept/reject accordingly. Thank you for being a valuable member of the PwnedHub community!',1,3,1),(11,'2019-02-18 14:23:13','2019-02-18 15:43:15','Submission Updated','A submission for which you are the reviewer has been updated. Please visit the submission page for <a href=\'http://pwnedhub.com/submissions/view/4\'>bug ID #00004</a> to review the updated submission and accept/reject accordingly. Thank you for being a valuable member of the PwnedHub community!',1,3,1),(12,'2019-02-18 14:37:11','2019-02-18 15:39:12','New Submission for Review','You\'ve been randomly selected to review a bug bounty submission. That means that you are eligible to receive 25% of the bounty allotted for an accepted review of this bug! Please visit the submission page for <a href=\'http://pwnedhub.com/submissions/view/5\'>bug ID #00005</a> to review the submission and accept/reject accordingly. Thank you for being a valuable member of the PwnedHub community!',1,3,1),(13,'2019-02-18 14:38:21','2019-02-18 15:43:18','Submission Updated','A submission for which you are the reviewer has been updated. Please visit the submission page for <a href=\'http://pwnedhub.com/submissions/view/5\'>bug ID #00005</a> to review the updated submission and accept/reject accordingly. Thank you for being a valuable member of the PwnedHub community!',1,3,1),(14,'2019-02-18 14:39:08','2019-02-18 15:43:23','Submission Updated','A submission for which you are the reviewer has been updated. Please visit the submission page for <a href=\'http://pwnedhub.com/submissions/view/5\'>bug ID #00005</a> to review the updated submission and accept/reject accordingly. Thank you for being a valuable member of the PwnedHub community!',1,3,1),(15,'2019-02-18 14:46:42','2019-02-18 14:46:42','New Submission for Review','You\'ve been randomly selected to review a bug bounty submission. That means that you are eligible to receive 25% of the bounty allotted for an accepted review of this bug! Please visit the submission page for <a href=\'http://pwnedhub.com/submissions/view/6\'>bug ID #00006</a> to review the submission and accept/reject accordingly. Thank you for being a valuable member of the PwnedHub community!',1,2,0),(16,'2019-02-18 14:53:21','2019-02-18 15:41:28','New Submission for Review','You\'ve been randomly selected to review a bug bounty submission. That means that you are eligible to receive 25% of the bounty allotted for an accepted review of this bug! Please visit the submission page for <a href=\'http://pwnedhub.com/submissions/view/7\'>bug ID #00007</a> to review the submission and accept/reject accordingly. Thank you for being a valuable member of the PwnedHub community!',1,3,1),(17,'2019-02-18 14:58:10','2019-02-18 14:58:10','New Submission for Review','You\'ve been randomly selected to review a bug bounty submission. That means that you are eligible to receive 25% of the bounty allotted for an accepted review of this bug! Please visit the submission page for <a href=\'http://pwnedhub.com/submissions/view/8\'>bug ID #00008</a> to review the submission and accept/reject accordingly. Thank you for being a valuable member of the PwnedHub community!',1,2,0),(18,'2019-02-18 15:02:34','2019-02-18 15:42:17','New Submission for Review','You\'ve been randomly selected to review a bug bounty submission. That means that you are eligible to receive 25% of the bounty allotted for an accepted review of this bug! Please visit the submission page for <a href=\'http://pwnedhub.com/submissions/view/9\'>bug ID #00009</a> to review the submission and accept/reject accordingly. Thank you for being a valuable member of the PwnedHub community!',1,4,1),(19,'2019-02-18 15:08:22','2019-02-18 15:08:22','New Submission for Review','You\'ve been randomly selected to review a bug bounty submission. That means that you are eligible to receive 25% of the bounty allotted for an accepted review of this bug! Please visit the submission page for <a href=\'http://pwnedhub.com/submissions/view/10\'>bug ID #00010</a> to review the submission and accept/reject accordingly. Thank you for being a valuable member of the PwnedHub community!',1,2,0),(20,'2019-02-18 15:37:10','2019-02-18 15:44:31','Submission #00003 Rejected','We regret to inform you that your submission (<a href=\'http://pwnedhub.com/submissions/view/3\'>bug ID #00003</a>) has been rejected. If you believe a modified submission will increase the chances of a successful review, please submit again. Thank you for your participation.',1,2,1),(21,'2019-02-18 15:37:37','2019-02-18 15:42:55','Submission #00004 Confirmed','Congratulations! Your submission (<a href=\'http://pwnedhub.com/submissions/view/4\'>bug ID #00004</a>) has been confirmed as a valid bug. The bug has been disclosed to the public and your profile has been awarded 800 reputation points. Thank you for being a valuable member of the PwnedHub community!',1,4,1),(22,'2019-02-18 15:38:38','2019-02-18 15:44:37','Submission #00001 Confirmed','Congratulations! Your submission (<a href=\'http://pwnedhub.com/submissions/view/1\'>bug ID #00001</a>) has been confirmed as a valid bug. The bug has been disclosed to the public and your profile has been awarded 200 reputation points. Thank you for being a valuable member of the PwnedHub community!',1,2,1),(23,'2019-02-18 15:39:03','2019-02-18 15:44:40','Submission #00002 Confirmed','Congratulations! Your submission (<a href=\'http://pwnedhub.com/submissions/view/2\'>bug ID #00002</a>) has been confirmed as a valid bug. The bug has been disclosed to the public and your profile has been awarded 400 reputation points. Thank you for being a valuable member of the PwnedHub community!',1,2,1),(24,'2019-02-18 15:41:23','2019-02-18 15:44:44','Submission #00005 Confirmed','Congratulations! Your submission (<a href=\'http://pwnedhub.com/submissions/view/5\'>bug ID #00005</a>) has been confirmed as a valid bug. The bug has been disclosed to the public and your profile has been awarded 200 reputation points. Thank you for being a valuable member of the PwnedHub community!',1,2,1),(25,'2019-02-18 15:42:07','2019-02-18 15:44:46','Submission #00007 Confirmed','Congratulations! Your submission (<a href=\'http://pwnedhub.com/submissions/view/7\'>bug ID #00007</a>) has been confirmed as a valid bug. The bug has been disclosed to the public and your profile has been awarded 400 reputation points. Thank you for being a valuable member of the PwnedHub community!',1,2,1),(26,'2019-02-18 15:42:48','2019-02-18 15:44:48','Submission #00009 Confirmed','Congratulations! Your submission (<a href=\'http://pwnedhub.com/submissions/view/9\'>bug ID #00009</a>) has been confirmed as a valid bug. The bug has been disclosed to the public and your profile has been awarded 400 reputation points. Thank you for being a valuable member of the PwnedHub community!',1,2,1);
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
  `comment` text,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `messages`
--

LOCK TABLES `messages` WRITE;
/*!40000 ALTER TABLE `messages` DISABLE KEYS */;
INSERT INTO `messages` VALUES (1,'2015-10-28 04:55:11','2015-10-28 04:55:11','Hey, did you guys hear that we\'re having a security assessment this week?',3),(2,'2015-10-28 04:55:19','2015-10-28 04:55:19','No.',4),(3,'2015-10-28 04:56:09','2015-10-28 04:56:09','First I\'m hearing of it. I hope they don\'t find any bugs. This is my \"get rich quick\" scheme.',2),(4,'2015-10-28 04:57:02','2015-10-28 04:57:02','Heh. Me too. So looking forward to afternoons on my yacht. :-)',3),(5,'2015-10-28 04:57:32','2015-10-28 04:57:32','So, yeah, did any of you guys fix those things I found during peer review? I posted them in the slack channel. https://www.slack.com',3),(6,'2015-10-28 04:57:37','2015-10-28 04:57:37','No.',4),(7,'2015-10-28 04:57:41','2015-10-28 04:57:41','Nope.',2),(8,'2015-10-28 04:57:46','2015-10-28 04:57:46','Uh oh...',3);
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
  `modified` datetime NOT NULL,
  `player` varchar(255) NOT NULL,
  `score` int(11) NOT NULL,
  `recid` int(11) DEFAULT NULL,
  `recording` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `scores`
--

LOCK TABLES `scores` WRITE;
/*!40000 ALTER TABLE `scores` DISABLE KEYS */;
INSERT INTO `scores` VALUES (1,'2015-10-28 03:07:00','2015-10-28 03:07:00','Babygirl#1',50,8,'recTurn=230103230121030323012103210&recFrame=+r+b+4+3+4+7+i+f+9+3+8+5+7+i+b+j+1+g+1+g+g11+3+p+d+2+7&recFood=+n211k+lo+3q+ya+gc'),(2,'2015-10-28 05:31:19','2015-10-28 05:31:19','Cooperman',140,3,'recTurn=032101230123032101230121230103230321030321030123012321230301230&recFrame=+i+5+h+9+d+j+6+b+2+d+6+8+7+9+h+b+4+d+6+h+1+h+7+s+9+4+m+3+l+7+b+3+9+i+1+x+7+k+2+a+8+q+i+s+i+4+o+9+p+b+m+a+g+a+l+g+a+1+e+q+k+r+k&recFood=+hq+me+8a+3j+vb+qo15p+mj10s+9t+om13h+dn+v6+0c'),(3,'2015-10-28 05:32:13','2015-10-28 05:32:13','Hack3rPrincess',200,2,'recTurn=012323232103212301232103012321032301230103212103212321230301010323012303&recFrame=+f+j+5+3+c+a+1+9+1+b+h+o+f+1+f+h+4+i+5+m+e+9+f+c+q+p+7+c+1+g+m+5+a+2+8+o+710+c+9+1+t+5+a+1+o+m+r+m+6+e+8+9+9+f+6+g+3+6+k+9+1+j+3+c+1+a+9+j+3+e+1&recFood=+5d+ym+l5+d8+c8+y5174+lt+in+yb+uc+wn+vr+u5+c9+ie+zl14n+hb+fe+7k'),(4,'2015-10-28 05:32:37','2015-10-28 05:32:37','Babygirl#1',70,5,'recTurn=23230123230123012323010103212&recFrame=+h+6+c+7+6+v+p+e+2+h+8+f+a+7+f+e+e+r+a+1+a+7+5+1+f+1+n+3+e&recFood=+sk+9t+v6+kd+q515j+wk10f'),(5,'2015-10-28 05:37:26','2015-10-28 05:37:26','Babygirl#1',90,4,'recTurn=012301010303232301230123030121030&recFrame=+g+m+612+k+6+l+8+1+d+9+7+b+e+2+g+2+g+l+6+i+b+o+m+5+h+j+f+2+d+l+f+a&recFood=+1c12l+f4+4m+ir+np+s1+ii+fn+f3'),(6,'2015-10-28 05:34:21','2015-10-28 05:34:21','Cooperman',270,0,'recTurn=230103230123230123212103230103012301012121032123012323012323012301030123010301012321230301230121&recFrame=+m+g+e+1+e+i+6+n+a+u+h+8+2+k+e10+g+1+d+a+e+o+2+v+1+w+a+b+3+d+9+f+f13+m+a+5+n+f+c+4+f+1+t+j+1+f11+i10+h+c+1+m+j12+p10+g+2+a+z+q+y+p+l+a+2+a+9+j+x+i+a+g+g+h+d+c+1+b+9+b+1+a+x+k+e+5+s+r13+j+3+8+1&recFood=117+t616c+cf147+bl+5i+o4+q3+tc+fj+1c14n+86+j1125+in+s7+3214j+jh+v7+g9+19+bd18b11o147'),(7,'2015-10-28 05:34:34','2015-10-28 05:34:34','Hack3rPrincess',30,9,'recTurn=0321012323&recFrame=+h+3+g+8+5+q+8+2+d11&recFood=+kr+1l+rr+ft'),(8,'2015-10-28 05:34:56','2015-10-28 05:34:56','Cooperman',70,6,'recTurn=230301230323010101232123&recFrame=+n+b+6+o+e+1+j+9+2+c+f+t+3+9+1+6+1+b+5+e+6+f+h+2&recFood=+r5+fb+8a+68+ln+co11o10t'),(9,'2015-10-28 05:36:34','2015-10-28 05:36:34','Hack3rPrincess',260,1,'recTurn=03230301230123012321212301230103212123012321012303232301230321012303030123032301230101032301210123012321230323032121010321230&recFrame=+r+c+g+h+7+c+2+c+1+u+3+m+m+g+g+m+k+8+a+3+9+7+2+9+o+1+o+b+i+8+h+v+7+a+5+a+2+i+o11+6+c+1+a+5+l+f+r+3+8+8+1+b+b+1+z+m+m+4+k+n+p+p+p+113+7+b+1+5+1+n+8+v+1+r+1+v+c+y+e11+j+5+3+4+a+7+6+4+6+m+1+l+2+d+g+o+n11+l+1+g+1+h+a+8+3+6+h+1+j+1+m+e+c+1+k+4+j+n+u+e+6+e&recFood=+a2+gh+ep+is+r7+bm+d3+v2+f2155+hq+il+ph+18+dt+a4+jc+75+ei+sl13k+3k+cj+y5+ko+yb12g'),(10,'2015-10-28 05:36:53','2015-10-28 05:36:53','Cooperman',60,7,'recTurn=23012301210123010121230&recFrame=+l+9+5+7+6+a+m+h+2+i+p+k+1+g+h+9+2+g+1+r+7+6+7&recFood=+t6+v6+xs+qq+p0+ke+zb');
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
INSERT INTO `tools` VALUES (1,'2015-10-28 02:09:59','2015-10-28 02:09:59','Dig','dig','(Domain Internet Groper) Network administration tool for Domain Name System (DNS) name server interrogation.'),(2,'2015-10-28 02:10:29','2015-10-28 02:10:29','Nmap','nmap','(Network Mapper) Utility for network discovery and security auditing.'),(3,'2015-10-28 02:10:59','2015-10-28 02:10:59','Nikto','nikto','Signature-based web server scanner.'),(4,'2015-10-28 02:11:29','2015-10-28 02:11:29','SSLyze','sslyze','Fast and powerful SSL/TLS server scanning library.'),(5,'2015-10-28 02:11:59','2015-10-28 02:11:59','SQLmap','sqlmap --batch','Penetration testing tool that automates the process of detecting and exploiting SQL injection flaws.');
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
  `name` varchar(255) NOT NULL,
  `avatar` text,
  `signature` text,
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
INSERT INTO `users` VALUES (1,'2015-10-28 01:51:59','2015-10-28 01:51:59','admin','Administrator','/images/avatars/admin.png','All your base are belong to me.','EAoFAQYYGgEKBgwQ',1,'Ralf',NULL,0,1),(2,'2015-10-28 04:46:27','2015-10-28 04:46:27','Cooperman','Cooper','/images/avatars/c-man.png','Gamer, hacker, and basketball player. Energy sword FTW!','JxdbBwtAFwoZVFo=',3,'Augusta',NULL,1,1),(3,'2015-10-28 04:47:14','2015-10-28 04:47:14','Babygirl#1','Taylor','/images/avatars/wolf.jpg','Wolf in a past life. Nerd in the current. Johnny 5 is indeed alive.','EAoZAAwXBw0EABoREQQfBgwGChYfExkYFg==',2,'Rocket',NULL,1,1),(4,'2015-10-28 04:48:19','2015-10-28 04:48:19','Hack3rPrincess','Tanner','/images/avatars/kitty.jpg','I might be small, cute, and cuddly, but remember... dynamite comes in small tightly wrapped packages that go boom.','Cw4IFkcXHAhES1pCXA==',0,'Drumstick',NULL,1,1);
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

-- Dump completed on 2019-02-10  1:11:35
