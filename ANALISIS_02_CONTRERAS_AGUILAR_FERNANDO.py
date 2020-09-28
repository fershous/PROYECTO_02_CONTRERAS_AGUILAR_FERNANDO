# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 15:12:03 2020

@author: Fernando Contreras Aguilar
"""

import csv
from tabulate import tabulate
import pandas as pd

db = [] #Variable para base de datos
countries = set() #Set para leer países sin repetir

routes = [] #Arreglo de rutas
visited = [] #Arreglo de rutas visitadas en el ciclo for
visited_transport = [] #Arreglo de transportes visitados en el ciclo for

#Diccionario que contiene el valor total de las importaciones y exportaciones
total = {
    'Exports': 0,
    'Imports': 0
    }

#Diccionario de cada país
countries = {}
#Arreglo de las rutas que existen
transports = []

with open('synergy_logistics_database.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for line in reader:
        db.append(line)
        
for line in db:
   #Ruta actualmente leída
   actual_route = line['origin'] + '-' + line['destination']
   
   #Se suma al total en la posición Exports o Imports, dependiendo de la línea leída
   total[line['direction']] += int(line['total_value'])
   
   #Se crea un objeto ruta
   route = {
    'origin'     : line['origin'],
    'destination': line['destination'],
    'count': {
        'Total'  : 0,
        'Exports': 0,
        'Imports': 0
        },
    'Exports'    : 0,
    'Imports'    : 0,
    'products'   : {}
    }
   
   #Se crea un objeto transporte
   transport = {
        'transport_mode': line['transport_mode'],
        'Exports': 0,
        'Imports': 0
   }
   
   #Se verifica que el medio de transporte no exista aún   
   if line['transport_mode'] not in visited_transport:
       #Si no existe, se agregan a sus respectivos arreglos
       transport[line['direction']] = int(line['total_value']) #Se inicializa el valor de la dirección
       visited_transport.append(line['transport_mode'])
       transports.append(transport.copy())
   else:
       #Si existe, se busca en el arreglo
       for idx, item in enumerate(transports):
           if item['transport_mode'] == line['transport_mode']:
               #Se le suma el valor a su respectiva dirección
               item[line['direction']] += int(line['total_value'])
               break
   
   #Se verifica que que la ruta no exista aún
   if actual_route not in visited:
       #si no existe, se agrega a su respectivo arreglo
       route['count'][line['direction']] = 1 #Se inicializa el conteo de la ruta en dicha dirección
       route['count']['Total'] = 1 #Se inicializa el conteo de todas las direcciones
       route[line['direction']] = int(line['total_value']) #Se inicializa el valor en la respectiva dirección
       route['products'][line['transport_mode']] = [1, int(line['total_value'])] #Se inicializa el conteo y el valor del respectivo medio de transport
       visited.append(actual_route)
       routes.append(route.copy())
       
   else:
       for idx, item in enumerate(routes):
           #Si existe, se busca la ruta y se agregan sus respectivos valores
           if item['origin'] == line['origin'] and item['destination'] == line['destination']:
               item['count'][line['direction']] += 1
               item['count']['Total'] += 1
               item[line['direction']] += int(line['total_value'])
               if line['transport_mode'] in item['products'].keys():
                   item['products'][line['transport_mode']][0] += 1 
                   item['products'][line['transport_mode']][1] += int(line['total_value'])
               else:
                   item['products'][line['transport_mode']] = [1, int(line['total_value'])]
               break
           

#Opción 1. Demanda de las rutas de importación y exportación
def by_routes():
    
    #Se ordena el arreglo dependiendo del conteo de cada dirección
    by_demand_imports = (sorted(routes, key = lambda k: k['count']['Imports'], reverse=True))
    by_demand_exports = (sorted(routes, key = lambda k: k['count']['Exports'], reverse=True))
    
    df2 = pd.DataFrame(by_demand_imports).reindex(columns=['origin','destination','count'])
    df2.style.hide_index()
    print('\nIMPORTS')
    print(tabulate(df2.head(10), headers = 'keys', tablefmt = 'psql', showindex=False))
    print('\nEXPORTS')
    df3 = pd.DataFrame(by_demand_exports).reindex(columns=['origin','destination','count'])
    df3.style.hide_index()
    print(tabulate(df3.head(10), headers = 'keys', tablefmt = 'psql', showindex=False))
    
#Opción 2. Medios de transporte más importantes
def by_transport_mode():
    
    #Se ordenan dos listas, dependiendo de la dirección
    by_conveyance_imports = sorted(transports, key = lambda k: k['Imports'], reverse=True)
    by_conveyance_exports = sorted(transports, key = lambda k: k['Exports'], reverse=True)
    
    df = pd.DataFrame(by_conveyance_exports).reindex(columns=['transport_mode','Exports'])
    df.style.hide_index()
    print(tabulate(df, headers = 'keys', tablefmt = 'psql', showindex=False))
    
    df2 = pd.DataFrame(by_conveyance_imports).reindex(columns=['transport_mode','Imports'])
    df2.style.hide_index()
    print(tabulate(df2, headers = 'keys', tablefmt = 'psql', showindex=False))

def by_values():
    
    #Se obtiene el 80% del valor de cada dirección, apartir del diccionario "total"
    exports_value = total['Exports'] * 0.8
    imports_value = total['Imports'] * 0.8
    
    sum_exports = 0
    sum_imports = 0
    
    exports = []
    imports = []
    intersection = []
    
    for route in routes:
        #Se inicializa cada país y el valor de importación y exportación para cada país
        countries[route['origin']] = {}
        countries[route['origin']]['Exports'] = 0
        countries[route['origin']]['Imports'] = 0
    for route in routes:
        #Se suman los valores de importación y exportación a cada país
        countries[route['origin']]['Exports'] += route['Exports']
        countries[route['origin']]['Imports'] += route['Imports']
    
    #Se ordenan los arreglos dependiendo de la exportacion y la importacion
    sorted_countries = sorted(countries.items(), key = lambda k_v: k_v[1]['Exports'], reverse=True)
    sorted_countries2 = sorted(countries.items(), key = lambda k_v: k_v[1]['Imports'], reverse=True)
     
    for country in sorted_countries:
        if sum_exports <= exports_value:
            #Se agregan países a un arreglo hasta tener el 80% del valor, antes calculado
            sum_exports += country[1]['Exports']
            exports.append(country)
            
    for country in sorted_countries2:
        if sum_imports <= imports_value:
            #Se agregan países a un arreglo hasta tener el 80% del valor, antes calculado
            sum_imports += country[1]['Imports']
            imports.append(country)
       
    #Se realiza la intersección de los arreglos previamente llenados
    intersection = [value for value in exports if value in imports]
            
    for country in intersection:
        print(country[0] + ': ' + str(country[1]))
        
    print(exports)
    print(imports)
        
def by_country():
    country = input('Enter a country: ')
    print(country)
    for route in routes:
        if route['origin'] == country:
            print(route['products'])
            
        

exit = False

while not exit:
    try:
        from IPython import get_ipython
        get_ipython().magic('clear')
        get_ipython().magic('reset -f')
    except:
        pass
    option = input('''----- Select an option ------
1. By imports/exports routes
2. By transport mode
3. By imports/exports values
4. Search by country
5. Exit

>> ''')
    
    if option == '1': 
        by_routes()
        input("Press Enter to continue...")
    elif option == '2':
        by_transport_mode()
        input("Press Enter to continue...")
    elif option == '3':
        by_values()
        input("Press Enter to continue...")
    elif option == '4':
        by_country()
        input("Press Enter to continue...")
    elif option == '5':
        exit = True
    else:
        print('Error, invalid option')
        input("Press Enter to continue...")
    
    
         

