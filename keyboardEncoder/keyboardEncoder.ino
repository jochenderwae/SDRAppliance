#include <Keyboard.h>
#include <RotaryEncoder.h>

#define E1_SW 14
#define E1_DT 16
#define E1_CLK 10

#define E2_SW 7
#define E2_DT 8
#define E2_CLK 9

#define E3_SW 4
#define E3_DT 5
#define E3_CLK 6



RotaryEncoder encoder1(E1_DT, E1_CLK);
RotaryEncoder encoder2(E2_DT, E2_CLK);
RotaryEncoder encoder3(E3_DT, E3_CLK);

void setup() {
  // put your setup code here, to run once:
  Keyboard.begin();

  pinMode(E1_SW, INPUT_PULLUP);
  pinMode(E2_SW, INPUT_PULLUP);
  pinMode(E3_SW, INPUT_PULLUP);
}

void loop() {
  // put your main code here, to run repeatedly:
  static int pos1 = 0;
  static int pos2 = 0;
  static int pos3 = 0;
  encoder1.tick();
  encoder2.tick();
  encoder3.tick();

  bool sw1 = digitalRead(E1_SW) == LOW;
  bool sw2 = digitalRead(E2_SW) == LOW;
  bool sw3 = digitalRead(E3_SW) == LOW;

  int newPos = encoder1.getPosition();
  if (pos1 != newPos) {
    if(sw1) {
      Keyboard.press(KEY_LEFT_SHIFT);
    }
    if(pos1 > newPos) {
      Keyboard.press(KEY_LEFT_ARROW);
    } else {
      Keyboard.press(KEY_RIGHT_ARROW);
    }
    pos1 = newPos;
  } // if

  newPos = encoder2.getPosition();
  if (pos2 != newPos) {
    if(sw2) {
      //
    }
    if(pos2 > newPos) {
      Keyboard.press(KEY_UP_ARROW);
    } else {
      Keyboard.press(KEY_DOWN_ARROW);
    }
    delay(100);
    pos2 = newPos;
  } // if

  newPos = encoder3.getPosition();
  if (pos3 != newPos) {
    if(pos3 > newPos) {
      Keyboard.write(sw3?'E':'e');
    } else {
      Keyboard.write(sw3?'F':'f');
    }
    pos3 = newPos;
  } // if

  Keyboard.releaseAll();
}
