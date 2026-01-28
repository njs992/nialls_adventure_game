/*

  HelloWorld.ino

  Universal 8bit Graphics Library (https://github.com/olikraus/u8g2/)

  Copyright (c) 2016, olikraus@gmail.com
  All rights reserved.

  Redistribution and use in source and binary forms, with or without modification, 
  are permitted provided that the following conditions are met:

  * Redistributions of source code must retain the above copyright notice, this list 
    of conditions and the following disclaimer.
    
  * Redistributions in binary form must reproduce the above copyright notice, this 
    list of conditions and the following disclaimer in the documentation and/or other 
    materials provided with the distribution.

  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND 
  CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, 
  INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF 
  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT 
  NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, 
  STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
  ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  

*/

#include <Arduino.h>
#include <U8g2lib.h>

#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif
#ifdef U8X8_HAVE_HW_I2C
#include <Wire.h>
#endif

/*
  U8g2lib Example Overview:
    Frame Buffer Examples: clearBuffer/sendBuffer. Fast, but may not work with all Arduino boards because of RAM consumption
    Page Buffer Examples: firstPage/nextPage. Less RAM usage, should work with all Arduino boards.
    U8x8 Text Only Example: No RAM usage, direct communication with display controller. No graphics, 8x8 Text only.
    
*/

U8G2_SSD1306_128X64_NONAME_F_4W_SW_SPI u8g2(U8G2_R0, /* clock=*/ 10, /* data=*/ 9, /* cs=*/ 12, /* dc=*/ 11, /* reset=*/ 13);

// const char* print_format( String s, uint8_t n )
// {
//   const uint8_t BUFLEN;
//   char buf[BUFLEN];
//   snprintf( buf, BUFLEN, "%s,% 2d\0", s, n );
//   return buf;
// }

void setup(void) {
  u8g2.begin();
}

void loop(void) {
  const size_t BUFLEN{30};
  char buf[BUFLEN];
  const String name{ "Luke Skywalker" };
  const int MAX_LIFE{15};
  int life{6};
  int might{2};
  int speed{7};
  int defense{12};
  int fortitude{14};
  int pow_bonus{1};
  int agy_bonus{0};
  int hrt_bonus{-1};
  int com_bonus{5};

  u8g2.clearBuffer();					// clear the internal memory
  u8g2.setColorIndex(1);
  u8g2.setFont(u8g2_font_tom_thumb_4x6_mf);	// choose a suitable font

  // snprintf(buf, BUFLEN, "%s", name);
  int name_xpos = 24 + ((128-24)/2);
  name_xpos -= ((name.length()*4)/2);
  u8g2.drawStr(name_xpos,6, name.c_str());
  u8g2.drawStr(0,6,"LIFE: ");
  snprintf(buf, BUFLEN, "%2d/%2d\0", life, MAX_LIFE);
  u8g2.drawStr(3,12, buf);
  snprintf(buf, BUFLEN, "MIT:%2d\0", might);
  u8g2.drawStr(0,20, buf);
  snprintf(buf, BUFLEN, "SPD:%2d\0", speed);
  u8g2.drawStr(0,26, buf);
  snprintf(buf, BUFLEN, "DEF:%2d\0", defense);
  u8g2.drawStr(0,32, buf);
  snprintf(buf, BUFLEN, "FOR:%2d\0", fortitude);
  u8g2.drawStr(0,38, buf);
  snprintf(buf, BUFLEN, "POW:%s%d\0", (pow_bonus>0)?"+":(pow_bonus<0)?"-":" ",abs(pow_bonus));
  u8g2.drawStr(0,46,buf);
  snprintf(buf, BUFLEN, "AGY:%s%d\0", (agy_bonus>0)?"+":(agy_bonus<0)?"-":" ",abs(agy_bonus));
  u8g2.drawStr(0,52,buf);
  snprintf(buf, BUFLEN, "HRT:%s%d\0", (hrt_bonus>0)?"+":(hrt_bonus<0)?"-":" ",abs(hrt_bonus));
  u8g2.drawStr(0,58,buf);
  snprintf(buf, BUFLEN, "COM:%s%d\0", (com_bonus>0)?"+":(com_bonus<0)?"-":" ",abs(com_bonus));
  u8g2.drawStr(0,64,buf);

  u8g2.drawLine(24, 0, 24, 64);
  u8g2.drawLine(25, 8, 128, 8);
  u8g2.drawLine(0, 13, 23, 13);
  u8g2.drawLine(0, 39, 23, 39);

  //up
  u8g2.drawRFrame(75-14, 15+5,25,9,3);
  u8g2.drawStr(75-11,15+12,"Index");
  //down
  u8g2.drawRFrame(75-16, 38+5,29,9,3);
  u8g2.drawStr(75-13,38+12,"Subtle");
  //left
  u8g2.drawRFrame(45-15, 26+5,29,9,3);
  u8g2.drawStr(45-12,26+12,"Player");
  //right
  u8g2.drawRFrame(105-17,26+5,33,9,3);
  // u8g2.setColorIndex(0);
  u8g2.drawStr(105-14,26+12,"Rolling");
  // u8g2.setColorIndex(1);

  u8g2.sendBuffer();					// transfer internal memory to the display
  delay(1000);  
}

