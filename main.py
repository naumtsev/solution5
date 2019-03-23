import pygame
import requests
import sys
import os

from requests import get, post, put
import argparse


def search(place):
    geocoder_request = "http://geocode-maps.yandex.ru/1.x/?geocode={}&format=json".format(place)
    response = get(geocoder_request)
    json_response = response.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
    x, y = json_response.split()
    return (str(x) + ',' + str(y), (float(x), float(y)))

def size(response_my):
    resp = response_my['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['boundedBy']['Envelope']
    lx, ly = map(float, resp['lowerCorner'].split())
    rx, ry = map(float, resp['upperCorner'].split())
    w = abs(rx - lx)
    h = abs(ry - ly)
    return (w, h)

def scope(response_my):
    w, h = size(response_my)
    return w / 3 , h / 3


cities = ['Москва', 'Ульяновск', 'Казань']
cords = []
for i in cities:
    geocoder_request = "http://geocode-maps.yandex.ru/1.x/?geocode={}&format=json".format(i)
    response = get(geocoder_request)
    w, h = scope(response.json())
    cords.append((search(i)[1], w, h))

response = None
images = []



cnt = 0
for cord in cords:
    try:

        map_request = "http://static-maps.yandex.ru/1.x/?l=sat&ll={},{}&spn={},{}".format(cord[0][0], cord[0][1], cord[1], cord[2])
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
    except:
        print("Запрос не удалось выполнить. Проверьте наличие сети Интернет.")
        sys.exit(1)

    map_file = "map{}.png".format(cnt)
    with open(map_file, "wb") as file:
        file.write(response.content)

    images.append(pygame.image.load(map_file))
    cnt += 1

pygame.init()
screen = pygame.display.set_mode((600, 450))

ind = 0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


        if event.type == pygame.MOUSEBUTTONDOWN:
            ind += 1
            if ind == len(images):
                ind = 0


    screen.fill(pygame.Color(0, 0, 0))
    screen.blit(images[ind], (0, 0))
    pygame.display.flip()


pygame.quit()

for i in range(len(cords)):
    os.remove("map{}.png".format(i))