""" Classes for pixy2 data.

Note: for i2c communication two modules are used at the moment:
      - smbus2 for most requests
      - smbus for setting default_turn and next_turn

      smbus2 is used because smbus is limited to 32 bytes which is too short
      for requesting mainFeatures.
      But I can't get smbus2 working proberly to set default_turn and
      next_turn. Values for both turns can range between -90 and 90 degrees
      and smbus2 doesn't accept negative values.
      Further investigation is required to find solution that is only using
      one module for i2c communication.
"""
from smbus2 import SMBusWrapper, i2c_msg
from smbus import SMBus

# Barcode constants
BARCODE_FORWARD = 1
BARCODE_LEFT = 0
BARCODE_RIGHT = 5
BARCODE_DEACTIVATE = 12
BARCODE_ACTIVATE = 13


class Pixy2:
    def __init__(self):
        # Set address for i2c communication (set on Pixy2 camera with PixyMon)
        self.i2c_address = 0x54
        self.bus_smbus = SMBus(3)
        # Settings for linetraacking (see wiki Pixycam.com)
        self._mode = 0
        self._default_turn = 0
        self._next_turn = 0

    def lamp_on(self):
        """Turn lamp on."""
        with SMBusWrapper(3) as bus:
            msg = i2c_msg.write(self.i2c_address, [174, 193, 22, 2, 1, 0])
            bus.i2c_rdwr(msg)

    def lamp_off(self):
        """Turn lamp off."""
        with SMBusWrapper(3) as bus:
            msg = i2c_msg.write(self.i2c_address, [174, 193, 22, 2, 0, 0])
            bus.i2c_rdwr(msg)

    def set_mode(self, mode):
        """Set mode for Pixy2."""
        with SMBusWrapper(3) as bus:
            msg = i2c_msg.write(self.i2c_address, [174, 193, 54, 1, 0])
            bus.i2c_rdwr(msg)
        self._mode = mode

    def getdata(self):
        """Get linetracking data form pixy2."""
        # i2C r/w transaction
        msg_w = i2c_msg.write(self.i2c_address, [174, 193, 48, 2, 0, 7])
        msg_r = i2c_msg.read(self.i2c_address, 64)
        with SMBusWrapper(3) as bus:
            bus.i2c_rdwr(msg_w, msg_r)
        return msg_r

    def set_vector(self, index):
        """Set vector for Pixy2 to follow."""
        msg_w = i2c_msg.write(self.i2c_address, [174, 193, 56, 1, index])
        msg_r = i2c_msg.read(self.i2c_address, 10)
        with SMBusWrapper(3) as bus:
            bus.i2c_rdwr(msg_w, msg_r)
        return msg_r

    def set_next_turn(self, angle):
        """Set direction robot has to take at intersection."""
        if angle >= 0:
            data = [174, 193, 58, 2, angle, 0]
        else:
            data = [174, 193, 58, 2, angle, -1]
        self.bus_smbus.write_i2c_block_data(self.i2c_address, 0, data)
        msg_r = self.bus_smbus.read_i2c_block_data(self.i2c_address, 0, 10)
        self._next_turn = angle
        return msg_r

    def set_default_turn(self, angle):
        """"Set direction robot has to take at intersection."""
        if angle >= 0:
            data = [174, 193, 60, 2, angle, 0]
        else:
            data = [174, 193, 60, 2, angle, -1]
        self.bus_smbus.write_i2c_block_data(self.i2c_address, 0, data)
        msg_r = self.bus_smbus.read_i2c_block_data(self.i2c_address, 0, 10)
        self._next_turn = angle
        return msg_r


class Vector:
    def __init__(self):
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        self.index = 0
        self.flags = 0


class Intersection:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.nr_of_branches = 0
        self.branches = []

    def add_branch(self, branch):
        b = Branch()
        b.index = branch.index
        b.angle = branch.angle
        self.branches.append(b)


class Branch:
    def __init__(self):
        self.index = 0
        self.angle = 0
        self.angle_byte1 = 0
        self.angle_byte2 = 0


class Barcode:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.flags = 0
        self.code = 0


