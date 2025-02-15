# Importamos las librerias
import cv2
import random
import SeguimientoManos as sm  
import os
import imutils
import time

# Declaracion de variables
fs = False
fu = False      # Bandera up
fd = False      # Bandera down
fj = False      # Bandera juego
fr = False      # Bandera reset
fgia = False    # Bandera gana IA
fgus = False    # Bandera gana Usuario
femp = False    # Bandera empate
fder = False    # Bandera derecha
fizq = False    # Bandera izquierda
conteo = 0

# Contadores de victorias
victorias_usuario = 0
victorias_ia = 0
rondas_jugadas = 0

mano_levantada = False
tiempo_mano_levantada = 0
TIEMPO_ESPERA = 1  # Segundos que debe mantenerse la mano levantada
ultimo_tiempo = time.time()
contador_iniciado = False
mostrar_mensaje_inicial = True
conteo_finalizado = False  

# Frame skip
FRAME_SKIP = 2  # Procesar 1 de cada 2 frames
frame_count = 0

# Accedemos a la carpeta
path = 'Imagenes'
images = []
clases = []
lista = os.listdir(path)

# Leemos los rostros del DB
for lis in lista:
    # Leemos las imagenes de los rostros
    imgdb = cv2.imread(f'{path}/{lis}')
    # Almacenamos imagen
    images.append(imgdb)
    # Almacenamos nombre
    clases.append(os.path.splitext(lis)[0])

print(clases)

# Lectura de la camara
cap = cv2.VideoCapture(0)

# Declaramos el detector
detector = sm.detectormanos(Confdeteccion=0.7)

def detect_gesture(lista1, is_left):
    """
    Detecta el gesto (piedra, papel, tijera) basado en la posición de los dedos
    """
    if len(lista1) == 0:
        return "No detectado"
        
    # Extraemos valores de interés
    # Punta DI
    x2, _ = lista1[8][1:]
    # Punta DC
    x3, _ = lista1[12][1:]
    # Punta DA
    x4, _ = lista1[16][1:]

    # Falange DI
    x22, _ = lista1[6][1:]
    # Falange DC
    x33, _ = lista1[10][1:]
    # Falange DA
    x44, _ = lista1[14][1:]

    # Verificamos si la mano está en la izquierda
    if is_left:
        # Piedra
        if x2 < x22 and x3 < x33 and x4 < x44:
            return "Piedra"
        # Papel
        elif x2 > x22 and x3 > x33 and x4 > x44:
            return "Papel"
        # Tijera
        elif x2 > x22 and x3 > x33 and x4 < x44:
            return "Tijera"
    else:
        # Piedra
        if x2 > x22 and x3 > x33 and x4 > x44:
            return "Piedra"
        # Papel
        elif x2 < x22 and x3 < x33 and x4 < x44:
            return "Papel"
        # Tijera
        elif x2 < x22 and x3 < x33 and x4 > x44:
            return "Tijera"
    
    return "Gesto no reconocido"

def detectar_mano_levantada(lista1):
    if len(lista1) == 0:
        return False
    
    # Obtenemos la posición de la muñeca y la punta del dedo medio
    muneca_y = lista1[0][2]  # Coordenada y de la muñeca
    dedo_medio_y = lista1[12][2]  # Coordenada y de la punta del dedo medio
    
    # Si el dedo medio está significativamente más arriba que la muñeca
    return (muneca_y - dedo_medio_y) > 100


