from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone

from .forms import ProjektForm, RoomsForm, WallsForm, WallsRoomsForm
from .models import Projekt, Rooms, Rooms_results, Walls, WallsRooms
from .calc_zyski import * 



def index(request):
    return render(request, "base.html")

def projekty(request):
    proj_lista = Projekt.objects.all()
    # proj_lista = Projekt.objects.all().order_by("-number") #sortuj malejąco
    return render(request, "projekty.html", {'proj_lista': proj_lista})

def proj_detail(request,pk):
    proj = Projekt.objects.get(pk=pk)
    if request.method == "POST":
        new_name = request.POST['new_name']
        proj.name = new_name
        proj.save()
    return render(request, "proj-detail.html",{'proj': proj} )



def proj_search(request):
    search_text = request.GET.get('searching','')
    filtered_projects = set()

    projects = Projekt.objects.filter(name__icontains = search_text)
    if projects:
        for project in projects:
            filtered_projects.add(project)
    projects = Projekt.objects.filter(number__icontains = search_text)
    if projects:
        for project in projects:
            filtered_projects.add(project)
    projects = Projekt.objects.filter(description__icontains = search_text)
    if projects:
        for project in projects:
            filtered_projects.add(project)
    
    filtered_projects_sorted = sorted(list(filtered_projects), key=lambda x: x.number) #posortuj listę wg numeru projektu

    return render(request, "proj-search.html", {"search_text":search_text, 
                                                "projects":filtered_projects_sorted})

def proj_edit(request, pk=None):
    if pk is not None:
        projekt = get_object_or_404(Projekt, pk=pk)
    else:
        projekt = None

    if request.method == "POST":
        form = ProjektForm(request.POST, instance=projekt)
        if form.is_valid():
            updated_projekt = form.save()
            if projekt is None:
                messages.success(request, f"Obiekt {updated_projekt} został utworzony")
            else:
                messages.success(request, f"Obiekt {updated_projekt} został uaktualniony")
            return redirect('proj-detail', updated_projekt.pk)
    else:
        form = ProjektForm(instance=projekt)
    
    return render(request, "form-example.html", {"method":request.method, "form":form})

def proj_zyski(request,pk):
    proj = Projekt.objects.get(pk=pk)
    rooms = sorted(Rooms.objects.filter(projekt=pk), key=lambda x: x.r_number)
    
    room_results_list = []

    for nr, room in enumerate(rooms):
        zyski_ciepla = f"zyski_{nr}"
        zyski_ciepla = Wyniki()
        zyski_od_ludzi_wyn = zyski_ciepla.calc_gains_people(room.r_people,room.r_person)
        zyski_od_osw_wyn = zyski_ciepla.calc_gains_lights(room.r_area,room.r_light)
        zyski_od_urz_wyn = zyski_ciepla.calc_gains_devices(room.r_devices)
        zyski_od_air_wyn = zyski_ciepla.calc_gains_air(room.r_temp,room.r_air)
        #obliczenia zysków na ścianach - polega na wywołaniu metody tyle razy ile jest ścian
        scianywpom = room.wallsrooms_set.all() #filtracja metodą _set.all() polega na listowaniu pomieszczeń, które występują w rooms.
        #instrukcja warunkowa jest konieczna aby metoda nie przyjmowała wartości ostatniej iteracji pętli
        if scianywpom:
            for sciana in scianywpom:
                wsp_U = sciana.wall.wall_U
                klasa = sciana.wall.klasa
                pow = sciana.wall_area
                kierunek = sciana.kierunek
                zyski_od_scian = zyski_ciepla.calc_gains_walls(kierunek=kierunek, klasa=klasa, area=pow, U=wsp_U)
        else:
            zyski_od_scian = zyski_ciepla.calc_gains_walls()

        edited_room = Rooms_results.objects.filter(pom=room.pk).first() # filtruję po kluczu obcym przy metodzie filter będzie to lista 
                                                                        # dlatego zamiast edited_room[0] daję metodę .first()
        if edited_room:
            edited_room.res_people = zyski_od_ludzi_wyn
            edited_room.res_light = zyski_od_osw_wyn
            edited_room.res_devices = zyski_od_urz_wyn
            edited_room.res_air = zyski_od_air_wyn
            edited_room.res_walls = zyski_od_scian
            room_results_list.append(edited_room)
            edited_room.save()
        else:
            room_to_save = Rooms_results(pom=room,res_people=zyski_od_ludzi_wyn,
                                         res_light=zyski_od_osw_wyn,res_devices=zyski_od_urz_wyn,
                                         res_air=zyski_od_air_wyn, res_walls=zyski_od_scian)
            room_results_list.append(room_to_save)
            room_to_save.save()

    return render(request, "proj-zyski.html",{'proj': proj, 'rooms':rooms, 'room_results_list':room_results_list} )

