from django.shortcuts import render
from draftapp.tasks import query_picks
from draftapp.utility import load_cache, getimagedict, getrankrequest, getpatchrequest, clean_pick_dictionary

MAX_DICTS = 100


def index(request):
    return render(request, "draftapp/index.html")


def draft(request, side):
    image_dic = getimagedict()
    try:
        if request.is_ajax() and request.method == "GET":
            if request.GET.get('table') == "ban":
                return load_bantable(request, side, image_dic)
            elif request.GET.get('table') == "pick":
                return load_picktable(request, side, image_dic)
        else:
            return default_load(request, side, image_dic)

    except KeyError:
        return render(request, "draftapp/draft.html", {'image_dic': image_dic, 'side': side})


def default_load(request, side, image_dic):
    ban_dict = load_cache()
    ban_list = list()
    if side == "blue":
        [ban_list.append(dictt) for dictt in ban_dict["blue"][0:MAX_DICTS]]
        context_dict = {'image_dic': image_dic, 'side': side, 'ban_list': ban_list}
    elif side == "red":
        [ban_list.append(dictt) for dictt in ban_dict["red"][0:MAX_DICTS]]
        context_dict = {'image_dic': image_dic, 'side': side, 'ban_list': ban_list}
    else:
        context_dict = {'image_dic': image_dic, 'side': side}
    return render(request, "draftapp/draft.html", context_dict)


def load_bantable(request, side, image_dic):
    rank = getrankrequest(request.GET.get('rank', None))
    patch = getpatchrequest(request.GET.get('patch', None))
    ban_list = list()
    if rank is not None and patch is not None:
        ban_dict = load_cache(rank, patch)
    else:
        ban_dict = load_cache()

    if side == "blue":
        [ban_list.append(dictt) for dictt in ban_dict["blue"][0:MAX_DICTS]]
        context_dict = {'image_dic': image_dic, 'side': side, 'ban_list': ban_list}
    elif side == "red":
        [ban_list.append(dictt) for dictt in ban_dict["red"][0:MAX_DICTS]]
        context_dict = {'image_dic': image_dic, 'side': side, 'ban_list': ban_list}
    else:
        context_dict = {'image_dic': image_dic, 'side': side}

    return render(request, "draftapp/bantable.html", context_dict)


def load_picktable(request, side, image_dic):
    # TODO - Add Rank and Patch Filtering to Queries
    # rank = getrankrequest(request.GET.get('rank', None))
    # patch = getpatchrequest(request.GET.get('patch', None))
    pick_str = request.GET.get('pick_dict', None)
    pick_dict = clean_pick_dictionary(pick_str)
    result = query_picks.apply_async(args=(side, pick_dict,), queue='loldraft')
    data_list = result.get()
    data_list = data_list[0:100]
    context_dict = {'image_dic': image_dic, 'side': side, 'pick_list': data_list}
    return render(request, "draftapp/picktable.html", context_dict)
