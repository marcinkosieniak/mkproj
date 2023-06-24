from zyski.pakiety import tabele
import math

class Wyniki():
    """Klasa do obliczenia zysków ciepła w pomieszczeniach"""
    def __init__(self):
        self.godziny_people = {str(key) : value for (key, value) in enumerate([hour for hour in range(8,21)],start=8)}
        self.godziny_lights = self.godziny_people.copy()
        self.godziny_devices = self.godziny_people.copy()
        self.godziny_air = {}
        self.godziny_sciany = {}
        self.godziny_okna = {}

    def calc_gains_people(self,people,watts):
        """Metoda do obliczenia zysków od ludzi. Wynik to słownik."""
        for key, value in self.godziny_people.items():
            self.godziny_people[key] = people * watts
        return self.godziny_people
    
    def calc_gains_devices(self,watts=0):
        """Metoda do ibliczenia zysków od urządzeń. Wynik to słownik."""
        for key, value in self.godziny_devices.items():
            self.godziny_devices[key] = watts
        return self.godziny_devices
    
    def calc_gains_lights(self,area,watts,a=0,b=0.3):
        """Metoda do obliczenia zysków od oświetlenia. Wynik to słownik."""
        for key, value in self.godziny_lights.items():
            if key == "19":
                ko = 0.35
                self.godziny_lights[key] = round(area * watts * ((ko * (1-b-a)) + b))
            elif key == "20":
                ko = 0.60
                self.godziny_lights[key] = round(area * watts * ((ko * (1-b-a))+b))
            else:
                ko = 0.0
                self.godziny_lights[key] = (area * watts * ((ko * (1-b-a))+b)) * 0
        return self.godziny_lights
    
    def calc_gains_air(self,ti=24,air=0):
        """Metoda do obliczenia zysków od infiltracji. 
        ti - temp. wewn. w pomieszczeniu (zmienna),
        air - strumień powietrza infiltrującego w m3/h,
        te - temp. zewnętrzna stała od +18*C do +32 """
        #słownik temperatur zewnętrznych
        te = {
            "8":24, "9":24, "10":26, "11":26,"12":32,
            "13":32, "14":32, "15":30, "16":28, "17":26,
            "18":24, "19":20, "20":18
        }
        for key, value in te.items():
            self.godziny_air[key] = round(air / 3600 * 1.2 * (value-ti) * 1000)
        return self.godziny_air

    def calc_gains_walls(self, ti=26, tesr=24.5, kierunek="N", klasa ="1",
                        area = 0, U = 0):
        """
        Metoda do obliczenia zysków ciepła od ścian. Polega na pobraniu danej ściany,
        sprawdzeniu jej kierunku świata oraz klasy przegrody i obliczeniu zysków ciepła 
        dla jednej przegrody co godzinę. Wynikiem jest słownik z jedną ścianą a następnie 
        inkrementacja do głównego ślownika wszystkich ścian. Metoda będzie dodawać wartości 
        do głównego słownika za każdym razem od jej wywołania. 
        Główny słownik zostaje przypisany do instancji class Wyniki. Słownik: self.godziny_sciany = {}
        """
        one_wall = tabele.klasy[f"Klasa_{klasa}_{kierunek}"]
        one_wall_result = { key : round(area*U*(value + tesr - 24.5 - ti + 22)) for key, value in one_wall.items()}
        self.godziny_sciany.update({key: self.godziny_sciany.get(key, 0) + value for key, value in one_wall_result.items()})
        
        return  self.godziny_sciany
    
    def calc_gains_windows(self, ti=26, tesr=24.5, kierunek="N", szer_b = 3, wys_h = 4,
                        area = 0, U = 0, C = 0.75, b1 = 1, b2 = 1, b3 = 1):
        """
        Metoda do obliczenia zysków ciepła od okien. Polega na pobraniu danego okna,
        sprawdzeniu kierunku świata oraz pozostałych parametrów i obliczeniu zysków ciepła 
        dla każdego okna co godzinę. Wynikiem jest słownik z jednym oknem ze wszystkimi parametrami
        a następnie inkrementowanie wartości do głównego słownika wszystkich okien. 
        Metoda będzie dodawać wartości do głównego słownika za każdym razem od jej wywołania. 
        Główny słownik zostaje przypisany do instancji class Wyniki. Słownik: self.godziny_okna = {}
        Oznaczenia:
        ti - temperatura w pom., tesr - temp. średnia na zewn., kierunek - kierunek ściany w któryj jest okno,
        szer_b - szerokość szyby, wys_h - wysokość szyby, area - pow. okna, U - wsp. U dla okna, 
        C - udział powierzchni oszklonej (zakładane 75%), b1 - osłona zewnętrzna, b2 - rodzaj oszklenia,
        b3 - osłona wewnętrzna, b - iloczyn C * b1*b2*b3 (średni współczynnik przepuszczalności promieni słon.)
        """
        te = {"8":24, "9":24, "10":26, "11":26,"12":32, "13":32, "14":32, "15":30, "16":28, "17":26,"18":24, "19":20, "20":18}
        a = 0.1
        b = C * b1 * b2 * b3
        Brad = tabele.sciany[f"Sciana_{kierunek}_Brad"]
        Hrad = tabele.sciany[f"Sciana_{kierunek}_Hrad"]
        Icmax = tabele.sciany[f"Sciana_{kierunek}_Icmax"]
        Irmax = tabele.sciany[f"Sciana_{kierunek}_Irmax"]
        s = tabele.sciany[f"Sciana_{kierunek}_s"]
        Rc_Rs = self._window_factors(kierunek, szer_b, wys_h, Brad, Hrad, a )
        Rc = Rc_Rs[0]
        Rs = Rc_Rs[1]
        one_window = { str(key) : 0 for key in [x for x in range(8,21)]}

        one_window_result = { key : round((area*((Rs[key]*b*Icmax[key]*s[key])+(Rc[key]*b*Irmax[key]*s[key])))+(area*((te[key]-ti)*U))) for key, value in one_window.items()}
        self.godziny_okna.update({key: self.godziny_okna.get(key, 0) + value for key, value in one_window_result.items()})

        return  self.godziny_okna

    def _window_factors(self,kierunek,szer_b, wys_h, Brad, Hrad, a):
        """Metoda pomocnicza do obliczeń współczynników dla okien. Wynikiem są słowniki dla współczynników Rc, Rs"""

        if kierunek == "N":
            Ic = { str(key) : szer_b for key in [x for x in range(8,21)]}
            hc = { str(key) : wys_h for key in [x for x in range(8,21)]}
        elif kierunek == "NW":
            Ic = { str(key) : (a * math.tan(Brad[str(key)]) if key > 15  else szer_b ) for key in [x for x in range(8,21)]}
            hc = { str(key) : (a * math.tan(Hrad[str(key)])/math.cos(Brad[str(key)]) if key > 15  else wys_h ) for key in [x for x in range(8,21)]}
        elif kierunek == "W":
            Ic = { str(key) : (a * math.tan(Brad[str(key)]) if key > 12  else szer_b ) for key in [x for x in range(8,21)]}
            hc = { str(key) : (a * math.tan(Hrad[str(key)])/math.cos(Brad[str(key)]) if key > 12  else wys_h ) for key in [x for x in range(8,21)]}
        elif kierunek == "SW":
            Ic = { str(key) : (a * math.tan(Brad[str(key)]) if key > 9  else szer_b ) for key in [x for x in range(8,21)]}
            hc = { str(key) : (a * math.tan(Hrad[str(key)])/math.cos(Brad[str(key)]) if key > 9  else wys_h ) for key in [x for x in range(8,21)]}
        elif kierunek == "S":
            Ic = { str(key) : (a * math.tan(Brad[str(key)]) if key < 18  else szer_b ) for key in [x for x in range(8,21)]}
            hc = { str(key) : (a * math.tan(Hrad[str(key)])/math.cos(Brad[str(key)]) if key < 18  else wys_h ) for key in [x for x in range(8,21)]}
        elif kierunek == "SE":
            Ic = { str(key) : (a * math.tan(Brad[str(key)]) if key < 15  else szer_b ) for key in [x for x in range(8,21)]}
            hc = { str(key) : (a * math.tan(Hrad[str(key)])/math.cos(Brad[str(key)]) if key < 15  else wys_h ) for key in [x for x in range(8,21)]}
        elif kierunek == "E":
            Ic = { str(key) : (a * math.tan(Brad[str(key)]) if key < 12  else szer_b ) for key in [x for x in range(8,21)]}
            hc = { str(key) : (a * math.tan(Hrad[str(key)])/math.cos(Brad[str(key)]) if key < 12  else wys_h ) for key in [x for x in range(8,21)]}
        else:
            Ic = { str(key) : szer_b for key in [x for x in range(8,21)]}
            hc = { str(key) : wys_h for key in [x for x in range(8,21)]}

        Rc = {key : (((szer_b*(hc[str(key)])+((wys_h-hc[str(key)])*Ic[str(key)])))/(wys_h*szer_b)) for key, value in hc.items()}
        Rs = {key: 1-Rc[key] for key, value in Rc.items()}
        factors = [Rc, Rs]
        
        return factors




if __name__ == "__main__":
    test = Wyniki()
    print(test.godziny_people)
    new_list=[{'8': 1100, '9': 2500, '10': 2300},{'8': 1200, '9': 2700, '10': 2400}]
    for i,j in enumerate(new_list):
        print(sorted(new_list[i].items(), key=lambda x: x[1])[-1]) #sortowanie po wartościach słowników
    print([(key,value) for key, value in new_list[0].items() if value == max(new_list[0].values())]) #MAX z 0 elementu listy słowników

