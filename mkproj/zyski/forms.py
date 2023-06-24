from django import forms
from .models import Projekt, Rooms, Walls, WallsRooms, validate_positive
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator

#zmienna dla nadpisania klasy bootstrapowej class="form-control form-control-sm
class_bstrp= "form-control form-control-sm"

class ProjektForm(forms.ModelForm):
    class Meta:
        model = Projekt
        exclude = ["proj_start_date"]
        # fields = ("name","number", "description","proj_start_date")
        
        widgets = {"name":forms.TextInput
                (attrs={"placeholder":"Nazwa projektu", 
                        "class":class_bstrp}),
                "number":forms.TextInput
                (attrs={"placeholder":"Numer projektu", 
                        "class":class_bstrp}),
                "description":forms.TextInput
                (attrs={"placeholder":"Opis projektu", 
                        "class":class_bstrp}),
                        }
        labels = {
            "name": _("Nazwa projektu"),
            "number": _("Numer projektu"),
            "description": _("Opis projektu"),
        }

        help_texts = {
            "name": _(""),
            "description": _(""),
        } 

class RoomsForm(forms.ModelForm):
    class Meta:
        model = Rooms
        fields = ("r_number", "r_name", "r_area", "r_people", 
                  "r_temp","r_air","r_light", "r_person","r_devices",
                  "r_group","r_comment")

        widgets = {"r_name":forms.TextInput
           (attrs={"placeholder":"Nazwa pomieszczenia", "class":class_bstrp}),
                   "r_number":forms.TextInput
           (attrs={"placeholder":"Numer pomieszczenia w formacie 001", "class":class_bstrp}),
           "r_area":forms.NumberInput
           (attrs={"placeholder":"Powierzchnia pomieszczenia w m2", "class":class_bstrp,"step":0.5}),
           "r_people":forms.NumberInput
           (attrs={"placeholder":"Ilość osób", "class":class_bstrp}),
           "r_temp":forms.NumberInput
           (attrs={"placeholder":"Temperatura", "class":class_bstrp}),
           "r_air":forms.NumberInput
           (attrs={"placeholder":"Powietrze w m3/h", "class":class_bstrp}),
           "r_light":forms.NumberInput
           (attrs={"placeholder":"Emisja ośw. w W/m2", "class":class_bstrp}),
           "r_person":forms.NumberInput
           (attrs={"placeholder":"Wskaźnik W/os.", "class":class_bstrp}),
           "r_devices":forms.NumberInput
           (attrs={"placeholder":"Emisja od urz. w W", 
                   "class":class_bstrp}),
           "r_group":forms.TextInput
           (attrs={"placeholder":"Grupa", "class":class_bstrp}),
           "r_comment":forms.TextInput
           (attrs={"placeholder":"Komentarz", "class":class_bstrp}),
                   }

        labels = {
            "r_number": _("Numer pomieszczenia"),
            "r_name": _("Nazwa pomieszczenia"),
            "r_area": _("Powierzchnia pomieszczenia"),
            "r_people": _("Ilość osób w pomieszczeniu"),
            "r_temp": _("Temperatura wewnętrzna w pomieszczeniu"),
            "r_air": _("Strumień powietrza infiltracyjnego m3/h"),
            "r_light": _("Emisja ciepła od oświetlenia W/m2"),
            "r_person": _("Emisja ciepła od ludzi W/os"),
            "r_devices": _("Emisja ciepła od urzązeń W"),
            "r_group": _("Grupa pomieszczenia"),
            "r_comment": _("Komentarz do pomieszczenia"),
        }
        help_texts = {
            "r_number": _(""),
            "r_name": _(""),
            "r_area": _(""),
            "r_people": _(""),
            "r_temp": _(""),
            "r_air": _(""),
            "r_light": _(""),
            "r_person": _(""),
            "r_devices": _(""),
            "r_person": _(""),
            "r_group": _(""),
            "r_comment": _(""),
        }    
        
class WallsForm2(forms.ModelForm):
    class Meta:
        model = Walls
        fields = ("wall_symbol","wall_name","wall_description", "klasa", "wall_U")

class WallsForm(forms.Form):
    wall_symbol = forms.CharField(max_length=10, label="Symbol ściany", 
                             widget=forms.TextInput(attrs={"placeholder":"Wpisz symbol ściany, np. SZ1","class":class_bstrp}))
    wall_name = forms.CharField(max_length=90, label="Nazwa ściany",required=False, 
                             widget=forms.Textarea(attrs={"rows": 2,"placeholder":"Wpisz nazwę ściany","class":class_bstrp}))
    wall_description = forms.CharField(max_length=90, label="Opis ściany",required=False, 
                             widget=forms.Textarea(attrs={"rows": 2,"placeholder":"Wpisz dodatkowy opis ściany","class":class_bstrp}))
    klasa = forms.ChoiceField(choices=Walls.WallsKl.choices, initial = "3",
                              label="Klasa przegrody",widget=forms.Select(attrs={"class":class_bstrp}) )
    wall_u = forms.FloatField(label = "Współczynnik przenika ciepła ściany", validators=[MaxValueValidator(20)],
                              min_value=0.01, step_size=0.01,
                              widget=forms.NumberInput(attrs={"placeholder":"Wpisz U ściany [W/m2*K]", "class":class_bstrp}))
    

class WallsRoomsForm(forms.Form):
    # class Meta:
    #     model = WallsRooms
    #     fields = ("kierunek","wall_area")

    kierunek = forms.ChoiceField(choices=WallsRooms.WallsDir.choices, initial = "N",
                            label="Kierunek świata ściany",widget=forms.Select(attrs={"class":class_bstrp}) )
    wall_area = forms.FloatField(label = "Powierzchnia ściany", validators=[MaxValueValidator(100000)],
                        min_value=1, step_size=0.1,
                        widget=forms.NumberInput(attrs={"placeholder":"Wpisz powierzchnię ściany [m2]", "class":class_bstrp}))
    # wall_symbol = forms.CharField(max_length=10, label="Symbol ściany", 
    #                     widget=forms.TextInput(attrs={"placeholder":"Wpisz symbol ściany, np. SZ1","class":class_bstrp}))
