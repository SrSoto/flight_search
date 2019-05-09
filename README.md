# Flight Search: A Headless Python Flight Searcher

## Prerrequisitos de funcionamiento

Para el funcionamiento de `flight_search.py` es necesario tener los siguientes
paquetes y software instalados:

* Python3: `flight_search.py` está escrito en Python3

* Selenium:

```
pip3 install -U selenium
```

* Driver de Selenium: Se utiliza `geckodriver`i (>= 0.17.0), incluido en
	`flight_search/selenium/drivers`.  Si aparece el error

```
	selenium.common.exceptions.WebDriverException: Message: ‘geckodriver’
	executable needs to be in PATH`
```

Desde Bash ejecutar

```
	$ export PATH='path/to/geckodriver'
```

* Tor: Es necesario disponer de Tor y **escribir el path hacia tor en el
	fichero de configuración `flight_search/selenium/config/flight_search.conf`**.
	Para más información, abrir dicho fichero de configuración. Para instalar Tor:

```
sudo apt-get update
sudo apt-get install tor
```

* Driver de Tor: Es necesario tener instalado `tbselenium`

```
	pip install tbselenium
```

* Xvfb:

```sudo apt-get install xvfb```

## Contenido del proyecto

Es bastante imprescindible leer la memoria para entrar en mejor contexto con el
resto de ficheros de este trabajo. Sin embargo, este es un árbol-resumen de los
contenidos:

* `conexión usual/`: Archivos referentes al capítulo 3 Incluyen objetos XML de
	rastreo de paquetes, y `txt`'s sobre hosts y cookies. 
* `flight_search/`: Archivos referentes a los capítulos 4, 5 y 7
    * `requests/`: Archivos referentes al capítulo 4.  Incluye el código de
      "intentos" de arañas web. Consultar el capítulo 4 para entender por qué
      no es la versión final.
    * `selenium/`: Archivos referentes a los capítulos 5 y 7 Incluye
      `flight_search.py`, la implementación principal de este trabajo.
        * `config/`: Carpeta con el archivo de configuración de flight_search
      Importante configurarlo, o quizás no funcione `flight_search` adecuadamente
        * `cookie_data/`: Carpeta con pickles de cookies utilizadas. Necesaria para
      navegar simulando uso de cookies.
        * `drivers/`: Ejecutables de los dos drivers utilizados. Imprescindible para
      funcionar las búsquedas con y sin cookies.
        * `log/`: Directorio con logs de ejecución de tandas de búsqueda. Se entregan
      vacíos.
        * `searches/`: Directorio con los .txt de fijación de búsquedas y los .sh de
      ejecución de tantas de búsquedas.
        * `src/`:  Directorio con otros `.py` implementados para flight_search.
      Contiene `Driver.py`, `Iberia.py` y `Ryanair.py`.
        * `flight_data/`: Contiene `flight_data_db.sqlite` (base de datos principal),
      txt's auxiliares y gráficas.
            * `plots/`: Contiene todas las gráficas de los vuelos fijados (en `.png` y
          `.eps`), así como el bash script y `.py` que las genera.

## Licencia

© Manuel Soto Jiménez, 2019.

