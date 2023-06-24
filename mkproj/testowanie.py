#%%
class testowa():
    bok_a = 5
    bok_b = 10
    obiekty = 0

    def __init__(self):
       self.numer = 15

    def __str__(self):
        f"{self.numer}"


    def sumowanie(self):
        c = self.bok_a + self.bok_b
        testowa.obiekty += 1
        return f"Długośc boku wynosi {c}, ilość obiektów wynosi: {testowa.obiekty}"

    
suma = testowa().sumowanie()
suma1 = testowa()
suma1.sumowanie()

testowa_lista = []
zbior = set()
if len(testowa_lista) < 1:
    print("Pusta lista")
if not testowa_lista:
    print("Pusta lista")
if testowa_lista:
    zbior.add(testowa_lista[0])
    print("Pusta lista")
    print("zbior")

print("*"*20)

numer = 20
numer_fl = -20.155

print(type(numer))
print(type(numer_fl))

slownik1 = {"a":"7"}
slownik2 = {"a":"9"}
lista_slownikow = []
lista_slownikow.append(slownik1)
lista_slownikow.append(slownik2)
print(lista_slownikow)
#%%
from zyski.pakiety import tabele
import math
class Wyniki():
    """Klasa do obliczenia zysków ciepła w pomieszczeniach"""
    def __init__(self):
        self.godziny_people = {str(key) : value for (key, value) in enumerate([hour for hour in range(8,21)],start=8)}
        self.godziny_lights = self.godziny_people.copy()
        self.godziny_air = {}
        self.godziny_sciany = {}
        self.godziny_okna = {}


    def calc_gains_people(self,people,watts):
        """Metoda do obliczenia zysków od ludzi. Wynik to słownik."""
        for key, value in self.godziny_people.items():
            self.godziny_people[key] = people * watts
        return self.godziny_people
    
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
            self.godziny_air 
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
        """Metoda pomocnicza do obliczeń współczynników dla okien. Wynikiem są słowniki dla współczynników Ic, hc, Rc, Rs"""

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

        # Rc = {str(key) : szer_b*(hc[str(key)]+(wys_h-hc[str(key)])*Ic[str(key)])/(wys_h*szer_b) for key in [x for x in range(8,21)]}
        Rc = {key : (((szer_b*(hc[str(key)])+((wys_h-hc[str(key)])*Ic[str(key)])))/(wys_h*szer_b)) for key, value in hc.items()}
        Rs = {key: 1-Rc[key] for key, value in Rc.items()}
        factors = [Rc, Rs]
        
        return factors





okno1 = Wyniki()
okno2 = Wyniki()

# print(okno1._window_factors(kierunek="SW",szer_b = 3, wys_h = 4, a=0.1, Brad = tabele.sciany["Sciana_SW_Brad"], Hrad = tabele.sciany["Sciana_SW_Hrad"])[0])
# print(okno1._window_factors(kierunek="SW",szer_b = 3, wys_h = 4, a=0.1, Brad = tabele.sciany["Sciana_SW_Brad"], Hrad = tabele.sciany["Sciana_SW_Hrad"])[1])

print(okno1.calc_gains_windows(kierunek="N",szer_b = 3, wys_h = 4, area=36, U=1.5))
print(okno2.calc_gains_windows(kierunek="NW",szer_b = 3, wys_h = 4, area=36, U=1.5))



# %%
import math
print (math.tan(45))
a=5/(-1)
print(a)

zm = "1,1"
b = zm.split(",")
print(b[0])

one_window = {str(key) : 0 for key in [x for x in range(8,21)]}
print(one_window)

# %%
lista1=[1,2,3,4,5]
lista2=[1,2,3,4,5]
print([(x+lista2[idx]) for idx, x in enumerate(lista1) ])
print({ key : 0 for key in [x for x in range(8,21)]})
print({ str(key) : (150 if key > 15  else 0 ) for key in [x for x in range(8,21)] })
print({ key : value for key, value in enumerate([0 for x in range(8,21)],start=8)})


# %%
from zyski.pakiety import tabele
kierunek, klasa = "W", "1"
a,u = 0,0

start_dict = tabele.Klasa_1_N if kierunek == "N" else None
if start_dict is None: start_dict = tabele.Klasa_1_W if (kierunek == "W" and klasa == "1") else None
if start_dict is None: start_dict = tabele.Klasa_1_W if (kierunek == "SW" and klasa == "1") else None
print({key : value*a*u for key, value in start_dict.items()})
# %%
area = 36
b=0.75

Icmax = 604
Irmax = 192
s = 0.58
te = 26
U=1.5
ti=26
Rc = 0.06
Rs = 0.94

test = round((area*((Rs*b*Icmax*s)+(Rc*b*Irmax*s)))+(area*((te-ti)*U)))
# test = round((36*((0.91*0.75*604*0.22)+(0.09*0.75*192*0.22)))+(36*((24-26)*1.5)))
print(test)


# %%
