#include <Adafruit_Fingerprint.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

#define TX D1
#define RX D2

#define MODE_IDLE 0
#define MODE_ENROLL 1
#define MODE_VERIFY 2
#define MODE_DELETE 3
#define MODE_DELETE_ALL 4

#define ENROLL_MODE_LED D5
#define VERIFY_MODE_LED D6
#define ACTIVE_MODE_LED D7

const char* server_url = "http://192.168.241.248:8000";
const char* is_active_api = "/fingerprint/is_active";
const char* mode_api = "/fingerprint/mode";
const char* enroll_api = "/fingerprint/enroll";
const char* verify_api = "/fingerprint/verify";
const char* delete_all_api = "/fingerprint/delete_all";

const char* ssid = "test";      
const char* password = "88888888"; 

SoftwareSerial mySerial(TX, RX); 
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);

volatile int finger_status = -1;
int mode = MODE_IDLE;  
uint8_t id = 1;


void manualFingerprintCommands() {
    
  if (Serial.available()) {
    char cmd = Serial.read();
    
    // Clear any remaining characters in the buffer
    while(Serial.available()) {
      Serial.read();
    }
    
    if (cmd == 'E' || cmd == 'e') {
      mode = MODE_ENROLL;
      Serial.println("Switched to Enroll Mode");
    } else if (cmd == 'V' || cmd == 'v') {
      mode = MODE_VERIFY;
      Serial.println("Switched to Verify Mode");
    } else if (cmd == 'D' || cmd == 'd') {
      mode = MODE_DELETE_ALL;
      Serial.println("Deleting all fingerprints...");
    }
  }

  if (mode == MODE_DELETE_ALL) {
    if (deleteAllFingerprints()) {
      Serial.println("All fingerprints deleted!");
    } else {
      Serial.println("Failed to delete all fingerprints!");
    }
    mode = MODE_IDLE;
  }
}

void setup()  
{
  Serial.begin(9600);
  while (!Serial); 
  delay(100);

  ledSetup();
  wifiSetup();
  fingerprintSetup();
}


void loop() {
  if (!checkIfActive()) {
    delay(1000);  
    return;
  }

  if (!checkMode()) {
    delay(1000);  
    return;
  }

  checkDeleteCommand();

  digitalWrite(ACTIVE_MODE_LED, HIGH);
  if (mode == MODE_ENROLL) {
    digitalWrite(ENROLL_MODE_LED, HIGH);
    getFingerprintEnroll();
    digitalWrite(ENROLL_MODE_LED, LOW);
    digitalWrite(ACTIVE_MODE_LED, LOW);
    delay(5000);

    mode = MODE_VERIFY;
  
  } else if (mode == MODE_VERIFY) {
    digitalWrite(VERIFY_MODE_LED, HIGH);
    finger_status = getFingerprintIDez();
    if (finger_status != -1 && finger_status != -2) {
      Serial.print("Match");
      String jsonData = "{\"match_id\": " + String(finger_status) + "}";
      postVerificationResult(jsonData);
      digitalWrite(ACTIVE_MODE_LED, LOW);
      delay(5000);
    } else {
      if (finger_status == -2) {
        String jsonData = "{\"match_id\": -1}";
        postVerificationResult(jsonData);
        for (int ii = 0; ii < 5; ii++) {
          Serial.print("Not Match");
        }
        digitalWrite(ACTIVE_MODE_LED, LOW);
        delay(5000);
      }
    }
    digitalWrite(VERIFY_MODE_LED, LOW);
  }
  
  delay(50);
}

void ledSetup() {
  pinMode(ENROLL_MODE_LED, OUTPUT);
  pinMode(VERIFY_MODE_LED, OUTPUT);
  pinMode(ACTIVE_MODE_LED, OUTPUT);

  digitalWrite(ENROLL_MODE_LED, HIGH);
  digitalWrite(VERIFY_MODE_LED, HIGH);
  digitalWrite(ACTIVE_MODE_LED, HIGH);
  delay(1000);
  digitalWrite(ENROLL_MODE_LED, LOW);
  digitalWrite(VERIFY_MODE_LED, LOW);
  digitalWrite(ACTIVE_MODE_LED, LOW);
}


