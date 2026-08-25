// Define the 2-byte framing marker Python is looking for
const byte markerA = 0xAA;
const byte markerB = 0xBB;

// Define the button pins
const int ECOFLEX_BTN= 52;
const int CELLOPHANE_BTN_UP = 48;
const int CELLOPHANE_BTN_SIDE= 50;

const int RECORD_POINT_BTN = 53;

// Array to hold the 6 analog readings + 1 label
unsigned int payload[7]; 

void setup() {
  Serial.begin(115200);
  
  // Enable internal pull-up resistors (buttons read LOW when pressed)
  pinMode(ECOFLEX_BTN, INPUT_PULLUP);
  pinMode(CELLOPHANE_BTN_UP, INPUT_PULLUP);
  pinMode(CELLOPHANE_BTN_SIDE, INPUT_PULLUP);

  pinMode(RECORD_POINT_BTN, INPUT_PULLUP);
}

void loop() {
  // 1. Read all 6 pins
  payload[0] = analogRead(A0);
  payload[1] = analogRead(A1);
  payload[2] = analogRead(A2);
  payload[3] = analogRead(A3);
  payload[4] = analogRead(A4);
  payload[5] = analogRead(A5);

  // 2. Check buttons and assign the label
  if (digitalRead(ECOFLEX_BTN) == LOW) {
    payload[6] = 1; // Ecoflex label
  } else if (digitalRead(CELLOPHANE_BTN_UP) == LOW) {
    payload[6] = 2; // Cellophane label (A oritetantion)

  } else if (digitalRead(CELLOPHANE_BTN_SIDE)==LOW) {
    payload[6] = 3; // Cellophane Label (B oritnetaion)
  }
  else if (digitalRead(RECORD_POINT_BTN) == LOW) {
    payload[6] = 4;

  } else {
    payload[6] = 0; // No button held
  }

  // 3. Send the synchronization markers
  Serial.write(markerA);
  Serial.write(markerB);

  // 4. Send the payload (7 integers * 2 bytes each = 14 bytes transmitted)
  Serial.write((byte*)payload, sizeof(payload));
}