class MainFeatures:
    def __init__(self):
        self.error = False
        self.type_of_packet = 49
        self.length_of_payload = 0
        self.number_of_vectors = 0
        self.number_of_intersections = 0
        self.number_of_barcodes = 0
        self.vectors = []
        self.intersections = []
        self.barcodes = []

    def add_vector(self, vector):
        v = Vector()
        v.x0 = vector.x0
        v.y0 = vector.y0
        v.x1 = vector.x1
        v.y1 = vector.y1
        v.index = vector.index
        v.flags = vector.flags
        self.vectors.append(v)
        self.number_of_vectors += 1

    def add_intersection(self, intersection):
        ints = Intersection()
        b = Branch()
        ints.x = intersection.x
        ints.y = intersection.y
        ints.nr_of_branches = intersection.nr_of_branches
        for branch in intersection.branches:
            b.index = branch.index
            b.angle = branch.angle
            b.angle_byte1 = branch.angle_byte1
            b.angle_byte2 = branch.angle_byte2
            ints.add_branch(b)
        self.intersections.append(ints)
        self.number_of_intersections += 1

    def add_barcode(self, barcode):
        b = Barcode()
        b.x = barcode.x
        b.y = barcode.y
        b.flags = barcode.flags
        b.code = barcode.code
        self.barcodes.append(b)
        self.number_of_barcodes += 1

    def clear(self):
        self.length_of_payload = 0
        self.number_of_vectors = 0
        self.number_of_intersections = 0
        self.number_of_barcodes = 0
        self.vectors.clear()
        self.intersections.clear()
        self.barcodes.clear()


def parse_pixy2_data(type, data):
    if type == 49:
        block = parse_main_features(data)
        return block


def parse_main_features(data):
    main_features = MainFeatures()
    vector = Vector()
    intersection = Intersection()
    branch = Branch()
    barcode = Barcode()
    main_features.length_of_payload = int.from_bytes(data.buf[3], 'little')
    i_payload = 0
    while i_payload < main_features.length_of_payload:
        feature_type = int.from_bytes(data.buf[6+i_payload], 'little')
        feature_length = int.from_bytes(data.buf[7+i_payload], 'little')
        if feature_type == 1:
            # Feature type is 'vector'
            vector.x0 = int.from_bytes(data.buf[8+i_payload], 'little')
            vector.y0 = int.from_bytes(data.buf[9+i_payload], 'little')
            vector.x1 = int.from_bytes(data.buf[10+i_payload], 'little')
            vector.y1 = int.from_bytes(data.buf[11+i_payload], 'little')
            vector.index = int.from_bytes(data.buf[12+i_payload], 'little')
            vector.flags = int.from_bytes(data.buf[13+i_payload], 'little')
            main_features.add_vector(vector)
        elif feature_type == 2:
            # feature type is 'intersection'
            intersection.x = int.from_bytes(data.buf[8+i_payload], 'little')
            intersection.y = int.from_bytes(data.buf[9+i_payload], 'little')
            intersection.nr_of_branches = int.from_bytes(
                data.buf[10+i_payload], 'little')
            for i in range(0, intersection.nr_of_branches):
                ii = i_payload+4*i
                branch.index = int.from_bytes(data.buf[12+ii],
                                              byteorder='little', signed=False)
                branch.angle = int.from_bytes(data.buf[14+ii]+data.buf[15+ii],
                                              byteorder='little', signed=True)
                branch.angle_byte1 = data.buf[14+ii]
                branch.angle_byte2 = data.buf[15+ii]
                intersection.add_branch(branch)
            main_features.add_intersection(intersection)
        elif feature_type == 4:
            # Feature type is 'barcode'
            barcode.x = int.from_bytes(data.buf[8+i_payload], 'little')
            barcode.y = int.from_bytes(data.buf[9+i_payload], 'little')
            barcode.flags = int.from_bytes(data.buf[10+i_payload], 'little')
            barcode.code = int.from_bytes(data.buf[11+i_payload], 'little')
            main_features.add_barcode(barcode)
        else:
            # Unknown feature type
            main_features.error = True

        # Update index in payload
        i_payload += feature_length + 2

    # Return data
    return main_features