while True:
    # Lectura de la videocaptura
    ret, frame = cap.read()

    # Frame skip: Solo procesar 1 de cada FRAME_SKIP frames
    frame_count += 1
    if frame_count % FRAME_SKIP != 0:
        continue

    # Leemos teclado
    t = cv2.waitKey(1)

    # Extraemos la mitad del frame
    al, an, c = frame.shape
    cx = int(an/2)
    cy = int(al/2)

    # Espejo
    frame = cv2.flip(frame, 1)

    # Encontramos las manos
    frame = detector.encontrarmanos(frame, dibujar=True)
    # Posiciones mano 1
    lista1, bbox1, jug = detector.encontrarposicion(frame, ManoNum=0, dibujar=True, color=[0, 255, 0])

    tiempo_actual = time.time()
    
    cv2.putText(frame, f"Usuario: {victorias_usuario}  IA: {victorias_ia}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # 1 Jugador
    if jug == 1:
        # Dividimos pantalla
        cv2.line(frame, (cx, 0), (cx, 480), (0, 255, 0), 2)

        # Mostramos jugadores
        cv2.rectangle(frame, (245, 25), (380, 60), (0, 0, 0), -1)
        cv2.putText(frame, '1 JUGADOR', (250, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.71, (0, 255, 0), 2)
        
        if len(lista1) != 0:
            x1, y1 = lista1[9][1:]
            is_left = x1 < cx
            
            # Detectar el gesto y mostrarlo
            gesto = detect_gesture(lista1, is_left)
            cv2.rectangle(frame, (x1-50, y1-50), (x1+100, y1-20), (0, 0, 0), -1)
            cv2.putText(frame, f"Gesto: {gesto}", (x1-45, y1-30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Detectar mano levantada e iniciar contador solo si no ha finalizado
            if detectar_mano_levantada(lista1) and not conteo_finalizado:
                # Obtener dimensiones del frame
                alto_frame, ancho_frame, _ = frame.shape
                
                # Texto y fuente
                texto = "¡Listo!"
                fuente = cv2.FONT_HERSHEY_SIMPLEX
                escala_fuente = 2
                grosor_fuente = 3
                color_texto = (0, 0, 0)  # Negro
                
                # Obtener tamaño del texto
                (ancho_texto, alto_texto), _ = cv2.getTextSize(texto, fuente, escala_fuente, grosor_fuente)
                
                # Calcular coordenadas para centrar el texto
                x_texto = (ancho_frame - ancho_texto) // 2
                y_texto = (alto_frame + alto_texto) // 2 -150  # Centrado verticalmente
                
                # Mostrar el texto en el centro del frame
                cv2.putText(frame, texto, (x_texto, y_texto), fuente, escala_fuente, color_texto, grosor_fuente)

                if not mano_levantada:
                    mano_levantada = True
                    tiempo_mano_levantada = tiempo_actual
                    
                if not contador_iniciado and (tiempo_actual - tiempo_mano_levantada) >= TIEMPO_ESPERA:
                    contador_iniciado = True
                    ultimo_tiempo = tiempo_actual
                    imagen_actual = 0
            else:
                mano_levantada = False
            
            # Sistema de conteo con imágenes
            if contador_iniciado:
                # Determinar qué imagen mostrar basado en el tiempo transcurrido
                tiempo_transcurrido = tiempo_actual - ultimo_tiempo
                
                if tiempo_transcurrido < 1:  # Primer segundo
                    imagen_actual = 0
                elif tiempo_transcurrido < 2:  # Segundo segundo
                    imagen_actual = 1
                elif tiempo_transcurrido < 3:  # Tercer segundo
                    imagen_actual = 2
                    
                    alto_frame, ancho_frame, _ = frame.shape

                    # Texto y fuente
                    texto = "¡Agite su mano!"
                    fuente = cv2.FONT_HERSHEY_SIMPLEX
                    escala_fuente = 2
                    grosor_fuente = 3
                    color_texto = (0, 0, 0) 

                    # Obtener tamaño del texto
                    (ancho_texto, alto_texto), _ = cv2.getTextSize(texto, fuente, escala_fuente, grosor_fuente)

                    # Calcular coordenadas para centrar el texto
                    x_texto = (ancho_frame - ancho_texto) // 2
                    y_texto = (alto_frame + alto_texto) // 2 + 150 # Un poco más abajo que "¡Listo!"

                    # Mostrar el texto centrado
                    cv2.putText(frame, texto, (x_texto, y_texto), 
                                cv2.FONT_HERSHEY_SIMPLEX, escala_fuente, 
                                color_texto, grosor_fuente)
                else:  # Después de 3 segundos
                    conteo = 3  # Iniciar el juego
                    contador_iniciado = False
                    conteo_finalizado = True  # Bloquear el reinicio hasta que se resetee manualmente
                
                # Mostrar la imagen actual del contador
                if imagen_actual <= 2:
                    img = images[imagen_actual]
                    img = imutils.resize(img, width=240, height=240)
                    ali, ani, c = img.shape
                    
                    if x1 < cx:
                        frame[130: 130 + ali, 350: 350 + ani] = img
                        fizq = True
                        fder = False
                    else:
                        frame[130: 130 + ali, 30: 30 + ani] = img
                        fder = True
                        fizq = False
            
            # Jugamos
            elif conteo == 3:
                # Si no hemos jugado jugamos
                if fj == False and fr == False:
                    # Elegimos piedra papel o tijera
                    juego = random.randint(3,5)
                    fj = True

                # Izquierda
                if fizq == True and fder == False:
                    # Mostramos
                    img = images[juego]
                    # Redimensionamos
                    img = imutils.resize(img, width=240, height=240)
                    ali, ani, c = img.shape
                    # Mostramos imagen
                    frame[130: 130 + ali, 350: 350 + ani] = img
                    print(juego)

                    # Si ya jugamos
                    if fj == True and fr == False:
                        # Extraemos valores de interes
                        # Punta DI
                        x2, y2 = lista1[8][1:]
                        # Punta DC
                        x3, y3 = lista1[12][1:]
                        # Punta DA
                        x4, y4 = lista1[16][1:]

                        # Falange DI
                        x22, y22 = lista1[6][1:]
                        # Falange DC
                        x33, y33 = lista1[10][1:]
                        # Falange DA
                        x44, y44 = lista1[14][1:]

                        # Condiciones de posicion
                        # Piedra
                        if x2 < x22 and x3 < x33 and x4 < x44:
                            # IA PAPEL
                            if juego == 3:
                                # GANA IA
                                print('GANA LA IA')
                                # Bandera Ganador
                                fgia = True
                                fgus = False
                                femp = False
                                fr = True
                                victorias_ia += 1
                            # IA PIEDRA
                            elif juego == 4:
                                # EMPATE
                                print('EMPATE')
                                # Bandera Ganador
                                fgia = False
                                fgus = False
                                femp = True
                                fr = True

                            elif juego == 5:
                                # GANA USUARIO
                                print('GANA EL HUMANO')
                                # Bandera Ganador
                                fgia = False
                                fgus = True
                                femp = False
                                fr = True
                                victorias_usuario += 1
                        # Papel
                        elif x2 > x22 and x3 > x33 and x4 > x44:
                            # IA PAPEL
                            if juego == 3:
                                # EMPATE
                                print('EMPATE')
                                fgia = False
                                fgus = False
                                fr = True
                                femp = True
                            # IA PIEDRA
                            elif juego == 4:
                                # GANA USUARIO
                                print('GANA EL HUMANO')
                                # Bandera Ganador
                                fgia = False
                                fgus = True
                                femp = False
                                fr = True
                                victorias_usuario += 1
                            elif juego == 5:
                                # GANA LA IA
                                print('GANA LA IA')
                                # Bandera Ganador
                                fgia = True
                                fgus = False
                                femp = False
                                fr = True
                                victorias_ia += 1

                        # Tijera
                        elif x2 > x22 and x3 > x33 and x4 < x44:
                            # IA PAPEL
                            if juego == 3:
                                # GANA EL USUARIO
                                print('GANA EL HUMANO')
                                # Bandera Ganador
                                fgia = False
                                fgus = True
                                femp = False
                                fr = True
                                victorias_usuario += 1
                            # IA PIEDRA
                            elif juego == 4:
                                # GANA LA IA
                                print('GANA LA IA')
                                # Bandera Ganador
                                fgia = True
                                fgus = False
                                femp = False
                                fr = True
                                victorias_ia += 1
                            elif juego == 5:
                                # EMPATE
                                print('EMPATE')
                                fgia = False
                                fgus = False
                                femp = True
                                fr = True
                    # Mostramos ganador
                    # IA
                    if fgia == True:
                        gan = images[6]
                        alig, anig, c = gan.shape
                        frame[70: 70 + alig, 180: 180 + anig] = gan
                        cv2.putText(frame, "", (200, 400), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    # USUARIO
                    elif fgus == True:
                        gan = images[7]
                        alig, anig, c = gan.shape
                        frame[70: 70 + alig, 180: 180 + anig] = gan
                        cv2.putText(frame, "", (200, 400), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    # EMPATE
                    elif femp == True:
                        gan = images[8]
                        alig, anig, c = gan.shape
                        frame[70: 70 + alig, 180: 180 + anig] = gan
                        cv2.putText(frame, "¡EMPATE!", (200, 400), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

                    # Incrementar el número de rondas jugadas
                    rondas_jugadas += 1

                    # Verificar si alguien ha ganado 3 veces
                    if victorias_usuario == 3 or victorias_ia == 3:
                        if victorias_usuario == 3:
                            cv2.putText(frame, "¡GANASTE EL JUEGO!", (100, 400), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        elif victorias_ia == 3:
                            cv2.putText(frame, "¡IA GANA EL JUEGO!", (100, 400), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        
                        # Mostrar mensaje de reinicio después de la partida completa
                        cv2.putText(frame, "Presiona 'r' para reiniciar", (120, 450), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                    # Reiniciar juego solo si alguien llegó a 3 victorias y se presiona 'r'
                    if (t == 82 or t == 114) and (victorias_usuario == 3 or victorias_ia == 3):  # 'R' o 'r'
                        fs = False
                        fu = False
                        fd = False
                        fj = False
                        fr = False
                        fgia = False
                        fgus = False
                        femp = False
                        fder = False
                        fizq = False
                        conteo = 0
                        victorias_usuario = 0
                        victorias_ia = 0
                        rondas_jugadas = 0  # Reiniciar rondas solo cuando se termine el juego
                        reiniciar_conteo()
                        
                # Reset al presionar 'r'
                    if t == 82 or t == 114:  # 82 es 'R' y 114 es 'r'
                        fs = False
                        fu = False
                        fd = False
                        fj = False
                        fr = False
                        fgia = False
                        fgus = False
                        femp = False
                        fder = False
                        fizq = False
                        conteo = 0
                        reiniciar_conteo()
                # Derecha
                if fizq == False and fder == True:
                    # Mostramos
                    img = images[juego]
                    # Redimensionamos
                    img = imutils.resize(img, width=240, height=240)
                    ali, ani, c = img.shape
                    # Mostramos imagen
                    frame[130: 130 + ali, 30: 30 + ani] = img
                    print(juego)

                    # Si ya jugamos
                    if fj == True and fr == False:
                        # Extraemos valores de interes
                        # Punta DI
                        x2, y2 = lista1[8][1:]
                        # Punta DC
                        x3, y3 = lista1[12][1:]
                        # Punta DA
                        x4, y4 = lista1[16][1:]

                        # Falange DI
                        x22, y22 = lista1[6][1:]
                        # Falange DC
                        x33, y33 = lista1[10][1:]
                        # Falange DA
                        x44, y44 = lista1[14][1:]

                        # Condiciones de posicion
                        # Piedra
                        if x2 > x22 and x3 > x33 and x4 > x44:
                            # IA PAPEL
                            if juego == 3:
                                # GANA IA
                                print('GANA LA IA')
                                # Bandera Ganador
                                fgia = True
                                fgus = False
                                femp = False
                                fr = True
                                victorias_ia += 1
                            # IA PIEDRA
                            elif juego == 4:
                                # EMPATE
                                print('EMPATE')
                                # Bandera Ganador
                                fgia = False
                                fgus = False
                                femp = True
                                fr = True

                            elif juego == 5:
                                # GANA USUARIO
                                print('GANA EL HUMANO')
                                # Bandera Ganador
                                fgia = False
                                fgus = True
                                femp = False
                                fr = True
                                victorias_usuario += 1

                        # Papel
                        elif x2 < x22 and x3 < x33 and x4 < x44:
                            # IA PAPEL
                            if juego == 3:
                                # EMPATE
                                print('EMPATE')
                                fgia = False
                                fgus = False
                                fr = True
                                femp = True
                            # IA PIEDRA
                            elif juego == 4:
                                # GANA USUARIO
                                print('GANA EL HUMANO')
                                # Bandera Ganador
                                fgia = False
                                fgus = True
                                femp = False
                                fr = True
                                victorias_usuario += 1
                            elif juego == 5:
                                # GANA LA IA
                                print('GANA LA IA')
                                # Bandera Ganador
                                fgia = True
                                fgus = False
                                femp = False
                                fr = True
                                victorias_ia += 1

                        # Tijera
                        elif x2 < x22 and x3 < x33 and x4 > x44:
                            # IA PAPEL
                            if juego == 3:
                                # GANA EL USUARIO
                                print('GANA EL HUMANO')
                                # Bandera Ganador
                                fgia = False
                                fgus = True
                                femp = False
                                fr = True
                                victorias_usuario += 1
                            # IA PIEDRA
                            elif juego == 4:
                                # GANA LA IA
                                print('GANA LA IA')
                                # Bandera Ganador
                                fgia = True
                                fgus = False
                                femp = False
                                fr = True
                                victorias_ia += 1
                            elif juego == 5:
                                # EMPATE
                                print('EMPATE')
                                fgia = False
                                fgus = False
                                femp = True
                                fr = True

    if jug == 1:
                     # Mostramos ganador
                    # IA
                    if fgia == True:
                        gan = images[6]
                        alig, anig, c = gan.shape
                        frame[70: 70 + alig, 180: 180 + anig] = gan
                        cv2.putText(frame, "", (200, 400), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    # USUARIO
                    elif fgus == True:
                        gan = images[7]
                        alig, anig, c = gan.shape
                        frame[70: 70 + alig, 180: 180 + anig] = gan
                        cv2.putText(frame, "", (200, 400), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    # EMPATE
                    elif femp == True:
                        gan = images[8]
                        alig, anig, c = gan.shape
                        frame[70: 70 + alig, 180: 180 + anig] = gan
                        cv2.putText(frame, "¡EMPATE!", (200, 400), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                        
                    # Incrementar el número de rondas jugadas
                    rondas_jugadas += 1

                    # Verificar si alguien ha ganado 3 veces
                    if victorias_usuario == 3 or victorias_ia == 3:
                        if victorias_usuario == 3:
                            cv2.putText(frame, "¡GANASTE EL JUEGO!", (100, 400), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        elif victorias_ia == 3:
                            cv2.putText(frame, "¡IA GANA EL JUEGO!", (100, 400), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        
                        # Mostrar mensaje de reinicio después de la partida completa
                        cv2.putText(frame, "Presiona 'r' para reiniciar", (120, 450), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                    # Reiniciar juego solo si alguien llegó a 3 victorias y se presiona 'r'
                    if (t == 82 or t == 114) and (victorias_usuario == 3 or victorias_ia == 3):  # 'R' o 'r'
                        fs = False
                        fu = False
                        fd = False
                        fj = False
                        fr = False
                        fgia = False
                        fgus = False
                        femp = False
                        fder = False
                        fizq = False
                        conteo = 0
                        victorias_usuario = 0
                        victorias_ia = 0
                        rondas_jugadas = 0  # Reiniciar rondas solo cuando se termine el juego
                        reiniciar_conteo()
                        
                # Reset al presionar 'r'
                    if t == 82 or t == 114:  # 82 es 'R' y 114 es 'r'
                        fs = False
                        fu = False
                        fd = False
                        fj = False
                        fr = False
                        fgia = False
                        fgus = False
                        femp = False
                        fder = False
                        fizq = False
                        conteo = 0
                        reiniciar_conteo()
                    def reiniciar_conteo():
                        global contador_iniciado, conteo_finalizado, mano_levantada
                        contador_iniciado = False
                        conteo_finalizado = False
                        mano_levantada = False
                        

                    if mostrar_mensaje_inicial:
                        mensaje = "Mantenga la mano levantada para iniciar"
                        cv2.putText(frame, mensaje, (int(cx/2), cy), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        mostrar_mensaje_inicial = False          
                  
    # 0 Jugadores (corregida la indentación)
    elif jug == 0:
        # Mostramos jugadores
        cv2.rectangle(frame, (225, 25), (388, 60), (0, 0, 0), -1)
        cv2.putText(frame, '0 JUGADORES', (230, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.71, (0, 0, 255), 2)

        # Mensaje inicio en el centro de la pantalla
        texto = 'LEVANTE SU MANO PARA INICIAR'
        tamaño_texto = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        texto_x = (frame.shape[1] - tamaño_texto[0]) // 2
        texto_y = (frame.shape[0] + tamaño_texto[1]) // 2

        cv2.rectangle(frame, (texto_x - 10, texto_y - tamaño_texto[1] - 10), (texto_x + tamaño_texto[0] + 10, texto_y + 10), (0, 0, 0), -1)
        cv2.putText(frame, texto, (texto_x, texto_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Mostramos frames
    cv2.imshow("JUEGO CON AI", frame)
    if t == 27:
        break
cap.release()
cv2.destroyAllWindows()