void fingerprintSetup() {
  Serial.println("\n\nAdafruit Fingerprint sensor enrollment");
  finger.begin(57600);
  
  if (finger.verifyPassword()) {
    Serial.println("Found fingerprint sensor!");
  } else {
    Serial.println("Did not find fingerprint sensor :(");
    while (1) { delay(1); }
  }
}

void wifiSetup() {
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected to WiFi!");
}

bool checkIfActive() {
  WiFiClient client;
  HTTPClient http;
  
  String url = String(server_url) + String(is_active_api);
  
  http.begin(client, url);
  int httpResponseCode = http.GET();
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    http.end();
    
    return response.indexOf("true") > -1;
  }
  
  http.end();
  return false; 
}


int getFingerprintIDez() {
  uint8_t p = finger.getImage();
  if (p != 2) {
    //Serial.println(p);
  }
  if (p != FINGERPRINT_OK) return -1;
  
  p = finger.image2Tz();
  if (p != 2) {
    //Serial.println(p);
  }
  if (p != FINGERPRINT_OK) return -1;

  p = finger.fingerFastSearch();
  if (p != FINGERPRINT_OK) return -2;
  
  Serial.print("Found ID #"); Serial.print(finger.fingerID); 
  Serial.print(" with confidence of "); Serial.println(finger.confidence);
  return finger.fingerID; 
}

bool isIdTaken(uint8_t id) {
  uint8_t p = finger.loadModel(id);
  if (p == FINGERPRINT_OK) {
    return true;  
  }
  return false;  
}


uint8_t getNextAvailableId() {
  uint8_t id = 1;
  while (id <= 127) {  // 127 max ID
    if (!isIdTaken(id)) {
      return id;
    }
    id++;
  }
  return 0; 
}

void sendEnrollmentStatus(String status, String message, String finger) {
    WiFiClient client;
    HTTPClient http;
    
    String url = String(server_url) + "/fingerprint/enrollment_status";
    String jsonData = "{\"status\": \"" + status + "\", \"message\": \"" + message + "\", \"finger\": \"" + finger + "\"}";
    
    http.begin(client, url);
    http.addHeader("Content-Type", "application/json");
    
    int httpResponseCode = http.POST(jsonData);
    Serial.println("Enrollment status: " + status + " - " + message + " (" + finger + ")");
    http.end();
}

