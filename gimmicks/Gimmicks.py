from lxml import etree
from io import BytesIO
import struct

from serialization.io import (read_dtype, read_int32,
                              write_int32, write_tuple16)


def gimmick_factory(gimmick_bytes):
    # first, get the kind:
    gimmick_bytes.seek(0x4)
    kind = read_int32(gimmick_bytes)
    gimmick_bytes.seek(0)
    if kind == 2:
        return Gimmick_Door(gimmick_bytes)
    if kind == 3:
        return Gimmick_Laser(gimmick_bytes)
    if kind == 4:
        return Gimmick_Crown(gimmick_bytes)
    elif kind == 22:
        return Gimmick_Battery(gimmick_bytes)
    elif kind == 23:
        return Gimmick_WarpCloud(gimmick_bytes)
    elif kind == 27:
        return Gimmick_Gravity(gimmick_bytes)
    else:
        return Gimmick(gimmick_bytes)


class Gimmick():
    def __init__(self, fobj):
        if not self.param_fmts:
            self.param_fmts = ('<i', '<i', '<i', '<i', '<i', '<i')

        if not self.param_names:
            self.param_names = ('param0', 'param1', 'param2', 'param3',
                                'param4', 'param5')

        if fobj is None:
            return
        self.wuid = read_int32(fobj)
        self.kind = read_int32(fobj)
        self.x = read_int32(fobj)
        self.y = read_int32(fobj)
        self.group = read_int32(fobj)
        self.appearance = read_int32(fobj)

        self.load_parameters(fobj)

    @staticmethod
    def new(wuid, kind, x, y, group, appearance=0):
        if kind == 3:
            new_class = Gimmick_Laser(None)
            new_class.direction = 8  # up by default
        elif kind == 4:
            new_class = Gimmick_Crown(None)
        elif kind == 22:
            new_class = Gimmick_Battery(None)
        elif kind == 27:
            new_class = Gimmick_Gravity(None)
        new_class.wuid = wuid
        new_class.kind = kind
        new_class.x = x
        new_class.y = y
        new_class.group = group
        new_class.appearance = appearance
        return new_class

    def load_parameters(self, fobj):
        self.param0 = read_dtype(fobj, self.param_fmts[0])
        self.param1 = read_dtype(fobj, self.param_fmts[1])
        self.param2 = read_dtype(fobj, self.param_fmts[2])
        self.param3 = read_dtype(fobj, self.param_fmts[3])
        self.param4 = read_dtype(fobj, self.param_fmts[4])
        self.param5 = read_dtype(fobj, self.param_fmts[5])

    def export(self, i):
        gimmick_data = etree.Element('Gimmick_{0}'.format(str(i)))
        wuid = etree.Element('wuid')
        wuid.text = str(self.wuid)
        gimmick_data.append(wuid)
        kind = etree.Element('kind')
        kind.text = str(self.kind)
        gimmick_data.append(kind)
        x = etree.Element('x')
        x.text = str(self.x)
        gimmick_data.append(x)
        y = etree.Element('y')
        y.text = str(self.y)
        gimmick_data.append(y)
        group = etree.Element('group')
        group.text = str(self.group)
        gimmick_data.append(group)
        appearance = etree.Element('appearance')
        appearance.text = str(self.appearance)
        gimmick_data.append(appearance)
        param0 = etree.Element('param0')
        param0.text = str(self.param0)
        gimmick_data.append(param0)
        param1 = etree.Element('param1')
        param1.text = str(self.param1)
        gimmick_data.append(param1)
        param2 = etree.Element('param2')
        param2.text = str(self.param2)
        gimmick_data.append(param2)
        param3 = etree.Element('param3')
        param3.text = str(self.param3)
        gimmick_data.append(param3)
        param4 = etree.Element('param4')
        param4.text = str(self.param4)
        gimmick_data.append(param4)
        param5 = etree.Element('param5')
        param5.text = str(self.param5)
        gimmick_data.append(param5)

    def image(self, data):
        return data.get(self.kind)

    def __bytes__(self):
        """ Serialize the Gimmick data. """
        data = BytesIO(b'')
        write_int32(data, self.wuid)
        write_int32(data, self.kind)
        write_int32(data, self.x)
        write_int32(data, self.y)
        write_int32(data, self.group)
        write_int32(data, self.appearance)

        for i, fmt in enumerate(self.param_fmts):
            if fmt == '<i':
                try:
                    write_int32(data, getattr(self, 'param{0}'.format(str(i))))
                except struct.error:
                    print(getattr(self, 'param{0}'.format(str(i))))
                    raise
            elif fmt == '<hh':
                write_tuple16(data, getattr(self, 'param{0}'.format(str(i))))

        return data.getvalue()

    def __getattr__(self, name):
        if name.startswith('param'):
            return 0
        else:
            raise AttributeError


