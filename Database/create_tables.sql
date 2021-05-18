CREATE DATABASE smart_garden_db;

USE smart_garden_db;

CREATE TABLE RecordingSession (
  SessionID INT UNSIGNED NOT NULL AUTO_INCREMENT,
  StartTime DATETIME NOT NULL
);

CREATE TABLE Device (
  DeviceID INT UNSIGNED NOT NULL AUTO_INCREMENT,
  SessionID INT UNSIGNED NOT NULL, 
  DeviceAddress VARCHAR(16) UNSIGNED NOT NULL,
  RegistrationTime DATETIME NOT NULL,
  FOREIGN KEY(RecordingSession) REFERENCES RecordingSession(SessionID),
  PRIMARY KEY (DeviceAddress)	
);

CREATE TABLE PlantReading (
  PlantRecord INT NOT NULL AUTO_INCREMENT,
  SessionID INT UNSIGNED NOT NULL,
  DeviceID INT UNSIGNED NOT NULL,
  MoistureContent FLOAT(4),
  Temperature FLOAT(4),
  Humidity FLOAT(4),
  Time DATETIME,
  FOREIGN KEY(RecordingSession) REFERENCES RecordingSession(SessionID),
  FOREIGN KEY(DeviceID) REFERENCES Device(DeviceID),
  PRIMARY KEY(PlantRecord)
);

CREATE TABLE Event (
  EventID INT NOT NULL AUTO_INCREMENT,
  SessionID INT UNSIGNED NOT NULL,
  SensorID INT UNSIGNED NOT NULL,
  ActuatorID INT UNSIGNED NOT NULL,
  Description TEXT,
  Time DATETIME,
  FOREIGN KEY(RecordingSession) REFERENCES RecordingSession(SessionID),
  FOREIGN KEY(SensorID) REFERENCES Device(DeviceID), 
  FOREIGN KEY(ActuatorID) REFERENCES Device(DeviceID),
  PRIMARY KEY(EventID)
);