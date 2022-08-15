import serial
import time
from PyCRC.CRCCCITT import CRCCCITT


class FisbaReadyBeam():


    def __init__(
                 self,
                 port='/dev/ttyUSB0',
                 baud=57600,
                 timeout=1,
                ):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.sequence = 0
        self.address = 2
        self.open()


    def open(self):
        self.laser = serial.Serial(
                                   self.port,
                                   self.baud,
                                   timeout=self.timeout,
                                   write_timeout=self.timeout
                                  )
        self.laser.flushInput()
        self.laser.flushOutput()
        command = self.construct_command(2010)
        self.send_command(command)


    def close(self):
        self.laser.flushInput()
        self.laser.flushOutput()
        self.laser.close()
        del self.laser


    def read(self, size=1):
        incoming_data = self.laser.read(size=size)
        if len(incoming_data) < size:
            raise Exception('Communication timed out.')
        else:
            return incoming_data


    def send_command(self, command):
        self.laser.reset_output_buffer()
        self.laser.reset_input_buffer()
        self.laser.write(command)
        self.laser.flush()
        cr = "\r".encode()
        response_frame = b''
        response_byte = self.read(size=1)
        while response_byte != cr:
            response_frame += response_byte
            response_byte = self.read(size=1)
        response_frame = response_frame[1:]
        time.sleep(0.1)
        print(command.decode())
        print(response_frame.decode())
        return response_frame


    def construct_command(self, parameter_id, value=None, instance=1, address=0):
        command = '#{:02X}'.format(address)
        self.sequence += 1
        command += '{:04X}'.format(self.sequence)
        if isinstance(value, type(None)):
            command += '?VR'
        elif not isinstance(value, type(None)):
            command += 'VS'
        command += '{:04X}'.format(parameter_id)
        command += '{:02X}'.format(instance)
        if not isinstance(value, type(None)):
            if isinstance(value, float):
                converted_value = '41F00000'
                command += converted_value
#                command += '{:08X}'.format(converted_value) 
            elif isinstance(value, int):
                command += '{:08X}'.format(value)
        checksum = CRCCCITT().calculate(input_data=command.encode())
        command += '{:04X}'.format(checksum)
        command += '\r'
        return command.encode()

    
    def set_laser(self, power=[10., 0., 10.]):
        for i in range(len(power)):
            if power[i] > 0:
                value = 1
            else:
                value = 0
            command = self.construct_command(7000, value=value, instance=int(i+1), address=self.address)
            self.send_command(command)
            command = self.construct_command(7006, value=value, instance=int(i+1), address=self.address)
            self.send_command(command)
            command = self.construct_command(7013, value=power[i], instance=int(i+1), address=self.address)
            self.send_command(command)
            command = self.construct_command(7010, instance=int(i+1), address=self.address)
            self.send_command(command)