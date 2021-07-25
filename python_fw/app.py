# import network
# ap = network.WLAN(network.AP_IF) # create access-point interface
# ap.config(essid='AutoBoat') # set the ESSID of the access point
# ap.config(max_clients=10) # set how many clients can connect to the network
# ap.active(True)         # activate the interface

# import usocket as socket
# import uselect as select

try:
    import uasyncio as asyncio
except:
    import asyncio

import time
import math
from machine import ADC, Pin, PWM

class Autoboat:
    def __init__(self) -> None:
        pass

    async def adc_reader(self):
        adc_left = ADC(Pin(32))     
        adc_right = ADC(Pin(33))     

        adc_left.atten(ADC.ATTN_11DB)   
        adc_left.width(ADC.WIDTH_12BIT)    

        adc_right.atten(ADC.ATTN_11DB)   
        adc_right.width(ADC.WIDTH_12BIT)    

        prev_left = 0
        prev_right = 0

        pwm_left = PWM(Pin(22)) 
        pwm_right = PWM(Pin(23)) 
        pwm_left.freq(100)
        pwm_left.duty(self.map_motor_control_to_duty(0.0))
        pwm_right.freq(100)
        pwm_right.duty(self.map_motor_control_to_duty(0.0))

        print("Duty for full back: ", self.map_motor_control_to_duty(-1.0))
        print("Duty for full forward: ", self.map_motor_control_to_duty(1.0))
        print("Duty for stop: ", self.map_motor_control_to_duty(0.0))

        coef = 0.5
        threshold = 0.1

        while True:
            await asyncio.sleep_ms(10)
            left_voltage = (float(adc_left.read())/4095.0 - 0.5) * 2.0
            right_voltage = (float(adc_right.read())/4095.0  - 0.5) * 2.0

            if math.fabs(left_voltage) < threshold:
                left_voltage = 0
            else:
                if left_voltage > 0:
                    left_voltage = left_voltage - threshold
                else:
                    left_voltage = left_voltage + threshold
            if math.fabs(right_voltage) < threshold:
                right_voltage = 0
            else:
                if right_voltage > 0:
                    right_voltage = right_voltage - threshold
                else:
                    right_voltage = right_voltage + threshold

            if prev_left != left_voltage or prev_right != right_voltage:
                print(left_voltage, right_voltage)

            forward = left_voltage * coef
            yaw = right_voltage * coef
            pwm_left.duty(self.map_motor_control_to_duty(forward + yaw))
            pwm_right.duty(self.map_motor_control_to_duty(forward - yaw))


    async def blinker(self):
        p = Pin(2, Pin.OUT)    
        while True:
            await asyncio.sleep(0.5)
            p.on()
            await asyncio.sleep(0.5)
            p.off()
   
    def map_motor_control_to_duty(self, motor_control_normalized):
        if motor_control_normalized > 1.0:
            motor_control_normalized = 1.0
        if motor_control_normalized < -1.0:
            motor_control_normalized = -1.0
        pulse_width = 1500.0e-6 + 400.0e-6 * motor_control_normalized
        freq = 100.0
        period = 1.0/freq
        duty = pulse_width/period
        return int(duty * 1023.0)

    async def main(self):
        asyncio.create_task(self.adc_reader())
        asyncio.create_task(self.blinker())
        # asyncio.create_task(self.api_server())
      

        while True:
            await asyncio.sleep(0.5)
            # print(time.time())

    async def handle_echo(reader, writer):
        print("here")
        data = await reader.read(100)
        message = data.decode()
        addr = writer.get_extra_info('peername')

        print("Received  from ", message, addr)

        print("Send: ", message)
        writer.write(data)
        await writer.drain()

        print("Close the connection")
        writer.close()

    async def api_server(self):
        server = await asyncio.start_server(
            Autoboat.handle_echo, '192.168.4.1', 8888)

        # addr = server.sockets[0].getsockname()
        print('Serving on ')

        async with server:
            await server.serve_forever()