uint8_t getFingerprintEnroll() {
    int p = -1;
    uint8_t mainId = 0;  // Declare mainId
    uint8_t backupId = 0; // Declare backupId

    id = getNextAvailableId();
    if (id == 0) {
      Serial.println("No free slot available!");
      return FINGERPRINT_NOFINGER;
    }
    
    // Enroll main finger
    Serial.println("\nReady to enroll main finger!");
    sendEnrollmentStatus("idle", "Place main finger on sensor", "main");
    
    bool mainEnrolled = false;
    
    while (!mainEnrolled) {
        p = finger.getImage();
        switch (p) {
            case FINGERPRINT_OK:
                Serial.println("Image taken");
                sendEnrollmentStatus("idle", "Image taken", "main");
                break;
            case FINGERPRINT_NOFINGER:
                Serial.println(".");
                continue;
            case FINGERPRINT_PACKETRECIEVEERR:
                Serial.println("Communication error");
                sendEnrollmentStatus("fail", "Communication error", "main");
                continue;
            case FINGERPRINT_IMAGEFAIL:
                Serial.println("Imaging error");
                sendEnrollmentStatus("fail", "Imaging error", "main");
                continue;
            default:
                Serial.println("Unknown error");
                sendEnrollmentStatus("fail", "Unknown error", "main");
                continue;
        }

        p = finger.image2Tz(1);
        if (p != FINGERPRINT_OK) {
            Serial.println("Conversion error");
            sendEnrollmentStatus("fail", "Conversion error, please try again.", "main");
            continue;
        }

        Serial.println("Remove finger");
        sendEnrollmentStatus("idle", "Remove finger", "main");
        delay(2000);
        p = 0;
        while (p != FINGERPRINT_NOFINGER) {
            p = finger.getImage();
        }

        p = -1;
        Serial.println("Place same finger again");
        sendEnrollmentStatus("idle", "Place same finger again", "main");
        while (p != FINGERPRINT_OK) {
            p = finger.getImage();
        }

        p = finger.image2Tz(2);
        if (p != FINGERPRINT_OK) {
            Serial.println("Conversion error");
            sendEnrollmentStatus("fail", "Conversion error, please try again.", "main");
            continue;
        }

        p = finger.createModel();
        if (p != FINGERPRINT_OK) {
            Serial.println("Model error");
            sendEnrollmentStatus("fail", "Model error, please try again.", "main");
            continue;
        }

        mainId = id++; // Assign mainId
        p = finger.storeModel(mainId);
        if (p == FINGERPRINT_OK) {
            Serial.println("Stored main finger successfully!");
            sendEnrollmentStatus("success", "Main finger enrolled successfully", "main");
            mainEnrolled = true;
        } else {
            Serial.println("Failed to store main finger");
            sendEnrollmentStatus("fail", "Failed to store main finger", "main");
        }
    }

    // Enroll backup finger
    Serial.println("\nReady to enroll backup finger!");
    sendEnrollmentStatus("idle", "Place backup finger on sensor", "backup");
    
    bool backupEnrolled = false;
    
    while (!backupEnrolled) {
        p = finger.getImage();
        switch (p) {
            case FINGERPRINT_OK:
                Serial.println("Image taken");
                sendEnrollmentStatus("idle", "Image taken", "backup");
                break;
            case FINGERPRINT_NOFINGER:
                Serial.println(".");
                continue;
            case FINGERPRINT_PACKETRECIEVEERR:
                Serial.println("Communication error");
                sendEnrollmentStatus("fail", "Communication error", "backup");
                continue;
            case FINGERPRINT_IMAGEFAIL:
                Serial.println("Imaging error");
                sendEnrollmentStatus("fail", "Imaging error, please try again.", "backup");
                continue;
            default:
                Serial.println("Unknown error");
                sendEnrollmentStatus("fail", "Unknown error", "backup");
                continue;
        }

        p = finger.image2Tz(1);
        if (p != FINGERPRINT_OK) {
            Serial.println("Conversion error");
            sendEnrollmentStatus("fail", "Conversion error, please try again.", "backup");
            continue;
        }

        Serial.println("Remove finger");
        sendEnrollmentStatus("idle", "Remove finger", "backup");
        delay(2000);
        p = 0;
        while (p != FINGERPRINT_NOFINGER) {
            p = finger.getImage();
        }

        p = -1;
        Serial.println("Place same finger again");
        sendEnrollmentStatus("idle", "Place same finger again", "backup");
        while (p != FINGERPRINT_OK) {
            p = finger.getImage();
        }

        p = finger.image2Tz(2);
        if (p != FINGERPRINT_OK) {
            Serial.println("Conversion error");
            sendEnrollmentStatus("fail", "Conversion error, please try again.", "backup");
            continue;
        }

        p = finger.createModel();
        if (p != FINGERPRINT_OK) {
            Serial.println("Model error");
            sendEnrollmentStatus("fail", "Model error, please try again.", "backup");
            continue;
        }

        backupId = id++; // Assign backupId
        p = finger.storeModel(backupId);
        if (p == FINGERPRINT_OK) {
            Serial.println("Stored backup finger successfully!");
            sendEnrollmentStatus("success", "Backup finger enrolled successfully", "backup");
            backupEnrolled = true;
        } else {
            Serial.println("Failed to store backup finger");
            sendEnrollmentStatus("fail", "Failed to store backup finger", "backup");
        }
    }

    Serial.println("Enrollment complete!");
    
    // Create and send final JSON response
    String jsonResponse = "{\"main\": " + String(mainId) + ", \"backup\": " + String(backupId) + "}";
    Serial.println("Enrollment complete. JSON response: " + jsonResponse);
    
    if (sendPostRequest(jsonResponse)) {
        Serial.println("Successfully sent to server");
        
        // Switch back to verify mode
        WiFiClient client;
        HTTPClient http;
        String url = String(server_url) + String(mode_api);
        String modeData = "{\"mode\": \"verify\"}";
        
        http.begin(client, url);
        http.addHeader("Content-Type", "application/json");
        
        int httpResponseCode = http.POST(modeData);
        if (httpResponseCode > 0) {
            Serial.println("Successfully switched to verify mode");
            mode = MODE_VERIFY;
        }
        http.end();
    }
    
    return FINGERPRINT_OK;
}