def proj_rooms(request,pk):
    proj = Projekt.objects.get(pk=pk)
    rooms = Rooms.objects.filter(projekt=pk).order_by('r_number')

    search_rooms = request.GET.get('searching_numbers','')
    if search_rooms:
        rooms = Rooms.objects.filter(r_number__icontains = search_rooms).filter(projekt=pk).order_by('r_number')
    else:
        search_rooms = request.GET.get('searching_names','')
        if search_rooms:
            rooms = Rooms.objects.filter(r_name__icontains = search_rooms).filter(projekt=pk).order_by('r_number')


    checked_row = request.POST.get("edycja")
    edited_room = None

    if request.method == "POST":
        if rooms and checked_row:
            edited_room = get_object_or_404(Rooms, pk = int(checked_row))
            form = RoomsForm(request.POST, instance = edited_room)
        else:
            form = RoomsForm(request.POST, instance = None)

        if form.is_valid():
            updated_room = form.save(False)
            updated_room.projekt = proj
            updated_room.save()

            return redirect("proj_rooms", proj.pk)
    else:
        form = RoomsForm()
    
    return render(request, "proj-rooms.html",{'proj': proj, 'rooms':rooms, 
                                              'form':form, 'edited_room':edited_room, 
                                              'checked_row':checked_row,
                                              'instance':edited_room, "search_rooms":search_rooms})

def proj_rooms_ed(request,pk,rpk):
    proj = get_object_or_404(Projekt, pk = pk)
    room = get_object_or_404(Rooms, pk = rpk)

    form = RoomsForm(instance = room)
    usun_pom = request.POST.get("usun")

    if request.method == "POST":
        form = RoomsForm(request.POST, instance = room)
        if usun_pom:
            room.delete()

        if usun_pom == None and form.is_valid():
            updated_room = form.save(False)
            updated_room.projekt = proj
            updated_room.save()

        return redirect("proj_rooms", proj.pk)
    
    return render(request, "proj-rooms-edit.html",{'proj': proj, 'room':room, 
                                                'form':form, 'instance':room, })

