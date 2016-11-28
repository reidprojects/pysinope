# PySinope

```python
from pysinope import PySinope, Thermostat

if "__main__" == __name__:

    py_sinope = PySinope()

    with py_sinope.connect("email", "pass") as sinope_interface:
        sinope_interface.read_gateway()

        main_gateway = sinope_interface.get_gateway_by_name('Home')
        therm = main_gateway.get_thermostat_by_name('Bedroom')

        print therm.temperature
        print therm.setpoint

        therm.mode = Thermostat.MODE_MANUAL  # Set the Thermostat mode.
        therm.setpoint = "20.00"

        print unicode(therm)

```