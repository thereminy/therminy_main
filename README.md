# thereminy_main

Theremin-y: Create music with friends by moving your hands

Find the musician inside of you with Theremin-y! In this project, we are implementing a method to create a musical piece with friends by just moving your hands. There are two main components for the hardware setup: a piece with a Phototransistor and another with an IMU. We will call these pieces Relative-Note-Changer (RNC) and Beat-Establisher (BE), each connected to the ESP. 

The "musician" will first initiate (turn on) their ESP, which will establish a connection with Theremin-y, the server side of this project. Once all of the "musicians" have connected, they click a button to indicate they are ready to "compose". Once the "musician" has connected to Theremin-y, will then have S seconds to write their own part of the music using the RNC and BE, being provided the beats-per-minute by Theremin-y. When the seconds have passed, the data gathered will be sent to Theremin-y, which will interpret the pitch and length of the notes sent by the "musicians", unite them and play the song. To "compose" music, the musicians will be able to change the relative pitch of a base note moving their hands closer or further away from the RNC. Furthermore, shaking the BE will indicate the end of the previous note and the start of the following note. 
