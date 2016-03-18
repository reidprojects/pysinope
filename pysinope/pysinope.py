# -*- coding: utf-8 -*-
import httplib
import urllib
import json


class Thermostat(object):
    MODE_MANUAL = "2"
    MODE_AUTOMATIC = "3"

    def __init__(self, json_thermostat=None, connection=None, headers=None):
        self._connection = connection
        self._headers = headers

        # Initialize the settings.
        self._active = None
        self._name = None
        self._rf_address = None
        self._rf_parent = None
        self._mac = None
        self._gateway_id = None
        self._model = None
        self._type = None
        self._id = None

        # Initialize the parameters.
        self._alarm = None
        self._error_code = None
        self._heat_level = None
        self._mode = None
        self._rssi = None
        self._setpoint = None
        self._temperature = None
        self._name = None

        if None is not json_thermostat:
            self.load_settings_from_json(json_thermostat)

    @property
    def temperature(self):
        return self._temperature

    @property
    def setpoint(self):
        return self._setpoint

    @setpoint.setter
    def setpoint(self, value):
        self._setpoint = value
        self.update_thermostat()

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value
        self.update_thermostat()

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    def load_settings_from_json(self, json_thermostat):
        self._active = unicode(json_thermostat['active'])
        self._name = unicode(json_thermostat['name'])
        self._rf_address = unicode(json_thermostat['rfAddress'])
        self._rf_parent = unicode(json_thermostat['rfParent'])
        self._mac = unicode(json_thermostat['mac'])
        self._gateway_id = unicode(json_thermostat['gatewayId'])
        self._model = unicode(json_thermostat['model'])
        self._type = unicode(json_thermostat['type'])
        self._id = unicode(json_thermostat['id'])

    def load_parameters_from_json(self, json_thermostat):
        self._alarm = unicode(json_thermostat.get('alarm', self._alarm))
        self._error_code = unicode(json_thermostat.get('errorCode', self._error_code))
        self._heat_level = unicode(json_thermostat.get('heatLevel', self._heat_level))
        self._mode = unicode(json_thermostat.get('mode', self._mode) if 1 == len(str(json_thermostat.get('mode', self._mode))) else str(json_thermostat.get('mode', self._mode))[1])
        # self._rssi = unicode(json_thermostat['rssi'])
        self._setpoint = unicode(json_thermostat.get('setpoint', self._setpoint))
        self._temperature = unicode(json_thermostat.get('temperature', self._temperature))

    def __unicode__(self):
        return unicode("Name : {}\n"
                       "Temperature : {}\n"
                       "Setpoint : {}\n"
                       "Heat level : {}%\n"
                       "Mode : {}").format(self._name,
                                           self._temperature,
                                           self._setpoint,
                                           self._heat_level,
                                           self._mode)

    def update_thermostat(self):
        encoded_parameters = urllib.urlencode({"temperature":
                                               self._setpoint,
                                               "mode": self._mode})
        # Set the mode before the Temp.
        self._set_thermostat_value("mode", encoded_parameters)
        self._set_thermostat_value("setpoint", encoded_parameters)

    def _set_thermostat_value(self, name, value):
        self._connection.request("PUT",
                                 "/api/device/{}/{}".format(self._id, name),
                                 value,
                                 headers=self._headers)
        self.load_parameters_from_json(json.loads(
            self._connection.getresponse().read()))