def proj_parts(request,pk):
    proj = Projekt.objects.get(pk=pk)
    rooms = Rooms.objects.filter(projekt=pk).order_by('r_number')
    walls = Walls.objects.filter(projekt=pk)
    wall_per_room = WallsRooms.objects.all()

    edycja_scian = request.POST.get("edycja_scian")
    usun = request.POST.get("usun_sciane")
    update_sciana = request.POST.get("update_sciana")
    
    if edycja_scian:
        ed_wall = Walls.objects.get(pk = edycja_scian)
        initial = {"wall_symbol":ed_wall,"wall_name":ed_wall.wall_name,
                   "wall_description":ed_wall.wall_description, "klasa":ed_wall.klasa,
                   "wall_u":ed_wall.wall_U,}
        form1 = WallsForm(initial=initial)
    else:
        form1 = WallsForm()

    if request.method == "POST":
        if usun:
            del_wall = Walls.objects.get(pk = usun)
            del_wall.delete()
            return redirect("proj_parts", proj.pk)
        elif update_sciana:
            form1 = WallsForm(request.POST)
            up_wall = Walls.objects.get(pk = update_sciana)
            if form1.is_valid():
                cld = form1.cleaned_data
                up_wall.wall_name = cld['wall_name']
                up_wall.wall_symbol = cld['wall_symbol']
                up_wall.wall_description = cld['wall_description']
                up_wall.wall_U = cld['wall_u']
                up_wall.klasa = cld['klasa']
                up_wall.projekt = proj
                up_wall.save()

                return redirect("proj_parts", proj.pk)


    if request.method == "POST" and not (edycja_scian or usun):
        form = WallsForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            new_wall = Walls(wall_name = cleaned_data['wall_name'],wall_symbol=cleaned_data['wall_symbol'],
                            wall_description=cleaned_data['wall_description'],wall_U=cleaned_data['wall_u'],
                            klasa=cleaned_data['klasa'])
            new_wall.projekt = proj
            new_wall.save()

            return redirect("proj_parts", proj.pk)
    else:
        form = WallsForm()


    return render(request, "proj-parts.html", {'proj':proj, 'rooms':rooms, 'walls':walls, 
                                            'form':form, 'form1': form1,"wall_per_room":wall_per_room,
                                            'edycja_scian':edycja_scian,'usun_sciane':usun, 'update_sciana':update_sciana,
                                            })

def proj_parts_ed(request,pk,rpk):
    proj = get_object_or_404(Projekt, pk = pk)
    room = get_object_or_404(Rooms, pk = rpk)
    walls = Walls.objects.filter(projekt=pk)
    wall_per_room = WallsRooms.objects.filter(room = rpk)

    form_wall = WallsRoomsForm()
    form1 = WallsRoomsForm()
    ed_sciany = request.POST.get("edycja_sciany")
    up_sciany = request.POST.get("up_sciany")
    del_sciany = request.POST.get("del_sciany")
    przypisz_sciane = request.POST.get("przypisz_sciane")
    up_wallroom = None

    if request.method == "POST" and ed_sciany:
        up_wallroom = WallsRooms.objects.get(pk = ed_sciany)
        initial = {"kierunek":up_wallroom.kierunek,"wall_area":up_wallroom.wall_area}
        form1 = WallsRoomsForm(initial=initial)

    if request.method == "POST":
        if up_sciany:
            form1 = WallsRoomsForm(request.POST)
            up_wallroom = WallsRooms.objects.get(pk = up_sciany)
            if form1.is_valid():
                cld = form1.cleaned_data
                up_wallroom.kierunek = cld['kierunek']
                up_wallroom.wall_area = cld['wall_area']
                up_wallroom.save()
                return redirect("proj_parts_ed", proj.pk, room.pk)
        elif del_sciany:
            del_wallroom = WallsRooms.objects.get(pk = del_sciany)
            del_wallroom.delete()
            return redirect("proj_parts_ed", proj.pk, room.pk)
        elif przypisz_sciane:
            form_wall = WallsRoomsForm(request.POST)
            wall_symbol = request.POST.get("symbol")
            selected_wall = Walls.objects.get(pk=wall_symbol)
            if form_wall.is_valid():
                cleaned_data = form_wall.cleaned_data
                joined_wall = WallsRooms(wall_area = cleaned_data['wall_area'],kierunek=cleaned_data['kierunek'])
                joined_wall.wall = selected_wall
                joined_wall.room = room
                joined_wall.save()
                return redirect("proj_parts_ed", proj.pk, room.pk)

    return render(request, "proj-parts-ed.html",{'proj':proj, 'room':room, 'walls':walls, 
                                                'form1':form1, 'form_wall':form_wall, 'wall_per_room':wall_per_room,
                                                'ed_sciany':ed_sciany,'up_wallroom':up_wallroom,'up_sciany':up_sciany, 
                                                'przypisz_sciane':przypisz_sciane, 'del_sciany': del_sciany,
                                                })

