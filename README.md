# PySinope

This library allows to interact with Sinope products. This will directly interact with their cloud serrver, it is not possible to use it directly with the gateway.

## Getting Started

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
## Authors

* **Alex Reid** - *Initial work* - [reid418](https://github.com/reid418) - - [Linked In](https://www.linkedin.com/in/alex-reid-43b3b258/)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## ToDo
- Support switches and other products;
- Add unittest
- Improve documentation