class Gimmick_SpawnPoint(Gimmick):
    """ Gimmick # 0 """
    def __init__(self, fobj):
        super(Gimmick_SpawnPoint, self).__init__(fobj)


class Gimmick_Door(Gimmick):
    """ Gimmick # 2 """
    def __init__(self, fobj):
        super(Gimmick_Door, self).__init__(fobj)
        self.y += 32

    def __bytes__(self):
        self.y -= 32
        _bytes = super(Gimmick_Door, self).__bytes__()
        self.y += 32
        return _bytes


class Gimmick_Laser(Gimmick):
    """ Gimmick # 3 """
    def __init__(self, fobj):
        self.param_names = ('direction', 'param1', 'param2', 'param3',
                            'param4', 'param5')

        super(Gimmick_Laser, self).__init__(fobj)

    def image(self, data):
        return data[self.kind][self.direction]

    @property
    def direction(self):
        return self.param0

    @direction.setter
    def direction(self, value):
        self.param0 = value


class Gimmick_Crown(Gimmick):
    """ Gimmick # 4 """
    def __init__(self, fobj):
        super(Gimmick_Crown, self).__init__(fobj)


class Gimmick_Battery(Gimmick):
    """ Gimmick # 22 """
    def __init__(self, fobj):
        self.param_names = ('polarity', 'is_toggle', 'target_id', 'param3',
                            'param4', 'param5')
        super(Gimmick_Battery, self).__init__(fobj)

    @property
    def polarity(self):
        return self.param0

    @polarity.setter
    def polarity(self, value):
        self.param0 = value

    @property
    def is_toggle(self):
        return self.param1

    @is_toggle.setter
    def is_toggle(self, value):
        self.param1 = value

    @property
    def target_id(self):
        return self.param2

    @target_id.setter
    def target_id(self, value):
        self.param2 = value

    def image(self, data):
        return data[self.kind][self.polarity]


class Gimmick_WarpCloud(Gimmick):
    """ Gimmick # 23 """
    def __init__(self, fobj):
        self.param_names = ('direction', 'position', 'extent', 'out_group',
                            'param4', 'param5')
        self.param_fmts = ('<i', '<hh', '<hh', '<i', '<i', '<i')
        super(Gimmick_WarpCloud, self).__init__(fobj)

    def image(self, data):
        return {'rectangle': (self.position[0], self.position[1],
                              self.position[0] + self.extent[0],
                              self.position[1] - self.extent[1])}

    @property
    def direction(self):
        return self.param0

    @direction.setter
    def direction(self, value):
        self.param0 = value

    @property
    def position(self):
        return (self.param1[1], self.param1[0])

    @position.setter
    def position(self, value):
        self.param1 = (value[1], value[0])

    @property
    def extent(self):
        return (self.param2[1], self.param2[0])

    @extent.setter
    def extent(self, value):
        self.param2 = (value[1], value[0])

    @property
    def out_group(self):
        return self.param3

    @out_group.setter
    def out_group(self, value):
        self.param3 = value


class Gimmick_Gravity(Gimmick):
    """ Gimmick # 27 """
    def __init__(self, fobj):
        self.param_names = ('position', 'extent', 'is_active', 'direction',
                            'speed', 'param5')
        self.param_fmts = ('<hh', '<hh', '<i', '<i', '<i', '<i')
        super(Gimmick_Gravity, self).__init__(fobj)

    def image(self, data):
        # final value is subtracted because of the inverted y coordinate
        return {'rectangle': (self.position[0], self.position[1],
                              self.position[0] + self.extent[0],
                              self.position[1] - self.extent[1])}

    @property
    def position(self):
        return (self.param0[1], self.param0[0])

    @position.setter
    def position(self, value):
        self.param0 = (value[1], value[0])

    @property
    def extent(self):
        return (self.param1[1], self.param1[0])

    @extent.setter
    def extent(self, value):
        self.param1 = (value[1], value[0])

    @property
    def is_active(self):
        return self.param2

    @is_active.setter
    def is_active(self, value):
        self.param2 = value

    @property
    def direction(self):
        return self.param3

    @direction.setter
    def direction(self, value):
        self.param3 = value

    @property
    def speed(self):
        return self.param4

    @speed.setter
    def speed(self, value):
        self.param4 = value