bool sendPostRequest(String jsonData) {
  WiFiClient client;
  HTTPClient http;
  
  String url = String(server_url) + String(enroll_api);
  
  http.begin(client, url);
  http.addHeader("Content-Type", "application/json");
  
  int httpResponseCode = http.POST(jsonData);
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("HTTP Response code: " + String(httpResponseCode));
    Serial.println("Response: " + response);
    http.end();
    return true;
  } else {
    Serial.print("Error code: ");
    Serial.println(httpResponseCode);
    http.end();
    return false;
  }
}

// Must be used at the end of getFingerprintEnroll
bool postVerifyMode() {
  WiFiClient client;
  HTTPClient http;
  
  String url = String(server_url) + String(mode_api);
  
  http.begin(client, url);
  http.addHeader("Content-Type", "application/json");
  
  String jsonData = "{\"mode\": \"verify\"}";
  int httpResponseCode = http.POST(jsonData);
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("HTTP Response code: " + String(httpResponseCode));
    //Serial.println("Response: " + response);
    return true;
  } else {
    Serial.print("Error code: ");
    Serial.println(httpResponseCode);
     return false;
  }
  http.end();
}

bool postVerificationResult(String jsonData) {
  WiFiClient client;
  HTTPClient http;
  
  String url = String(server_url) + String(verify_api);
  
  http.begin(client, url);
  http.addHeader("Content-Type", "application/json");
  
  int httpResponseCode = http.POST(jsonData);
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("HTTP Response code: " + String(httpResponseCode));
    //Serial.println("Response: " + response);
    http.end();
    return true;
  } else {
    Serial.print("Error code: ");
    Serial.println(httpResponseCode);
    http.end();
    return false;
  }
}

bool checkMode() {
  WiFiClient client;
  HTTPClient http;
  
  String url = String(server_url) + String(mode_api);
  
  http.begin(client, url);
  int httpResponseCode = http.GET();
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    http.end();
    
    if (response.indexOf("enroll") > -1) {
      mode = MODE_ENROLL;
      return true;
    } else if (response.indexOf("verify") > -1) {
      mode = MODE_VERIFY;
      return true;
    }
  }
  
  http.end();
  return false;
}

bool deleteAllFingerprints() {
  Serial.println("Deleting all fingerprint templates...");
  
  for (int i = 1; i <= 127; i++) {
    if (finger.deleteModel(i) == FINGERPRINT_OK) {
      Serial.print("Deleted ID #");
      Serial.println(i);
    }
  }
  
  return true;
}

void checkDeleteCommand() {
    WiFiClient client;
    HTTPClient http;
    
    String url = String(server_url) + String(delete_all_api);
    
    http.begin(client, url);
    int httpResponseCode = http.GET();
    
    if (httpResponseCode > 0) {
        String response = http.getString();
        if (response.indexOf("true") > -1) {
            if (deleteAllFingerprints()) {
                Serial.println("All fingerprints deleted successfully");
            } else {
                Serial.println("Error deleting fingerprints");
            }
        }
    }
    http.end();
}
