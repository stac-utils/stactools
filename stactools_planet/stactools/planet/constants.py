import pystac

PLANET_EXTENSION_PREFIX = 'pl'

PLANET_PROVIDER = pystac.Provider(
    name='Planet',
    description=(
        'Contact Planet at '
        '[planet.com/contact-sales](https://www.planet.com/contact-sales/)'),
    url='http://planet.com',
    roles=['producer', 'processor'])
