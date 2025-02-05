import math
import cv2
import mediapipe as mp
import time

class detectormanos():
    def __init__(self, mode=False, maxManos=1, model_complexity=1, Confdeteccion=0.7, Confsegui=0.7):
        self.mode = mode
        self.maxManos = maxManos
        self.compl = model_complexity
        self.Confdeteccion = Confdeteccion
        self.Confsegui = Confsegui

        # Inicializar el detector de manos de MediaPipe
        self.mpmanos = mp.solutions.hands
        self.manos = self.mpmanos.Hands(self.mode, self.maxManos, self.compl, self.Confdeteccion, self.Confsegui)
        self.dibujo = mp.solutions.drawing_utils
        self.tip = [4, 8, 12, 16, 20]

    def encontrarmanos(self, frame, dibujar=True):
        imgcolor = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imgcolor.flags.writeable = False  # Mejora el rendimiento
        self.resultados = self.manos.process(imgcolor)

        if self.resultados.multi_hand_landmarks:
            for mano in self.resultados.multi_hand_landmarks:
                if dibujar:
                    self.dibujo.draw_landmarks(frame, mano, self.mpmanos.HAND_CONNECTIONS,
                                               self.dibujo.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                                               self.dibujo.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2))
        return frame

    def encontrarposicion(self, frame, ManoNum=0, dibujar=True, color=(0, 0, 255)):
        xlista, ylista, bbox = [], [], []
        self.lista = []

        if not self.resultados.multi_hand_landmarks:
            return self.lista, bbox, 0  # Devuelve una lista vacía y 0 si no hay manos detectadas

        miMano = self.resultados.multi_hand_landmarks[ManoNum]
        alto, ancho, _ = frame.shape

        for id, lm in enumerate(miMano.landmark):
            cx, cy = int(lm.x * ancho), int(lm.y * alto)
            xlista.append(cx)
            ylista.append(cy)
            self.lista.append([id, cx, cy])

            if dibujar:
                cv2.circle(frame, (cx, cy), 5, color, cv2.FILLED)

        xmin, xmax = min(xlista), max(xlista)
        ymin, ymax = min(ylista), max(ylista)
        bbox = xmin, ymin, xmax, ymax

        if dibujar:
            cv2.rectangle(frame, (xmin - 10, ymin - 10), (xmax + 10, ymax + 10), color, 2)

        return self.lista, bbox, len(self.resultados.multi_hand_landmarks)

    def dedosarriba(self):
        dedos = []
        if len(self.lista) == 0:
            return dedos  # Evita errores si no hay detección

        # Pulgar (comparando posición X en lugar de Y porque está orientado horizontalmente)
        if self.lista[self.tip[0]][1] > self.lista[self.tip[0] - 1][1]:
            dedos.append(1)
        else:
            dedos.append(0)

        # Otros dedos
        for id in range(1, 5):
            if self.lista[self.tip[id]][2] < self.lista[self.tip[id] - 2][2]:
                dedos.append(1)
            else:
                dedos.append(0)

        return dedos

    def distancia(self, p1, p2, frame, dibujar=True, r=8, t=2):
        x1, y1 = self.lista[p1][1:]
        x2, y2 = self.lista[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        longitud = math.hypot(x2 - x1, y2 - y1)

        if dibujar:
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), t)
            cv2.circle(frame, (x1, y1), r, (0, 255, 0), cv2.FILLED)
            cv2.circle(frame, (x2, y2), r, (0, 255, 0), cv2.FILLED)
            cv2.circle(frame, (cx, cy), r, (255, 0, 0), cv2.FILLED)

        return longitud, frame, [x1, y1, x2, y2, cx, cy]


def main():
    ptiempo = 0
    cap = cv2.VideoCapture(0)
    detector = detectormanos()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = detector.encontrarmanos(frame, dibujar=True)
        lista, bbox, _ = detector.encontrarposicion(frame, dibujar=True)

        # Mostrar FPS
        ctiempo = time.time()
        fps = 1 / (ctiempo - ptiempo) if (ctiempo - ptiempo) > 0 else 0
        ptiempo = ctiempo
        cv2.putText(frame, f"FPS: {int(fps)}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow("Manos", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # Presionar 'Esc' para salir
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
