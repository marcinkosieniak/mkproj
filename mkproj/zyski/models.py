from django.db import models
from django.contrib import auth
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator


def validate_positive(value):
    """Reguła walidacji pola DecimalField aby user nie mógł wpisac mniej niż zero"""
    if value < 0:
        raise ValidationError("Wartość musi być większa od 0")


class Projekt(models.Model):
    """Zapisane projekty."""
    name = models.CharField(max_length=90,
                             help_text="Nazwa projektu")
    proj_start_date = models.DateField(auto_now_add=True, verbose_name="Data utworzenia projektu.")
    number = models.CharField(max_length=20,
                            verbose_name="Numer projektu.")
    description = models.CharField(max_length=250, help_text="Opis projektu")

    # publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    # contributors = models.ManyToManyField('Contributor', through="BookContributor")
    
    def __str__(self):
        return self.name
    

class Rooms(models.Model):
    """Pomieszczenia per projekt."""
    r_name = models.CharField(max_length=50,
                              help_text="Nazwa pomieszczenia")
    r_number = models.CharField(max_length=10,
                                help_text="Numer pomieszczenia")
    # r_area = models.DecimalField(max_digits = 5, decimal_places = 2, validators=[validate_positive], help_text = "Powierzchnia w m2")
    r_area = models.PositiveIntegerField(help_text = "Powierzchnia w m2")
    r_people = models.PositiveIntegerField(help_text="Ilość osób w pomieszczeniu")
    r_temp = models.PositiveIntegerField(default = 20, help_text="Temperatura w pomieszczeniu")
    r_air = models.PositiveIntegerField(default= 0, blank=True, help_text="Powietrze infiltracyjne")
    r_light = models.PositiveIntegerField(default = 20, help_text="Emisja od oświetlenia W/m2")
    r_person = models.PositiveIntegerField(default = 80, help_text="Emisja ciepła od ludzi W/os")
    r_devices = models.PositiveIntegerField(default = 0, blank=True, null=True, help_text="Emisja od urządzeń W")
    r_group = models.CharField(default = "", blank=True, max_length=10, help_text="Grupa pomieszczenia")
    r_comment = models.CharField(default = "", blank=True, max_length=80, help_text="Komentarz do pomieszczenia")
    projekt = models.ForeignKey(Projekt, on_delete=models.CASCADE,
                                help_text="Projekt, w którym jest pomieszczenie")
    walls = models.ManyToManyField('Walls', through="WallsRooms")

    def __str__(self):
        return self.r_name

class Walls(models.Model):
    """Ściany per pomieszczenie"""
    
    class WallsKl(models.TextChoices):
        KLASA_1 = "1"
        KLASA_2 = "2"
        KLASA_3_domyślna = "3"
        KLASA_4 = "4"
        KLASA_5 = "5"
        KLASA_6 = "6"

    projekt = models.ForeignKey(Projekt, on_delete=models.CASCADE,
                                help_text="Projekt, w którym jest ściana")
    klasa = models.CharField(verbose_name="Klasa przegrody", default= "KLASA_3",
                                choices=WallsKl.choices, max_length=10, blank=False, null=False)
    wall_U = models.FloatField(validators=[MaxValueValidator(20)],blank=False, help_text = "Współczynnik przenikania ciepła ściany W/m2")
    wall_name = models.CharField(max_length=90, help_text="Nazwa ściany",blank=True ,null=True)
    wall_symbol = models.CharField(default="SZ1",max_length=10, help_text="Symbol ściany")
    wall_description = models.CharField(max_length=90, help_text="Opis ściany",blank=True ,null=True)

    def __str__(self):
        return self.wall_symbol

class WallsRooms(models.Model):
    """Klasa do przypisywania określonych ścian projektu do konkretnego pomieszczenia.
    Idea polega na przypisaniu odpowiedniej powierzchni i kierunku ściany do pomieszczenia."""
    class WallsDir(models.TextChoices):
            N = "N"
            NW = "NW" 
            W = "W"
            SW = "SW"
            S = "S"
            SE = "SE"
            E = "E" 
            NE = "NE"
    wall = models.ForeignKey(Walls, on_delete=models.CASCADE)
    room = models.ForeignKey(Rooms, on_delete=models.CASCADE)

    wall_area = models.FloatField(help_text = "Powierzchnia ściany w m2")
    kierunek = models.CharField(verbose_name="Kierunek świata przegrody",
                                choices=WallsDir.choices, max_length=5, blank=True, null=True)
    

class Rooms_results(models.Model):
    """Wyniki obliczeń na godzinę na pomieszczenie. Pola z zapisem wyników bez ingerencji usera."""

    res_people = models.JSONField(blank=True, null=True) #zyski od ludzi co godzinę
    res_light = models.JSONField(blank=True, null=True) #zyski od oświetlenia co godzinę
    res_walls = models.JSONField(blank=True, null=True) #zyski od ścian co godzinę
    res_windows = models.JSONField(blank=True, null=True) #zyski od okien co godzinę
    res_slabs = models.JSONField(blank=True, null=True) #zyski od stropów co godzinę
    res_air = models.JSONField(blank=True, null=True) #zyski od powietrza co godzinę
    res_devices = models.JSONField(blank=True, null=True) #zyski od urządzeń co godzinę

    pom = models.OneToOneField(Rooms, on_delete=models.CASCADE)