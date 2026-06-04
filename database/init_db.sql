-- MySQL dump 10.13  Distrib 8.0.19, for Win64 (x86_64)
--
-- Host: localhost    Database: mec_db
-- ------------------------------------------------------
-- Server version	8.0.43

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
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `category_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `hex_color` varchar(7) NOT NULL,
  PRIMARY KEY (`category_id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'Vaciado de Casa','#F1C40F'),(2,'Vintage','#8B4513'),(3,'Solidario','#E74C3C'),(4,'Upcycling','#9B59B6'),(5,'Liquidación','#2ECC71'),(11,'Vecinal','#3498DB');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `events`
--

DROP TABLE IF EXISTS `events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `events` (
  `event_id` int NOT NULL AUTO_INCREMENT,
  `organizer_id` int NOT NULL,
  `category_id` int NOT NULL,
  `title` varchar(150) NOT NULL,
  `description` text,
  `address` varchar(255) NOT NULL,
  `latitude` decimal(10,8) NOT NULL,
  `longitude` decimal(11,8) NOT NULL,
  `start_date` datetime NOT NULL,
  `end_date` datetime NOT NULL,
  `photo_url` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`event_id`),
  KEY `id_organizador` (`organizer_id`),
  KEY `id_categoria` (`category_id`),
  CONSTRAINT `events_ibfk_1` FOREIGN KEY (`organizer_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `events_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `events`
--

LOCK TABLES `events` WRITE;
/*!40000 ALTER TABLE `events` DISABLE KEYS */;
INSERT INTO `events` VALUES (23,9,1,'Vaciado de piso ','Nuevo mercadillo de economía circular.','Calle Gran Via , Vigo',42.19863950,-8.72795600,'2026-06-17 00:00:00','2026-06-17 00:00:00','http://localhost:5000/static/img_eventos/23/img_0.png,http://localhost:5000/static/img_eventos/23/img_1.png,http://localhost:5000/static/img_eventos/23/img_2.jpeg');
/*!40000 ALTER TABLE `events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `favorites`
--

DROP TABLE IF EXISTS `favorites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `favorites` (
  `user_id` int NOT NULL,
  `event_id` int NOT NULL,
  PRIMARY KEY (`user_id`,`event_id`),
  KEY `id_evento` (`event_id`),
  CONSTRAINT `favorites_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `favorites_ibfk_2` FOREIGN KEY (`event_id`) REFERENCES `events` (`event_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `favorites`
--

LOCK TABLES `favorites` WRITE;
/*!40000 ALTER TABLE `favorites` DISABLE KEYS */;
/*!40000 ALTER TABLE `favorites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `users_name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `user_type` enum('organizador','visitante') NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `photo_url` varchar(255) DEFAULT NULL,
  `registry_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `verified_email` tinyint(1) DEFAULT '0',
  `token_verified` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Antia Pardo Jimenez','apardo@mercadillosencasa.com','1234','organizador',NULL,NULL,'2026-04-07 14:52:58',0,NULL),(2,'Antía Pardo Jiménez','pardojimenezantia@gmail.com','scrypt:32768:8:1$KZfgL6pW4sWiFpz6$78e236682c4d2cdb7c3b74c4d6fcfdce62b1d5009e2b4eec49518598bd3499b79733a07349c896d91bbcfa86bee7aca68ed5b4203cc973073553844c747ffeaa','visitante','689398028',NULL,'2026-04-22 16:07:12',1,NULL),(9,'Antía Pardo Jiménez','apardo@sereniasolutions.com','scrypt:32768:8:1$luelKjKoLlJg66Bt$be0d1aae5c502c2f42fd85e5e3ca2edd46bedc1eb4137cff3bf9097f0bbec30400e5c425066389a79262e51bc871c4c15b6090530aedc4e99b41424e25c3d26e','organizador','','http://localhost:5000/static/img_perfil/9/profile_imagen.png','2026-04-29 17:26:47',1,NULL),(10,'Ana Garcia ','ana@gmail.com','scrypt:32768:8:1$r47NEmehdReQ7ySp$e017f13e68a9665974c28eed80605b8337aa825cd72052794daf68667be5f76df2544f3935d06da37cf1668cd8622d3f9f3c938676c7e1d34b1bdc5eaa032603','visitante','',NULL,'2026-04-29 17:38:22',1,NULL),(11,'Ana Garcia Ben ','anitagben@gmail.com','scrypt:32768:8:1$CM4TGwJJ23gGDlAG$cec891838fce566ffc162cf5999c28d7967d8b90c61b07317d6559446cd1dc3ff08c2351d85fc14a7b1aee6983b902ed17ad176396eea43aa0d8e33e11dcd193','visitante','',NULL,'2026-05-14 18:10:08',0,'dc17f826-ae1e-494d-8629-6c8c68e7cc6b');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'mec_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-04 12:20:09
