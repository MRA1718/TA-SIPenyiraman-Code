/***************************************************
     This example reads Analog Waterproof Capacitive Soil Moisture Sensor.

     Created 2019-10-25
     By Felix Fu <Felix.Fu@dfrobot.com>

     GNU Lesser General Public License.
     See <http://www.gnu.org/licenses/> for details.
     All above must be included in any redistribution
     ****************************************************/

    /***********Notice and Trouble shooting***************
     1.Connection and Diagram can be found here
     2.This code is tested on Arduino Uno.
     ****************************************************/

    const int AirValue = 645;   //you need to change this value that you had recorded in the air
    const int WaterValue = 70;  //you need to change this value that you had recorded in the water

    int intervals = (AirValue - WaterValue)/3;
    int soilMoistureValue = 0;
    void setup() {
      Serial.begin(115200); // open serial port, set the baud rate to 9600 bps
    }
    void loop() {
    soilMoistureValue = analogRead(A0);  //put Sensor insert into soil
    if(soilMoistureValue > WaterValue && soilMoistureValue < (WaterValue + intervals))
    {
      Serial.println("Very Wet");
    }
    else if(soilMoistureValue > (WaterValue + intervals) && soilMoistureValue < (AirValue - intervals))
    {
      Serial.println("Wet");
    }
    else if(soilMoistureValue < AirValue && soilMoistureValue > (AirValue - intervals))
    {
      Serial.println("Dry");
    }
    delay(500);
    }
