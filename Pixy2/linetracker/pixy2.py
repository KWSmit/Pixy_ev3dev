""" Classes and constants for pixy2 linetracking."""
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
        self.smbus = SMBus(3)
        # Settings for linetraacking (see wiki Pixycam.com)
        self._mode = 0
        self._default_turn = 0
        self._next_turn = 0

    def lamp_on(self):
        """Turn lamp on."""
        request_block = [174, 193, 22, 2, 1, 0]
        self.smbus.write_i2c_block_data(self.i2c_address, 0, request_block)

    def lamp_off(self):
        """Turn lamp off."""
        request_block = [174, 193, 22, 2, 0, 0]
        self.smbus.write_i2c_block_data(self.i2c_address, 0, request_block)

    def set_mode(self, mode):
        """Set mode for Pixy2."""
        request_block = [174, 193, 54, 1, mode]
        self.smbus.write_i2c_block_data(self.i2c_address, 0, request_block)
        self._mode = mode

    def getdata(self):
        """Get linetracking data form pixy2."""

        mainfeatures = MainFeatures()
        vector = Vector()
        intersection = Intersection()
        branch = Branch()
        barcode = Barcode()
        payload_read = 0

        # Request
        request_block = [174, 193, 48, 2, 0, 7]
        self.smbus.write_i2c_block_data(self.i2c_address, 0, request_block)

        # Read header info
        response = self.smbus.read_i2c_block_data(self.i2c_address, 0, 6)

        # Parse header info
        if response[2] == 49:
            mainfeatures.type_of_packet = response[2]
        else:
            mainfeatures.error = True
            return mainfeatures
        mainfeatures.length_of_payload = response[3]

        # Read payload data
        while payload_read < mainfeatures.length_of_payload:
            # Read feature type and feature_length:
            response = self.smbus.read_i2c_block_data(self.i2c_address, 0, 2)
            feature_type = response[0]
            feature_length = response[1]
            # Read feature data
            if feature_type == 1:
                # Feature type is 'vector'
                response = self.smbus.read_i2c_block_data(self.i2c_address,
                                                          0, feature_length)
                vector.x0 = response[0]
                vector.y0 = response[1]
                vector.x1 = response[2]
                vector.y1 = response[3]
                vector.index = response[4]
                vector.flags = response[5]
                mainfeatures.add_vector(vector)
            elif feature_type == 2:
                # feature type is 'intersection'
                response = self.smbus.read_i2c_block_data(self.i2c_address,
                                                          0, feature_length)
                intersection.x = response[0]
                intersection.y = response[1]
                intersection.nr_of_branches = response[2]
                for i in range(0, intersection.nr_of_branches):
                    i4 = i*4
                    branch.index = response[i4+0]
                    branch.angle = response[14+1]
                    branch.angle_byte1 = response[i4+2]
                    branch.angle_byte2 = response[i4+3]
                    intersection.add_branch(branch)
                mainfeatures.add_intersection(intersection)
            elif feature_type == 4:
                # Feature type is 'barcode'
                response = self.smbus.read_i2c_block_data(self.i2c_address,
                                                          0, feature_length)
                barcode.x = response[0]
                barcode.y = response[1]
                barcode.flags = response[2]
                barcode.code = response[3]
                mainfeatures.add_barcode(barcode)
            else:
                # Unknown feature type
                mainfeatures.error = True

            payload_read += feature_length + 2

        # Return data
        return mainfeatures

    def set_vector(self, index):
        """Set vector for Pixy2 to follow."""
        request_block = [174, 193, 56, 1, index]
        self.smbus.write_i2c_block_data(self.i2c_address, 0, request_block)
        response = self.smbus.read_i2c_block_data(self.i2c_address, 0, 10)
        return response

    def set_next_turn(self, angle):
        """Set direction robot has to take at intersection."""
        if angle >= 0:
            request_block = [174, 193, 58, 2, angle, 0]
        else:
            request_block = [174, 193, 58, 2, angle, -1]
        self.smbus.write_i2c_block_data(self.i2c_address, 0, request_block)
        response = self.smbus.read_i2c_block_data(self.i2c_address, 0, 10)
        self._next_turn = angle
        return response

    def set_default_turn(self, angle):
        """"Set direction robot has to take at intersection."""
        if angle >= 0:
            request_block = [174, 193, 60, 2, angle, 0]
        else:
            request_block = [174, 193, 60, 2, angle, -1]
        self.smbus.write_i2c_block_data(self.i2c_address, 0, request_block)
        response = self.smbus.read_i2c_block_data(self.i2c_address, 0, 10)
        self._next_turn = angle
        return response


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
