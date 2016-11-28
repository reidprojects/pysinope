# -*- coding: utf-8 -*-
import requests
from sinopeexceptions import InvalidSinopeAuthenticationError, UnknownSinopeError


class Thermostat(object):
    """ Implementation of a thermostat object of the Sinope interface."""
    MODE_MANUAL = "2"
    MODE_AUTOMATIC = "3"

    def __init__(self, json_thermostat=None, headers=None):
        self._headers = headers

        # Initialize the settings.
        self._active = None
        self._name = None
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

        if json_thermostat:
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
        self._gateway_id = unicode(json_thermostat['gatewayId'])
        self._model = unicode(json_thermostat['model'])
        self._type = unicode(json_thermostat['type'])
        self._id = unicode(json_thermostat['id'])

    def load_parameters_from_json(self, json_thermostat):
        self._alarm = unicode(json_thermostat.get('alarm', self._alarm))
        self._error_code = unicode(json_thermostat.get('errorCode', self._error_code))
        self._heat_level = unicode(json_thermostat.get('heatLevel', self._heat_level))
        self._mode = str(json_thermostat.get('mode', self._mode))[:1]    # Mode is represented by the first digit.
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
        params = {"temperature": self._setpoint,
                  "mode": self._mode}

        # Set the mode before the Temp.
        self._set_thermostat_value("mode", params)
        self._set_thermostat_value("setpoint", params)

    def _set_thermostat_value(self, name, params):
        r = requests.put("https://neviweb.com/api/device/{}/{}".format(self._id, name),
                         params,
                         headers=self._headers)

        self.load_parameters_from_json(r.json())


class Gateway(object):
    """Implementation of a Sinope's access point."""
    MODE_AWAY = '2'
    MODE_HOME = '0'

    def __init__(self, json_gateway=None, headers=None):
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
        params = {"mode": self._mode}
        self._set_gateway_value('mode', params)

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

    def _set_gateway_value(self, name, params):
        r = requests.post("https://neviweb.com/api/gateway/{}/{}".format(self._id, name),
                          params,
                          headers=self._headers)
        test = r.text
        print test
        self.load_from_json(r.json())


class PySinope(object):

    def __init__(self):
        """

        @return:
        """
        self._headers = {'Content-type': r'application/x-www-form-urlencoded'}
        self._session_id = None
        self._gateways = list()

    def connect(self, email, password):
        login_parameters = {'email': email,
                            'password': password,
                            'stayConnected': "0"}

        r = requests.post("https://neviweb.com/api/login",
                          data=login_parameters,
                          headers=self._headers)
        response = r.json()
        if 'error' in response:
            if response['error']['code'] == 1002:
                raise InvalidSinopeAuthenticationError(email)
            else:
                raise UnknownSinopeError(response)
        self._session_id = response['session']
        self._headers['Session-Id'] = self._session_id
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        requests.get("https://neviweb.com/api/logout",
                     headers=self._headers)
        return self

    def read_gateway(self):
        r = requests.get("https://neviweb.com/api/gateway",
                     headers=self._headers)

        for json_gateway in r.json():
            self._gateways.append(
                Gateway(json_gateway, self._headers))

        for gateway in self._gateways:
            r = requests.get(
                    "https://neviweb.com/api/device?gatewayId={}".format(gateway.id),
                    headers=self._headers)

            for json_thermostat in r.json():
                gateway.thermostats.append(Thermostat(
                    json_thermostat, self._headers))

            for thermostat in gateway.thermostats:
                self.read_thermostat(thermostat)

    def read_thermostat(self, thermostat):
        r = requests.get(
                "https://neviweb.com/api/device/{}/data?".format(thermostat.id),
                headers=self._headers)

        thermostat.load_parameters_from_json(r.json())

    @property
    def gateways(self):
        return self._gateways

    def get_gateway_by_name(self, name):
        for gateway in self._gateways:
            if gateway.name == name:
                return gateway
        raise Exception('Gateway {} not found.'.format(name))