class Gateway(object):
    MODE_AWAY = '2'
    MODE_HOME = '0'

    def __init__(self, json_gateway=None, connection=None, headers=None):
        self._connection = connection
        self._headers = headers

        self._id = None
        self._mac = None
        self._name = None
        self._is_active = None
        self._city = None
        self._postal_code = None
        self._mode = None
        self._thermostats = list()

        if None is not json_gateway:
            self.load_from_json(json_gateway)

    def load_from_json(self, json_gateway):
        self._id = unicode(json_gateway.get('id', self._id))
        self._mac = unicode(json_gateway.get('mac', self._mac))
        self._name = unicode(json_gateway.get('name', self._name))
        self._is_active = bool(json_gateway.get('active', self._is_active))
        self._city = unicode(json_gateway.get('city', self._city))
        self._mode = unicode(json_gateway.get('mode', self._mode))
        self._postal_code = unicode(json_gateway.get('postalCode',
                                                     self._postal_code))

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value
        encoded_parameters = urllib.urlencode({"mode": self._mode})
        self._set_gateway_value('mode', encoded_parameters)

    @property
    def thermostats(self):
        return self._thermostats

    @thermostats.setter
    def thermostats(self, value):
        self._thermostats = value

    def __unicode__(self):
        thermostats = u', \n\n'.join(map(unicode,
                                         self._thermostats)).replace('\n',
                                                                     '\n    ')
        return unicode("ID : {}\n"
                       "MAC : {}\n"
                       "Name : {}\n"
                       "Active : {}\n"
                       "City : {}\n"
                       "Postal Code : {}\n"
                       "Thermostats : \n    {}").format(self._id,
                                                        self._mac,
                                                        self._name,
                                                        self._is_active,
                                                        self._city,
                                                        self._postal_code,
                                                        thermostats)

    def get_thermostat_by_name(self, name):
        for thermostat in self._thermostats:
            if thermostat.name == name:
                return thermostat
        raise Exception('Thermostat {} not found.'.format(name))

    def _set_gateway_value(self, name, value):
        self._connection.request("POST",
                                 "/api/gateway/{}/{}".format(self._id, name),
                                 value,
                                 headers=self._headers)
        test = self._connection.getresponse().read()
        print test
        self.load_from_json(json.loads(test))


class PySinope(object):

    def __init__(self):
        """

        @return:
        """
        self._headers = {'Content-type': r'application/x-www-form-urlencoded'}
        self._connection = None
        self._session_id = None
        self._gateways = list()

    def connect(self, email, password):
        login_parameters = {'email': email,
                            'password': password,
                            'stayConnected': "0"}

        self._connection = httplib.HTTPSConnection('neviweb.com')

        encoded_parameters = urllib.urlencode(login_parameters)
        self._connection.request("POST",
                                 "/api/login",
                                 body=encoded_parameters,
                                 headers=self._headers)

        response = self._connection.getresponse().read()
        self._session_id = json.loads(response)['session']
        self._headers['Session-Id'] = self._session_id
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        self._connection.request("GET",
                                 "/api/logout",
                                 headers=self._headers)

        self._connection.getresponse().read()
        return self

    def read_gateway(self):
        assert self._connection is not None

        self._connection.request("GET",
                                 "/api/gateway",
                                 headers=self._headers)

        for json_gateway in json.loads(self._connection.getresponse().read()):
            self._gateways.append(
                Gateway(json_gateway, self._connection, self._headers))

        for gateway in self._gateways:
            self._connection.request("GET",
                                     "/api/device?gatewayId=%s" % gateway.id,
                                     headers=self._headers)

            for json_thermostat in json.loads(
                    self._connection.getresponse().read()):
                gateway.thermostats.append(Thermostat(
                    json_thermostat, self._connection, self._headers))

            for thermostat in gateway.thermostats:
                self.read_thermostat(thermostat)

    def read_thermostat(self, thermostat):
        self._connection.request("GET",
                                 "/api/device/%s/data?" % thermostat.id,
                                 headers=self._headers)

        thermostat.load_parameters_from_json(
            json.loads(self._connection.getresponse().read()))

    @property
    def gateways(self):
        return self._gateways

    def get_gateway_by_name(self, name):
        for gateway in self._gateways:
            if gateway.name == name:
                return gateway
        raise Exception('Gateway {} not found.'.format(name))


if "__main__" == __name__:
    py_sinope = PySinope()

    with py_sinope.connect('email', 'password') as sinope_interface:

        sinope_interface.read_gateway()
        main_gateway = sinope_interface.get_gateway_by_name('Maison')
        main_gateway.mode = Gateway.MODE_AWAY      # Set the gateway mode.
        salon_therm = main_gateway.get_thermostat_by_name('Salon / Cuisine')
        print unicode(salon_therm)
        salon_therm.mode = Thermostat.MODE_MANUAL  # Set the Thermostat mode.
        salon_therm.setpoint = "20.00"
        print unicode(salon_therm)
